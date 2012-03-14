import logging

from anykeystore.compat import basestring
from anykeystore.interfaces import KeyValueStore
from anykeystore.utils import coerce_timedelta, splitlines


log = logging.getLogger(__name__)

class MemcachedStore(KeyValueStore):
    def __init__(self,
                 servers=('localhost:11211',),
                 key_prefix='anykeystore.',
                 backend_api=None):
        if isinstance(servers, basestring):
            servers = splitlines(servers)
        self.servers = servers
        self.key_prefix = key_prefix
        self.backend_api = backend_api

    @classmethod
    def backend_api(cls):
        try:
            import memcache
        except ImportError: # pragma: no cover
            # fall back for Google App Engine -- hasnt been tested though
            from google.appengine.api import memcache
        return memcache

    def _get_conn(self):
        """The Memcached connection, cached for this call"""
        return self.backend_api.Client(self.servers)

    def _make_key(self, key):
        return '%s%s' % (self.key_prefix, key)

    def retrieve(self, key):
        data = self._get_conn().get(self._make_key(key))
        if data:
            return data
        raise KeyError

    def store(self, key, value, expires=None):
        key = self._make_key(key)
        log.debug('Servers %s storing %s=%s' % (self.servers, key, value))

        expiration = None
        if expires is not None:
            expiration = coerce_timedelta(expires).seconds
        self._get_conn().set(key, value, expiration or 0)

    def delete(self, key):
        key = self._make_key(key)
        log.debug('Deleting %s', key)
        self._get_conn().delete(key)

    def purge_expired(self):
        pass

backend = MemcachedStore
