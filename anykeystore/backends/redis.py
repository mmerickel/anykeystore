from __future__ import absolute_import

from anykeystore.compat import pickle
from anykeystore.interfaces import KeyValueStore
from anykeystore.utils import coerce_timedelta


class RedisStore(KeyValueStore):
    """ Simple storage via Redis.

    :param db: The name of the redis database.
    :param host: Redis server host.
    :param port: Redis server port.
    :param key_prefix: Key prefix to avoid colliding with other parts of
                       the redis key/value store.
    :param backend_api: Specific redis implementation to use.
    """

    def __init__(self, db=0, host='localhost', port=6379,
                 key_prefix='anykeystore.', backend_api=None):
        self.host = host
        self.port = int(port)
        self.db = int(db)
        self.key_prefix = key_prefix or ''
        self.backend_api = backend_api

    @classmethod
    def backend_api(cls):
        return __import__('redis')

    def _make_key(self, key):
        return '%s%s' % (self.key_prefix, key)

    _pool = None
    def _get_conn(self):
        """The Redis connection, cached for this call"""
        api = self.backend_api
        if self._pool is None:
            self._pool = api.ConnectionPool(
                host=self.host, port=self.port, db=self.db)
        return api.Redis(connection_pool=self._pool)

    def retrieve(self, key):
        data = self._get_conn().get(self._make_key(key))
        if data:
            return pickle.loads(data)
        raise KeyError

    def store(self, key, value, expires=None):
        key = self._make_key(key)
        c = self._get_conn()
        c.set(key, pickle.dumps(value, protocol=pickle.HIGHEST_PROTOCOL))
        if expires is not None:
            expires = coerce_timedelta(expires)
            c.expire(key, expires.seconds)

    def delete(self, key):
        self._get_conn().delete(self._make_key(key))

    def purge_expired(self):
        pass

backend = RedisStore
