import unittest2 as unittest
from mock import MagicMock

class TestMemcachedStore(unittest.TestCase):

    def _makeOne(self,
                 servers='myhost:8080',
                 key_prefix='key.',
                 backend_api=None):
        from anykeystore.backends.memcached import MemcachedStore
        store = MemcachedStore(
            servers=servers, key_prefix=key_prefix, backend_api=backend_api)
        return store

    def _makeClient(self):
        client = MagicMock(spec=['get', 'set', 'delete'])
        return client

    def test_init_with_server_string(self):
        store = self._makeOne(servers='myhost:8080\n yourhost:6790')
        self.assertEqual(store.servers, ['myhost:8080', 'yourhost:6790'])

    def test_init_with_server_list(self):
        store = self._makeOne(servers=['myhost:8080', 'yourhost:6790'])
        self.assertEqual(store.servers, ['myhost:8080', 'yourhost:6790'])

    def test__get_conn(self):
        api = MagicMock(spec=['Client'])
        api.Client.return_value = 'myconn'

        store = self._makeOne(backend_api=api)
        conn = store._get_conn()

        self.assertEqual(conn, 'myconn')
        api.Client.assert_called_with(['myhost:8080'])

    def test_store(self):
        store = self._makeOne()
        client = self._makeClient()
        store._get_conn = MagicMock(return_value=client)

        store.store('foo', 'bar')

        client.set.assert_called_with('key.foo', 'bar', 0)

    def test_store_with_expires(self):
        store = self._makeOne()
        client = self._makeClient()
        store._get_conn = MagicMock(return_value=client)

        store.store('foo', 'bar', expires=5)

        client.set.assert_called_with('key.foo', 'bar', 5)

    def test_delete(self):
        store = self._makeOne()
        client = self._makeClient()
        store._get_conn = MagicMock(return_value=client)

        store.delete('foo')

        client.delete.assert_called_with('key.foo')

    def test_retrieve(self):
        store = self._makeOne()
        client = self._makeClient()
        client.get.return_value = 'bar'
        store._get_conn = MagicMock(return_value=client)

        result = store.retrieve('foo')

        self.assertEqual(result, 'bar')
        client.get.assert_called_with('key.foo')

    def test_retrieve_expired(self):
        store = self._makeOne()
        client = self._makeClient()
        client.get.return_value = None
        store._get_conn = MagicMock(return_value=client)
        self.assertRaises(KeyError, store.retrieve, 'foo')
        client.get.assert_called_with('key.foo')

    def test_purge(self):
        store = self._makeOne()
        store.purge_expired()
