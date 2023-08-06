# Copyright (C) 2014 by Dr. Dieter Maurer <dieter@handshake.de>
"""`Delivery` related views."""
from decimal import Decimal

from zope.interface import Invalid, Interface, implements
from zope.schema import Int
from zope.component import adapts

from z3c.form.interfaces import ActionExecutionError
from z3c.form.field import Fields
from z3c.form.button import Buttons, ImageButton, handler, Handlers, \
     buttonAndHandler

from ..i18n import _
from ..delivery import ProviderDeliveries as DeliveriesCollection, \
     ClientsInDelivery

from .interfaces import ILayer
from .view import UdMixin, make_readonly_fields, \
     CrudEditSubForm, CrudEditForm
from .traversal import Proxy, CollectionProxy, Constant, Namespace


class Deliveries(CollectionProxy):
  obj = Constant(DeliveriesCollection())

class DeliveriesCrud(UdMixin): pass
  # likely, we want restrict deletion
  # def item_delete_check(self, item): return False


class Delivery(CollectionProxy): pass

class DeliveryCrud(UdMixin):
  def item_delete_check(self, item): return False




##############################################################################
## Provider delivery item

class Article(CollectionProxy):
  """actually a `ProviderDeliveryItem` inside a delivery as collection of the corresponding client delivery items."""

ProviderDeliveryItem = Article

class IChangeSchema(Interface):
  change = Int(title=_(u"Change"), description=_(u"Number of units to add/remove"), required=False)

class NoneAdapter(object):
  def __init__(*args): pass
  def __getattr__(self, k): return


class ProviderDeliveryItemEditSubForm(CrudEditSubForm):
  buttons = Buttons(
    ImageButton(u"dm_zope_reseller/assign.png", "assign", condition=lambda f: f.context.state==0),
    )

  handlers = Handlers()

  @handler(buttons["assign"])
  def handle_assign(self, action):
    self.context.assign()
    # as "assign" may remove an item, we reload the whole page
    r = self.request
    r.response.redirect(r["URL"])



class ProviderDeliveryItemEditForm(CrudEditForm):
  handlers = Handlers()

  @handler(CrudEditForm.buttons["apply"])
  def handle_apply(self, action):
    # iterate over the subforms and collect data, indexed by (client) delivery id
    errs = []; info = {}; sum = 0; action = False
    for f in self.subforms:
      f.update()
      d, e = f.extractData()
      if e: f.status = f.formErrorsMessage; errs.extend(e)
      else: 
        did = f.context.client_delivery_id
        di = info.get(did)
        if di is None: di = info[did] = dict(change=0, subforms=[])
        c = d.get("change")
        if c: di["change"] += c; sum += c; action = True
        di["subforms"].append(f)
    if errs: self.errors = errs; self.status = self.formErrorsMessage
    else:
      if sum:
        raise ActionExecutionError(
          Invalid(_(u"The sum of all changes must be 0"))
          )
      # iterate over the clients and perform the changes
      for di, i in info.iteritems():
        c = i["change"]
        if not c: continue
        try: i["subforms"][0].context.provider_delivery_item().change_client_delivery(di, c)
        except ValueError:
          raise ActionExecutionError(
            Invalid(_(u"Unit number for client ${client} becomes negative",
                      mapping=dict(client=f.context.client_title)
                      )
                    ))
      r = self.request
      r.response.redirect(r["URL"])


class ProviderDeliveryItemUd(UdMixin):
  url_pattern = None
  batch_size = 0
  def item_edit_check(self, item): return False

  EDIT_SUBFORM_FACTORY = ProviderDeliveryItemEditSubForm
  EDIT_FORM_FACTORY = ProviderDeliveryItemEditForm

  @property
  def crud_fields(self):
    cf = super(ProviderDeliveryItemUd, self).crud_fields
    return Fields(IChangeSchema) + make_readonly_fields(cf.select("units", "order_units", "order_max_units", "client_title", "article_order_no", "state"))


class ClientsUd(UdMixin):
  url_pattern = "++client++%s"

  def item_delete_check(*unused): return False
  item_edit_check = item_delete_check

  @property
  def crud_fields(self):
    return super(ClientsUd, self).crud_fields.select(
      "client_title", "proposed", "assigned", "confirmed",
      "delivery_date",
      )

  def __init__(self, *args):
    super(ClientsUd, self).__init__(*args)
    self.collection = self.context.obj.clients()

class Client(CollectionProxy):
  """Actually a client delivery."""


class ClientEditSubForm(CrudEditSubForm):
  buttons = Buttons(
    ImageButton(u"dm_zope_reseller/ok.png", "confirm", condition=lambda f: f.context.state==1),
    )

  handlers = Handlers()

  @handler(buttons["confirm"])
  def handle_confirm(self, action):
    self.context.confirm()
    # as "confirm" may remove an item, we reload the whole page
    r = self.request
    r.response.redirect(r["URL"])



class ClientEditForm(CrudEditForm):
  buttons = Buttons()
  handlers = Handlers()

  @buttonAndHandler(title=_(u"Deliver"), name="deliver",
                    condition=lambda f: f.context.obj.delivery_date is None
                    )
  def handle_deliver(self, action):
    self.context.obj.deliver()
    self.updateActions()

  def update(self):
    super(ClientEditForm, self).update()
    total_price = sum((f.context.total_price for f in self.subforms),
                      Decimal("0.00")
                      )
    self.bottom = """<b class="total-price">%s: %s EUR</b>""" % (
      self._crud().translate(_(u"Total price")), total_price
      )
                     

class ClientUd(UdMixin):
  url_pattern = None
  batch_size = 0

  def item_delete_check(*unused): return False
  item_edit_check = item_delete_check

  EDIT_SUBFORM_FACTORY = ClientEditSubForm
  EDIT_FORM_FACTORY = ClientEditForm

  @property
  def crud_fields(self):
    return make_readonly_fields(
      super(ClientUd, self).crud_fields.select(
        "article_title", "article_order_no", "state",
        "order_price", "order_units", "order_max_units",
        "units", "unit_price", "total_price",
        ))


class ClientNamespace(Namespace):
  adapts(Delivery, ILayer)

  NAME = "client"

  def OBJECT_FACTORY(self, id):
    return ClientsInDelivery(self.context.obj.id).get_item(id, KeyError)
