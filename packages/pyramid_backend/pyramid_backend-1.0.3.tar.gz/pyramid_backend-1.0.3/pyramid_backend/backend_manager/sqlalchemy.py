from __future__ import absolute_import
__author__ = 'tarzan'

from collections import OrderedDict
from sqlalchemy import func
from pyramid.decorator import reify
import importlib
from . import Manager, _name_to_words

DBSession = None
""":type : sqlalchemy.orm.session.Session"""

def factory(config):
    """
    :type config: pyramid.config.Configurator
    """
    global DBSession
    settings = config.get_settings()
    dbsession_path = settings.get('pyramid_backend.sqlalchemy.dbsession')
    if not dbsession_path:
        return lambda m: None

    _module, _var = dbsession_path.rsplit('.', 1)
    _module = importlib.import_module(_module, package=None)
    DBSession = getattr(_module, _var)

    def _create_manager(model):
        return SQLAlchemyManager(model)

    return _create_manager

# def is_column(attr):
#     if not isinstance(attr, InstrumentedAttribute):
#         return False
#     p = attr.property
#     if not isinstance(p, ColumnProperty):
#         return False
#     return True
#
class SQLAlchemyManager(Manager):

    @reify
    def column_names(self):
        return [c.name for c in self.Model.__table__.columns]

    def column(self, col_name):
        return getattr(self.Model, col_name)

    @property
    def _foreignkey_names(self):
        return [rel.key for rel in self.Model.__mapper__.relationships]

    @property
    def __default_list__columns_to_display__(self):
        columns = OrderedDict(zip(self.column_names, [_name_to_words(n) for n in self.column_names]))
        columns[self.id_attr] = '#'
        return columns

    @property
    def __default_detail__columns_to_display__(self):
        columns = OrderedDict(zip(self.column_names, [_name_to_words(n) for n in self.column_names]))
        columns[self.id_attr] = '#'
        return columns

    @property
    def __default_detail__relations_to_display__(self):
        return OrderedDict(zip(self._foreignkey_names, [_name_to_words(n) for n in self._foreignkey_names]))


    def create(self, data):
        obj = self.Model()
        for k,v in data.items():
            setattr(obj, k, v)
        DBSession.add(obj)
        DBSession.flush()
        return obj

    def update(self, obj, data):
        for k,v in data.items():
            setattr(obj, k, v)
        DBSession.merge(obj)
        DBSession.flush()
        return obj

    def delete(self, obj):
        DBSession.delete(obj)
        DBSession.flush()

    def fetch_objects(self, filters, page=1):
        query = DBSession.query(self.Model)
        for name, value in filters.items():
            if name in self.column_names:
                query = query.filter(self.column(name).like("%%%s%%" % value))
        limit = self.list__items_per_page
        offset = (page-1)*limit
        id_col = self.column(self.id_attr)
        query = query.order_by(id_col.desc())
        query = query.offset(offset).limit(limit)
        return query

    def count_objects(self, filters):
        id_col = self.column(self.id_attr)
        query = DBSession.query(func.count(id_col))
        for name, value in filters.items():
            if name in self.column_names:
                query = query.filter(self.column(name).like("%%%s%%" % value))
        return query.scalar()

    def find_object(self, id_value):
        return DBSession.query(self.Model).filter(self.column(self.id_attr) == id_value).first()