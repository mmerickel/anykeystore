import unittest

from mock import Mock, patch

class TestStore(unittest.TestCase):

    def test_create_store(self):
        from anykeystore import create_store
        store = create_store('memory')

        from anykeystore.backends.memory import MemoryStore
        self.assertTrue(isinstance(store, MemoryStore))

    def test_create_store_from_settings(self):
        from anykeystore import create_store_from_settings
        store = create_store_from_settings({'store': 'memory'})

        from anykeystore.backends.memory import MemoryStore
        self.assertTrue(isinstance(store, MemoryStore))

    def test_create_store_from_settings_with_prefix(self):
        from anykeystore import create_store_from_settings
        store = create_store_from_settings(
            {'any.store': 'memory'}, prefix='any.')

        from anykeystore.backends.memory import MemoryStore
        self.assertTrue(isinstance(store, MemoryStore))

    @patch('anykeystore.store._load_entry_point')
    def test_create_nonexistent_store(self, load_entry_point):
        from anykeystore import create_store
        from anykeystore.exceptions import ConfigurationError

        load_entry_point.return_value = None

        self.assertRaises(ConfigurationError, create_store, '_dumbdb')
        load_entry_point.assert_called_with('_dumbdb')

    @patch('anykeystore.store._load_entry_point')
    def test_create_nonexistent_substore(self, load_entry_point):
        from anykeystore import create_store
        from anykeystore.exceptions import ConfigurationError

        load_entry_point.return_value = None

        dumbdb = {'anykeystore.backends._dumbdb': 'foo'}
        with patch.dict('sys.modules', dumbdb):
            self.assertRaises(ConfigurationError, create_store, '_dumbdb')
            load_entry_point.assert_called_with('_dumbdb')

    @patch('anykeystore.store._load_entry_point')
    def test__load_backend_via_entry_point(self, load_entry_point):
        from anykeystore.store import _load_backend

        load_entry_point.return_value = 'foo_module'

        result = _load_backend('foo')

        load_entry_point.assert_called_with('foo')
        self.assertEqual(result, 'foo_module')

    @patch('anykeystore.store.pkg_resources')
    def test__load_entry_point(self, pkg_resources):
        from anykeystore.store import _load_entry_point

        foo_mock = Mock(spec=['name', 'load'])
        foo_mock.name = 'foo'
        foo_mock.load.return_value = 'bar'
        pkg_resources.iter_entry_points.return_value = [foo_mock]
        result = _load_entry_point('foo')
        self.assertEqual(result, 'bar')

    @patch('anykeystore.store.pkg_resources')
    def test__load_nonexistent_entry_point(self, pkg_resources):
        from anykeystore.store import _load_entry_point

        foo_mock = Mock(spec=['name', 'load'])
        foo_mock.name = 'foo'
        pkg_resources.iter_entry_points.return_value = [foo_mock]
        result = _load_entry_point('bar')
        self.assertEqual(result, None)

    @patch('anykeystore.store.pkg_resources', new=None)
    def test__load__entry_point_with_no_pkg_resources(self):
        from anykeystore.store import _load_entry_point

        result = _load_entry_point('bar')
        self.assertEqual(result, None)
