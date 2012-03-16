import unittest2 as unittest

class TestSQLStore(unittest.TestCase):

    def _makeOne(self, url='sqlite://', **kw):
        from anykeystore.backends.sqla import SQLStore
        store = SQLStore(url, **kw)
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
        store.purge_expired()
        self.assertRaises(KeyError, store.retrieve, 'foo')
