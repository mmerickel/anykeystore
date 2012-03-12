import unittest

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
