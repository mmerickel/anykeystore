import time

import unittest2 as unittest

def setUpModule():
    try: # pragma: no cover
        import sqlalchemy
    except ImportError: # pragma: no cover
        raise unittest.SkipTest('must install sqlalchemy to run sqla tests')

class TestSQLStore(unittest.TestCase):

    def _makeOne(self, url='sqlite://', **kw):
        from anykeystore.backends.sqla import SQLStore
        store = SQLStore(url, **kw)
        store.create()
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
        store.store('foo', 'bar', expires=-1)
        self.assertRaises(KeyError, store.retrieve, 'foo')

    def test_it_purge(self):
        store = self._makeOne()
        store.store('foo', 'bar', expires=0.01)
        time.sleep(0.05)
        store.purge_expired()
        self.assertRaises(KeyError, store.retrieve, 'foo')
