import time

import unittest2 as unittest

class TestMemoryStore(unittest.TestCase):

    def _makeOne(self):
        from anykeystore.backends.memory import MemoryStore
        return MemoryStore()

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
        time.sleep(0.02)
        store.purge_expired()
        self.assertRaises(KeyError, store.retrieve, 'foo')
