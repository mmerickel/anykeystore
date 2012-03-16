import unittest2 as unittest
from mock import MagicMock, patch

class TestRedisStore(unittest.TestCase):

    def _makeOne(self,
                 db=0,
                 key_prefix='key.',
                 host='localhost',
                 port=6379,
                 backend_api=None):
        from anykeystore.backends.redis import RedisStore
        store = RedisStore(db=db, key_prefix=key_prefix, host=host, port=port,
                           backend_api=backend_api)
        return store

    def _makeConnection(self):
        conn = MagicMock(spec=['get', 'set', 'delete', 'expire'])
        return conn

    def test__get_conn(self):
        api = MagicMock(spec=['Redis', 'ConnectionPool'])
        api.ConnectionPool.return_value = 'foo'
        api.Redis.return_value = 'myconn'

        store = self._makeOne(backend_api=api)
        conn = store._get_conn()
        self.assertEqual(conn, 'myconn')

        conn = store._get_conn()
        self.assertEqual(conn, 'myconn')

        api.Redis.assert_called_with(connection_pool='foo')
        self.assertEqual(api.ConnectionPool.call_count, 1)

    def test_store(self):
        store = self._makeOne()
        conn = self._makeConnection()
        store._get_conn = MagicMock(return_value=conn)

        with patch('anykeystore.backends.redis.pickle') as pickle:
            pickle.dumps = lambda value, protocol: value
            store.store('foo', 'bar')

        conn.set.assert_called_with('key.foo', 'bar')
        self.assertFalse(conn.expire.called)

    def test_store_with_expires(self):
        store = self._makeOne()
        conn = self._makeConnection()
        store._get_conn = MagicMock(return_value=conn)

        with patch('anykeystore.backends.redis.pickle') as pickle:
            pickle.dumps = lambda value, protocol: value
            store.store('foo', 'bar', expires=5)

        conn.set.assert_called_with('key.foo', 'bar')
        conn.expire.assert_called_with('key.foo', 5)

    def test_delete(self):
        store = self._makeOne()
        conn = self._makeConnection()
        store._get_conn = MagicMock(return_value=conn)

        store.delete('foo')

        conn.delete.assert_called_with('key.foo')

    def test_retrieve(self):
        store = self._makeOne()
        conn = self._makeConnection()
        conn.get.return_value = 'bar'
        store._get_conn = MagicMock(return_value=conn)

        with patch('anykeystore.backends.redis.pickle') as pickle:
            pickle.loads = lambda value: value
            result = store.retrieve('foo')

        self.assertEqual(result, 'bar')
        conn.get.assert_called_with('key.foo')

    def test_retrieve_expired(self):
        store = self._makeOne()
        conn = self._makeConnection()
        conn.get.return_value = None
        store._get_conn = MagicMock(return_value=conn)

        self.assertRaises(KeyError, store.retrieve, 'foo')

        conn.get.assert_called_with('key.foo')

    def test_purge(self):
        store = self._makeOne()
        store.purge_expired()
