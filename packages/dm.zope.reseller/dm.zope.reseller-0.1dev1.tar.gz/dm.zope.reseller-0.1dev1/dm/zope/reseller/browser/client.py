# Copyright (C) 2014 by Dr. Dieter Maurer <dieter@handshake.de>
from plone.z3cform.crud.crud import NullForm

from ..client import Clients as ClientsCollection

from .view import CrudMixin, SearchMixin
from .traversal import CollectionProxy, Constant


class Clients(CollectionProxy):
  obj = Constant(ClientsCollection())


class ClientsCrud(CrudMixin):
  css_class = "client"


class ClientsSearch(SearchMixin):
  css_class = "client"


class Client(CollectionProxy): pass


class ClientCrud(CrudMixin):
  url_pattern = "++client_delivery++%s"
  add_fields = None
