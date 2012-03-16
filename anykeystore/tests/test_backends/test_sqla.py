import unittest2 as unittest
from mock import MagicMock, patch

class TestSQLStore(unittest.TestCase):

    def _getTargetClass(self):
        from anykeystore.backends.sqla import SQLStore
        return SQLStore

    def _makeApi(self):
        api = MagicMock(spec=[
            'engine_from_config', 'MetaData',
            'select', 'insert', 'delete'])
        return api

    def test_init_with_table(self):
        cls = self._getTargetClass()
        api = self._makeApi()
        result = cls('myurl', table='foo', backend_api=api)
        self.assertEqual(result.table, 'foo')

    def test_init_with_table_name(self):
        cls = self._getTargetClass()
        api = self._makeApi()
        api.MetaData.return_value = 'a_meta'
        with patch.object(cls, '_make_table') as _make_table:
            _make_table.return_value = 'some_table'
            result = cls(
                'myurl', table_name='foo', backend_api=api)
        self.assertEqual(result.table, 'some_table')
        _make_table.assert_called_with('foo', 'a_meta')

    def test_init_with_table_name_and_metadata(self):
        cls = self._getTargetClass()
        api = self._makeApi()
        api.MetaData.return_value = 'a_meta'
        with patch.object(cls, '_make_table') as _make_table:
            _make_table.return_value = 'some_table'
            result = cls(
                'myurl', table_name='foo', metadata='b_meta', backend_api=api)
        self.assertEqual(result.table, 'some_table')
        _make_table.assert_called_with('foo', 'b_meta')

    def test__get_conn(self):
        cls = self._getTargetClass()
        api = self._makeApi()
        engine = MagicMock()
        engine.connect.return_value = 'myconn'
        api.engine_from_config.return_value = engine
        table = MagicMock()
        store = cls('myurl', table=table, backend_api=api)
        result = store._get_conn()
        self.assertEqual(result, 'myconn')
        self.assertTrue(store._created)
        self.assertEqual(table.create.call_count, 1)
        self.assertEqual(engine.connect.call_count, 1)

        result = store._get_conn()
        self.assertEqual(result, 'myconn')
        self.assertEqual(table.create.call_count, 1)
        self.assertEqual(engine.connect.call_count, 2)

    def test_retrieve(self):
        cls = self._getTargetClass()
        api = self._makeApi()
        table = MagicMock()
        store = cls('myurl', table=table, backend_api=api)
        with patch.object(store, '_get_conn') as get_conn:
            get_conn.return_value = conn = MagicMock()

            conn.execute.return_value.fetchone.return_value = ('bar', None)
            result = store.retrieve('foo')
            self.assertEqual(result, 'bar')

            conn.execute.return_value.fetchone.return_value = None
            self.assertRaises(KeyError, store.retrieve, 'foo')
