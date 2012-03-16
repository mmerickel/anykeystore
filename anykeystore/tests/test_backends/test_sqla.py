import unittest2 as unittest
from mock import MagicMock

class TestSQLStore(unittest.TestCase):

    def _getTargetClass(self):
        from anykeystore.backends.sqla import SQLStore
        return SQLStore

    def test_init_with_table(self):
        cls = self._getTargetClass()
        api = MagicMock(spec=['engine_from_config'])
        result = cls('myurl', table='foo', backend_api=api)
        self.assertEqual(result.table, 'foo')

    def test_init_with_table_name(self):
        cls = self._getTargetClass()
        cls._make_table = MagicMock(return_value='some_table')
        api = MagicMock(spec=['engine_from_config', 'MetaData'])
        api.MetaData.return_value = 'a_meta'
        result = cls(
            'myurl', table_name='foo', backend_api=api)
        self.assertEqual(result.table, 'some_table')
        cls._make_table.assert_called_with('foo', 'a_meta')

    def test_init_with_table_name_and_metadata(self):
        cls = self._getTargetClass()
        cls._make_table = MagicMock(return_value='some_table')
        api = MagicMock(spec=['engine_from_config', 'MetaData'])
        api.MetaData.return_value = 'a_meta'
        result = cls(
            'myurl', table_name='foo', metadata='b_meta', backend_api=api)
        self.assertEqual(result.table, 'some_table')
        cls._make_table.assert_called_with('foo', 'b_meta')
