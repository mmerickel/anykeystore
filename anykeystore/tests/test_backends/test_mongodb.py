from datetime import datetime, timedelta

import unittest2 as unittest
from mock import MagicMock, patch

class TestMongoStore(unittest.TestCase):

    def _makeOne(self,
                 db='testdb',
                 collection='keystore',
                 host='localhost',
                 port=8080,
                 backend_api=None):
        from anykeystore.backends.mongodb import MongoDBStore
        store = MongoDBStore(db=db, collection=collection, host=host,
                             port=port, backend_api=backend_api)
        return store

    def _makeConnection(self):
        conn = MagicMock(spec=[
            'create_collection', 'collection_names', '__getitem__'])
        return conn

    def test__get_conn(self):
        conn = self._makeConnection()
        conn.collection_names.return_value = ['keystore']

        db_conn = MagicMock()
        db_conn.__getitem__.return_value = conn

        api = MagicMock(spec=['Connection', 'binary'])
        api.Connection.return_value = db_conn

        store = self._makeOne(backend_api=api)
        result = store._get_conn()

        self.assertEqual(result, conn)
        api.Connection.assert_called_with('localhost', 8080, slave_okay=False)
        self.assertFalse(conn.create_collection.called)

    def test__get_conn_and_create_collection(self):
        conn = self._makeConnection()
        conn.collection_names.return_value = []

        db_conn = MagicMock()
        db_conn.__getitem__.return_value = conn

        api = MagicMock(spec=['Connection', 'binary'])
        api.Connection.return_value = db_conn

        store = self._makeOne(backend_api=api)
        result = store._get_conn()

        self.assertEqual(result, conn)
        api.Connection.assert_called_with('localhost', 8080, slave_okay=False)
        self.assertTrue(conn.create_collection.called)

    def test_store(self):
        api = MagicMock(spec=['Connection', 'binary'])
        store = self._makeOne(backend_api=api)
        collection = MagicMock(spec=['update', 'remove', 'find_one'])
        conn = self._makeConnection()
        conn.__getitem__.return_value = collection
        store._get_conn = MagicMock(return_value=conn)

        store.store('foo', 'bar')

        conn.__getitem__.assert_called_with('keystore')
        args = collection.update.call_args[0]
        self.assertEqual(args[0], {'key': 'foo'})
        self.assertEqual(args[1]['$set']['expires'], None)

    def test_store_with_expires(self):
        api = MagicMock(spec=['Connection', 'binary'])
        store = self._makeOne(backend_api=api)
        collection = MagicMock(spec=['update', 'remove', 'find_one'])
        conn = self._makeConnection()
        conn.__getitem__.return_value = collection
        store._get_conn = MagicMock(return_value=conn)

        now = datetime.utcnow()
        with patch('anykeystore.backends.mongodb.datetime') as dt:
            dt.utcnow.return_value = now
            store.store('foo', 'bar', expires=5)

        conn.__getitem__.assert_called_with('keystore')
        args = collection.update.call_args[0]
        self.assertEqual(args[0], {'key': 'foo'})
        self.assertEqual(args[1]['$set']['expires'],
                         now + timedelta(seconds=5))

    def test_delete(self):
        store = self._makeOne()
        collection = MagicMock(spec=['update', 'remove', 'find_one'])
        conn = self._makeConnection()
        conn.__getitem__.return_value = collection
        store._get_conn = MagicMock(return_value=conn)

        store.delete('foo')

        conn.__getitem__.assert_called_with('keystore')
        args = collection.remove.call_args[0]
        self.assertEqual(args[0], {'key': 'foo'})

    def test_retrieve(self):
        store = self._makeOne()
        collection = MagicMock(spec=['update', 'remove', 'find_one'])
        conn = self._makeConnection()
        conn.__getitem__.return_value = collection
        store._get_conn = MagicMock(return_value=conn)
        collection.find_one.return_value = {'expires': None, 'value': 'bar'}

        with patch('anykeystore.backends.mongodb.pickle') as pickle:
            pickle.loads = lambda value: value
            result = store.retrieve('foo')

        self.assertEqual(result, 'bar')
        conn.__getitem__.assert_called_with('keystore')
        args = collection.find_one.call_args[0]
        self.assertEqual(args[0], {'key': 'foo'})

    def test_retrieve_expired(self):
        store = self._makeOne()
        collection = MagicMock(spec=['update', 'remove', 'find_one'])
        conn = self._makeConnection()
        conn.__getitem__.return_value = collection
        store._get_conn = MagicMock(return_value=conn)

        old = datetime.utcnow() - timedelta(seconds=1)
        collection.find_one.return_value = {'expires': old, 'value': 'bar'}

        self.assertRaises(KeyError, store.retrieve, 'foo')

        conn.__getitem__.assert_called_with('keystore')
        args = collection.find_one.call_args[0]
        self.assertEqual(args[0], {'key': 'foo'})

    def test_purge(self):
        store = self._makeOne()
        collection = MagicMock(spec=['update', 'remove', 'find_one'])
        conn = self._makeConnection()
        conn.__getitem__.return_value = collection
        store._get_conn = MagicMock(return_value=conn)

        now = datetime.utcnow()
        with patch('anykeystore.backends.mongodb.datetime') as dt:
            dt.utcnow.return_value = now
            store.purge_expired()

        conn.__getitem__.assert_called_with('keystore')
        args = collection.remove.call_args[0]
        self.assertEqual(args[0], {'expires': {'$lte': now}})
