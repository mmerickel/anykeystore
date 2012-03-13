import time

import unittest2 as unittest

def setUpModule():
    try: # pragma: no cover
        import pymongo
    except ImportError: # pragma: no cover
        raise unittest.SkipTest('must install pymongo to run mongodb tests')

class TestMongoStore(unittest.TestCase):

    def _makeOne(self):
        from anykeystore.backends.mongodb import MongoDBStore
        store = MongoDBStore(db='test', collection='test_store')
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
        time.sleep(0.1)
        store.purge_expired()
        self.assertRaises(KeyError, store.retrieve, 'foo')
