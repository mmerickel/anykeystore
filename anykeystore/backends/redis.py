from __future__ import absolute_import

import redis

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
    """

    def __init__(self, db=0, host='localhost', port=6379,
                 key_prefix='anykeystore.'):
        self.host = host
        self.port = port
        self.db = db
        self.key_prefix = key_prefix or ''
        self.pool = redis.ConnectionPool(host=host, port=port, db=db)

    def _make_key(self, key):
        return '%s%s' % (self.key_prefix, key)

    def _get_conn(self):
        """The Redis connection, cached for this call"""
        return redis.Redis(connection_pool=self.pool)

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
