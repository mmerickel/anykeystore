from datetime import datetime

from sqlalchemy import engine_from_config
from sqlalchemy import Column, MetaData
from sqlalchemy import String, PickleType, DateTime, Table
from sqlalchemy.sql import select, delete

from anykeystore.interfaces import KeyValueStore
from anykeystore.utils import coerce_timedelta


class SQLStore(KeyValueStore):
    """ Simple storage via SQLAlchemy.

    The store will automatically create a table object if one is not
    supplied. The automatically generated table is shown below. If a
    table is supplied directly, it must support the required columns
    `key`, `value`, and `expires`.

    .. code-block:: python

        table = Table(table_name, metadata,
            Column('key', String(200), primary_key=True, nullable=False),
            Column('value', Text(), nullable=False),
            Column('expires', DateTime()),
        )

    :param engine: A SQLAlchemy engine.
    :param table: Optional. The SQLAlchemy Table instance to be used for
                  storage. If this isn't supplied, a table is generated
                  automatically.
    :type table: sqlalchemy.Table
    :param table_name: Optional. The name of the table.
    :param metadata: Optional. The SQLAlchemy MetaData instance to hook the
                 generated table into.
    :type metadata: sqlalchemy.MetaData
    """
    def __init__(self, url, **kw):
        self.url = url
        self.table = kw.pop('table', None)
        if not self.table:
            table_name = kw.pop('table_name', 'key_storage')
            meta = kw.pop('metadata', MetaData())
            self.table = Table(table_name, meta,
                Column('key', String(256), primary_key=True, nullable=False),
                Column('value', PickleType(), nullable=False),
                Column('expires', DateTime()),
            )
        kw['url'] = url
        self.engine = engine_from_config(kw, prefix='')

    def create(self):
        self.table.create(checkfirst=True, bind=self.engine)

    def retrieve(self, key):
        c = self.engine.connect()
        try:
            data = c.execute(select(
                [self.table.c.value, self.table.c.expires],
                self.table.c.key == key)).fetchone()
            if data:
                value, expires = data
                if expires is None or datetime.utcnow() < expires:
                    return value
        finally:
            c.close()
        raise KeyError

    def store(self, key, value, expires=None):
        expiration = None
        if expires is not None:
            expiration = datetime.utcnow() + coerce_timedelta(expires)
        c = self.engine.connect()
        try:
            c.execute(
                self.table.insert(), key=key, value=value, expires=expiration)
        finally:
            c.close()

    def delete(self, key):
        c = self.engine.connect()
        try:
            c.execute(delete(self.table, self.table.c.key == key))
        finally:
            c.close()

    def purge_expired(self):
        c = self.engine.connect()
        try:
            c.execute(
                delete(self.table, self.table.c.expires < datetime.utcnow()))
        finally:
            c.close()

backend = SQLStore
