from datetime import datetime

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
    :param backend_api: Should be SQLAlchemy.
    """
    def __init__(self, url, **kw):
        self.url = url
        self.table = kw.pop('table', None)
        self.backend_api = api = kw.pop('backend_api')
        if not self.table:
            table_name = kw.pop('table_name', 'key_storage')
            meta = kw.pop('metadata', api.MetaData())
            self.table = self._make_table(table_name, meta)
        kw['url'] = url
        self.engine = api.engine_from_config(kw, prefix='')

    @classmethod
    def backend_api(cls):
        import sqlalchemy
        import sqlalchemy.exc
        return sqlalchemy

    def _make_table(self, name, meta):
        api = self.backend_api
        table = api.Table(name, meta,
            api.Column(
                'key', api.String(256), primary_key=True, nullable=False),
            api.Column('value', api.PickleType(), nullable=False),
            api.Column('expires', api.DateTime()),
        )
        return table

    def _create_table(self):
        self.table.create(checkfirst=True, bind=self.engine)
        self._created = True

    _created = False
    def _get_conn(self):
        if not self._created:
            self._create_table()
        return self.engine.connect()

    def retrieve(self, key):
        c = self._get_conn()
        api = self.backend_api
        try:
            data = c.execute(api.select(
                [self.table.c.value, self.table.c.expires],
                self.table.c.key == key)).fetchone()
            if data:
                value, expires = data
                if expires is None or datetime.utcnow() < expires:
                    return value
        finally:
            c.close()
        raise KeyError

    def _insert_or_replace(self, c, key, value, expires):
        try:
            c.execute(
                self.table.insert(), key=key, value=value, expires=expires)
        except self.backend_api.exc.IntegrityError:
            c.execute(
                self.table.update(), key=key, value=value, expires=expires)

    def store(self, key, value, expires=None):
        expiration = None
        if expires is not None:
            expiration = datetime.utcnow() + coerce_timedelta(expires)
        c = self._get_conn()
        try:
            self._insert_or_replace(c, key, value, expiration)
        finally:
            c.close()

    def delete(self, key):
        c = self._get_conn()
        api = self.backend_api
        try:
            c.execute(api.delete(self.table, self.table.c.key == key))
        finally:
            c.close()

    def purge_expired(self):
        c = self._get_conn()
        api = self.backend_api
        try:
            c.execute(
                api.delete(
                    self.table, self.table.c.expires < datetime.utcnow()))
        finally:
            c.close()

backend = SQLStore
