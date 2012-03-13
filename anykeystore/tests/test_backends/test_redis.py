import time

import unittest2 as unittest

def setUpModule():
    try: # pragma: no cover
        import redis
    except ImportError: # pragma: no cover
        raise unittest.SkipTest('must install redis to run redis tests')

class TestRedisStore(unittest.TestCase):

    def _makeOne(self):
        from anykeystore.backends.redis import RedisStore
        store = RedisStore()
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
        store.store('foo', 'bar', expires=0)
        self.assertRaises(KeyError, store.retrieve, 'foo')

    def test_it_purge(self):
        store = self._makeOne()
        store.store('foo', 'bar', expires=0.01)
        time.sleep(0.1)
        store.purge_expired()
        self.assertRaises(KeyError, store.retrieve, 'foo')
