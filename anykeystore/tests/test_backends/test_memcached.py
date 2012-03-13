import time

import unittest2 as unittest

def setUpModule():
    try: # pragma: no cover
        import memcache
    except ImportError: # pragma: no cover
        raise unittest.SkipTest(
            'must install python-memcached to run memcached tests')

class TestRedisStore(unittest.TestCase):

    def _makeOne(self):
        from anykeystore.backends.memcached import MemcachedStore
        store = MemcachedStore(key_prefix='test_anykey.')
        return store

    def test_it(self):
        store = self._makeOne()
        store.store('foo', 'bar')
        value = store.retrieve('foo')
        self.assertEqual(value, 'bar')

    def test_it_delete(self):
        store = self._makeOne()
        store.store('foo', 'bar')
        store.delete('foo')
        self.assertRaises(KeyError, store.retrieve, 'foo')

    def test_it_old(self):
        store = self._makeOne()
        store.store('foo', 'bar', expires=1)
        time.sleep(1.01)
        self.assertRaises(KeyError, store.retrieve, 'foo')

    def test_it_purge(self):
        store = self._makeOne()
        store.store('foo', 'bar', expires=1)
        time.sleep(1.01)
        store.purge_expired()
        self.assertRaises(KeyError, store.retrieve, 'foo')
