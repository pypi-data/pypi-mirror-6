# Copyright (C) 2014 by Dr. Dieter Maurer <dieter@handshake.de>
from ..article import Articles as ArticlesCollection

from .view import CrudMixin, SearchMixin
from .traversal import CollectionProxy, Constant


class Articles(CollectionProxy):
  obj = Constant(ArticlesCollection())


class ArticlesCrud(CrudMixin):
  url_pattern = None

class ArticlesSearch(SearchMixin):
  url_pattern = None
  search_field_names = "title", "provider_order_no"

