# Copyright (C) 2014 by Dr. Dieter Maurer <dieter@handshake.de>
"""`Order` related views."""
from datetime import datetime

from zope.interface import Invalid, Interface, implements
from zope.component import adapts
from zope.schema import Bool, Choice, Bytes, Int, TextLine, Decimal

from z3c.form.interfaces import WidgetActionExecutionError
from z3c.form.field import Fields
from z3c.form.form import Form
from z3c.form.button import buttonAndHandler, Buttons, handler, ImageButton

from Products.statusmessages.interfaces import IStatusMessage

from ..i18n import _
from ..lib import mk_vocabulary, overridable_property
from ..article import unit_price
from ..order import Orders as OrdersCollection, ClientsInOrder
from ..interfaces import IProviderOrderItem, IArticle

from .interfaces import ILayer
from .view import CrudMixin, SearchMixin, CrudAddForm, CrudEditSubForm, \
     ViewBase, UdMixin, \
     ChildForm, IWrappedForm, \
     make_readonly_fields
from .traversal import Proxy, CollectionProxy, Constant, Namespace

class Orders(CollectionProxy):
  obj = Constant(OrdersCollection())

class OrdersCrud(CrudMixin):
  def item_edit_check(self, item): return item.open()


class Order(CollectionProxy):
  def open(self): return self.obj.open()
  def has_delivery(self): return self.obj.get_delivery() is not None
  def delivery_addable(self): return not self.open() and not self.has_delivery()


class OrderAddForm(CrudAddForm):
  def createAndAdd(self, data):
    collection = self._crud().context.obj
    order_no = data.pop("provider_order_no", "").strip()
    # determine article id
    from ..article import Articles
    articles = Articles()
    a = articles.list((("provider_order_no", order_no),))
    if not a:
      raise WidgetActionExecutionError(
        "provider_order_no",
        Invalid(_(u"Article does not exist"))
        )
    assert len(a) == 1
    aid = a[0].id
    # see if we already have a corresponding item
    if collection.list((("article_id", aid),)):
      raise WidgetActionExecutionError(
        "provider_order_no",
        Invalid(_("We already have an order item for this article"))
        )
    data.update(dict(
      order_id=collection.id,
      article_id=aid,
      catalog_price=a[0].catalog_price,
      ))
    return super(OrderAddForm, self).createAndAdd(data)
      


class OrderCrud(CrudMixin):
  ADD_FORM_FACTORY = OrderAddForm

  @overridable_property
  def add_fields(self):
    if self.context.open(): return Fields(
    IArticle["provider_order_no"],
    IProviderOrderItem["packages"],
    )


  __cf = None
  @overridable_property
  def crud_fields(self):
    cf = self.__cf
    if cf is None:
      cf = super(OrderCrud, self).crud_fields
      if not self.context.open():
        cf = make_readonly_fields(cf)
      self.__cf = cf
    return cf

  def item_edit_check(self, item): return item.open()
  def item_delete_check(self, item): return item.deletable()

  def order(self):
    self.context.obj.order()
    return self._render()

  def adjust(self):
    self.context.obj.adjust_order_items()
    return self._render()

  def to_delivery(self):
    r = self.request
    return r.response.redirect(
      "%s/deliveries/++child++%s"
      % (r["URL3"], self.context.obj.get_delivery().id)
      )

  def add_delivery(self):
    self.context.obj.add_delivery()
    return self.to_delivery()

  def _render(self):
    # fix the urls and "base"
    r = self.request; R = r.response
    r._steps[-1] = "crud"; r._resetURLS()
    R.setBase(r["URL1"] + "/")
    return self()

  def export(self):
    """Export the catalog tailored for this order."""
    # build a dict indexed by article id of our order items
    order = self.context.obj
    items = dict((i.article_id, i) for i in order.list())
    # prepare csv
    from StringIO import StringIO
    from csv import writer
    output = StringIO()
    def conv(s):
      if isinstance(s, unicode): s = s.encode("utf-8")
      elif s is None: s = ""
      else: s = str(s)
      return s
    write = lambda r, writerow=writer(output).writerow : writerow([conv(s) for s in r])
    header = (_(u"Article"), _(u"Description"), _(u"Order#"), _(u"Unit"), _(u"Price"), _(u"P-Size"), "", _(u"Available units"), "", _(u"Order units: wish"),  _(u"max"))
    header = map(self.translate, header)
    write((self.translate(self.context.title),)) # maybe more information
    # iterate over the articles and write a row for each
    from ..article import Articles
    for i, a in enumerate(Articles().list()):
      if not i % 40:
        write(())
        write(12 * ("***********",))
        write(header); 
        write(12 * ("***********",))
      info = [a.title, a.description, a.provider_order_no, a.unit,]
      #       c-price    p-price            u-price        with tax
      price = unit_price(a)
      info.extend([price, a.package_size, "",])
      # determine the available units
      item = items.get(a.id)
      if item is None:
        # we might want to look at the stock
        available = 0
      else:
        pno, perfect = item.optimal()
        if not perfect: pno += 1 # we cheat a bit
        available = item.package_size * pno + item.stock_units - item.client_order_units
      info.extend([available, "", "", ""])
      write(info)
    # now deliver the csv
    output.seek(0)
    r = self.request.response
    r.setHeader("Content-Type", "text/csv; charset=UTF-8")
    r.setBody(output.read())
    r.setHeader("Content-Disposition",
                "attachment; filename=\"%s.csv\""
                % order.title.replace("/", "-").replace(" ", "_")
                )


class OrderClients(UdMixin):
  title = _(u"Clients")

  def __init__(self, *args):
    super(OrderClients, self).__init__(*args)
    self.collection = ClientsInOrder(self.context.obj.id)

  url_pattern = "++client++%s"

  def item_delete_check(self, unused): return False


class ClientNamespace(Namespace):
  adapts(Order, ILayer)

  NAME = "client"

  def OBJECT_FACTORY(self, id):
    return ClientsInOrder(self.context.obj.id).get_item(id, KeyError)


class Client(Proxy):
  browser_default = "assigned",

  def has_unassigned_order_items(self):
    return len(self.obj.unassigned_order_items().list()) > 0

  # may want to handle this with acquisition
  def open(self): return self.__parent__.open()
  def has_delivery(self): return self.__parent__.has_delivery()
  def delivery_addable(self): return self.__parent__.delivery_addable()


##############################################################################
## Client order items

class IOrderItemsAddSchema(Interface):
  provider_order_no = TextLine(title=_(u"Order#"), description=_(u"Order number"), required=False)
  article_title = TextLine(title=_(u"Article"), required=False)
  units = Int(title=_(u"Units"), min=0)
  max_units = Int(title=_(u"Max units"), min=0, required=False)
  note = TextLine(title=_(u"Note"), required=False)
  unit_price = Decimal(title=_(u"Price per unit"), required=False)
  


class IOrderItemsImportSchema(Interface):
  include_unassigned = Bool(
    title=_(u"Include unassigned items"),
    description=_("Whether unassigned items should be first imported (they are always `added`."),
    default=True,
    )
  bytes = Bytes(
    title=_(u"Csv import file"),
    description=_(u"The csv file containing the order items to be imported"),
    required=False,
    )
  mode = Choice(
    title=_(u"Mode"),
    description=_(u"""How the new order items interact with existing ones: `update` (the `unit` and `max` fields of a new item overrides that of a corresponding existing one); `replace` (all existing order items are deleted before the import); `add` (the values of `unit` and `max` of new items are added to those of corresponding existing ones)."""),
    vocabulary=mk_vocabulary(("update", _(u"update")),
                             ("replace", _(u"replace")),
                             ("add", _(u"add")),
                             ),
    default="update",
    )


class OrderItemsAddForm(CrudAddForm):
  def createAndAdd(self, data):
    self._crud().create_or_update(data)
    self.ignoreRequest = True
    self.content.reload()
    self.updateWidgets()


class _ClientOrderItems(CrudMixin):
  # to be defined by derived classes
  type = None

  add_fields = Fields(IOrderItemsAddSchema)
  ADD_FORM_FACTORY = OrderItemsAddForm

  @overridable_property
  def title(self):
    t = self.translate
    return t(self.context.obj.title) + u": " + t(self.type)

  def __init__(self, *args):
    super(_ClientOrderItems, self).__init__(*args)
    self.collection = \
         getattr(self.context.obj, str(self.type).replace(" ","_"))()
    order = self.order = self.context.__parent__.obj
    if order.open(): self.add_fields = Fields(IOrderItemsAddSchema)
    else:
      self.add_fields = None
      self.crud_fields = make_readonly_fields(self.crud_fields)
      self.import_fields = None

  def update(self):
    subforms = self.get_subforms()
    if self.import_fields:
      subforms.append(self.IMPORT_FORM_FACTORY(self.context, self.request, self))
    super(_ClientOrderItems, self).update()

  def create_or_update(self, data, mode=None):
    add_msg = IStatusMessage(self.request).addStatusMessage
    def add_message(msg, info=None, type="warning"):
      msg = self.translate(msg)
      if mode is not None and info:
        msg += u"[" + self.translate(info) + u"]"
      add_msg(msg, type=type)
    def handle_error(field, msg, info=None):
      if mode is None: # from add form
        raise WidgetActionExecutionError(field, Invalid(msg))
      else: add_message(msg, info, "error") # from import
    pon = data["provider_order_no"]
    at = data["article_title"]
    if pon is None and at is None:
      return handle_error(
        "provider_order_no",
        _(u"You must specify either the Order# (prefered) or the article"),
        _(u"Item# ${item_no}", mapping=data) if "item_no" in data else None
        )
    from ..article import Articles
    articles = Articles()
    if pon is not None:
      a = articles.list((("provider_order_no", pon),))
      if not a: return handle_error(
        "provider_order_no",
        _(u"Article does not exist"),
        _(u"Order# ${provider_order_no}", mapping=data)
        )
    else: # `at` is not None
      a = articles.list((("title", at),))
      if not a: return handle_error(
        "article",
        _(u"Article does not exist"),
        at
        )
      if len(a) >= 2: return handle_error(
        "article",
        _(u"There are several matching articles (please use Order# instead)"),
        at
        )
    a = a[0]
    if at and a.title != at:
      add_message(
        _(u"Article title does not correspond (ignored)"),
        _(u"Item# ${item_no}, specified title ${stitle}, catalog title ${ctitle}, order# ${order_no}",
          mapping=dict(item_no=data.get("item_no"), order_no=a.provider_order_no, stitle=at, ctitle=a.title)
          )
        )
    oi = self.collection.list((("a.provider_order_no", a.provider_order_no),))
    oi = oi and oi[0] or None
    if oi and mode is None:
      return handle_error(
        "provider_order_no",
        _(u"There is already a correspinding order item. Please edit this one rather than add a new item with order# ${provider_order_no}",
          mapping=a
          )
        )
    aup = unit_price(a)
    up = data.get("unit_price") or aup
    if up is not None and up != aup:
      add_message(
        _(u"Specified price differs from catalog price"),
        _(u"Item# ${item_no}, order# ${order_no}, specified price ${sprice}, catalog price ${cprice}",
          mapping=dict(item_no=data.get("item_no"), order_no=a.provider_order_no, 
                       sprice=up, cprice=aup,
                       )
          )
        )
    units = data["units"]
    if units is None or units < 0:
      handle_error(
        "units",
        _(u"Invalid units specification (must be >= 0)"),
        _(u"Item# ${item_no}, order# ${order_no}, units ${units}",
          mapping=dict(data)
          ),
        )
      return
    max_units = data.get("max_units")
    if max_units is not None and max_units < units:
      handle_error(
        "max_units",
        _(u"max_units smaller than `units`"),
        _(u"Item# ${item_no}, order# ${order_no}, max_units ${max_units}, units ${units}",
          mapping=data
          )
        )
      max_units = None
    oi_data = dict(
      units=units, max_units=max_units,
      article_id=a.id, client_id=self.context.obj.id,
      unit_price=up,
      order_date=datetime.now(),
      )
    from ..client import ClientOrderItems
    collection = ClientOrderItems()
    if oi is None: oid = collection.add_item(oi_data)
    else:
      oid = oi_data["id"] = oi.id
      if mode == "add":
        for f in ("units", "max_units",):
          if oi_data[f] is None and oi[f] is None: continue
          oi_data[f] = coalesce(oi_data[f], oi_data["units"]) \
                       + coalesce(oi[f], oi["units"])
      collection.update_item(oi_data)
    if self.assign: self.order.add_client_order_item(oid)
    return oid


class OrderItemsImportForm(ChildForm, Form):
  implements(IWrappedForm)

  ignoreContext = True

  def __init__(self, *args):
    super(OrderItemsImportForm, self).__init__(*args)
    self.fields = self._crud().import_fields

  @buttonAndHandler(title=_(u"Import"), name="import")
  def handle_import(self, action):
    data, errors = self.extractData()
    if errors: self.status = self.formErrorsMessage; return
    self.ignoreRequest = True
    self.updateWidgets()
    self._import(data)

  def _import(self, data):
    from csv import reader
    from decimal import Decimal
    from StringIO import StringIO
    add_msg = IStatusMessage(self.request).addStatusMessage
    def add_message(msg, info=None, type="warning"):
      msg = self.translate(msg)
      if mode is not None and info:
        msg += u"[" + self.translate(info) + u"]"
      add_msg(msg, type=type)
    create_or_update = self._crud().create_or_update
    if data.get("include_unassigend"):
      for ucoi in self._crud().context.obj.unassigned_order_items.list():
        create_or_update(ucoi, "add")
    if data.get("bytes") is None: return
    def intify(d, f):
      v = d[f].strip()
      if not v: v = None
      elif v == "x": v = 1
      else:
        try: v =  int(v)
        except:
          d["field"] = f; d["value"] = v
          add_message(
            _(u"Bad integer value (ignored)"),
            _(u"Item# ${item_no}, order# ${order_no}, field ${field}, value ${value}",
              mapping=data,
              )
            )
          v = None
      d[f] = v
    def priceify(d, f):
      v = d[f].strip()
      if not v: v = None
      else:
        try: v = Decimal(v.replace(",", "."))
        except:
          add_message(
            _(u"Bad price value (ignored)"),
            _(u"Item# ${item_no}, order# ${order_no}, value ${unit_price}",
              mapping=data,
              )
            )
          v = None
      d[f] = v
    r = reader(StringIO(data["bytes"])); mode = data["mode"]
    oids = set(); item_no = 0
    state = -2 # skip first 2 lines
    for l in r:
      if state < 0: state += 1; continue # skip
      if not l[0]: continue # skip lines without title
      if l[0].startswith("***"):
        # header found - skip it
        state = -2
        continue
      l = [unicode(f, "utf-8") for f in l]
      item_no += 1
      d = dict(
        article_title=l[0],
        provider_order_no=l[2],
        unit_price=l[4],
        units=l[9],
        max_units=l[10],
        item_no=item_no,
        )
      for f in d.keys():
        if not f.endswith("units"): continue
        intify(d, f)
      priceify(d, "unit_price")
      if d["units"]:
        oid = create_or_update(d, mode)
        if oid is not None: oids.add(oid)
    if mode == "replace":
      # deactivate items we have not seen
      for o in self._crud().collection.list():
        if o.id not in oids: o.deactivate()



  def _crud(self): return self.__parent__


class ClientAssignedOrderItems(_ClientOrderItems):
  type = _("assigned_order_items")

  _af = None
  @overridable_property
  def import_fields(self):
    af = self._af
    if af is None:
      af = Fields(IOrderItemsImportSchema)
      if not self.context.has_unassigned_order_items():
        af = af.omit("include_unassigned")
      self._af = af
    return af

  assign = True
  IMPORT_FORM_FACTORY = OrderItemsImportForm


class ClientUnassignedOrderItems(_ClientOrderItems):
  type = _("unassigned_order_items")

  import_fields = None # for the moment
  assign = False



##############################################################################
## Provider order item

class Article(CollectionProxy):
  """actually a `ProviderOrderItem` inside an order as collection of the corresponding client order items."""

  # may want to handle this with acquisition
  def open(self): return self.__parent__.open()
  def has_delivery(self): return self.__parent__.has_delivery()
  def delivery_addable(self): return self.__parent__.delivery_addable()


class ArticleEditSubForm(CrudEditSubForm):
  buttons = Buttons(
    CrudEditSubForm.buttons.select("edit"),
    ImageButton(u"dm_zope_reseller/reopen.png", "reopen",
                condition=lambda form: form._crud().context.open()
                )
    )

  handlers = CrudEditSubForm.handlers.copy()

  @handler(buttons["reopen"])
  def handle_reopen(self, action):
    coi = self._crud().context # proxy
    o = coi.__parent__.obj
    o.reopen_client_order_item(coi.obj.id)
    r = self.request
    r.response.redirect(r["URL"])
    
class ArticleUd(UdMixin):
  url_pattern = None
  add_fields = None

  EDIT_SUBFORM_FACTORY = ArticleEditSubForm

  @overridable_property
  def crud_fields(self):
    cf = super(ArticleUd, self).crud_fields.select(
      "article_title", "provider_order_no",
      "client_title", "units", "max_units", "order_date",
      )
    if not self.context.open(): cf = make_readonly_fields(cf)
    return cf


def coalesce(*args):
  """return first argument which is not `None`."""
  for a in args:
    if a is not None: return a
