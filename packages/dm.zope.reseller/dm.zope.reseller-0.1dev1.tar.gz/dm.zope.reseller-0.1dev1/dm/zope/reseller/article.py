# Copyright (C) 2014 by Dr. Dieter Maurer <dieter@handshake.de>
"""Article management."""
from decimal import Decimal, ROUND_UP

from zope.interface import implements

from .db import Db, Table, ObjectBase
from .interfaces import IArticleSchema, IArticle


class Article(ObjectBase):
  implements(IArticleSchema)

  _SCHEMA_ = IArticleSchema


class Articles(Table):
  _TABLE_ = "reseller.article"
  _FACTORY_ = Article
  _ORDER_ = "title"



TAX = None
cent = Decimal('0.01')
def unit_price(article):
  global TAX
  if TAX is None:
    c = Db().cursor()
    c.execute("select code, percent from reseller.tax")
    TAX = dict((code, Decimal("1.00") + percent / Decimal(100)) for (code, percent) in c.fetchall())
  a = article
  price = a.catalog_price * a.price_ratio / a.package_size * TAX[a.tax_code]
  return price.quantize(cent, rounding=ROUND_UP)
