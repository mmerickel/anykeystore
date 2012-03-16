import os
import time
import unittest2 as unittest
from ConfigParser import ConfigParser


config = {}

def setUpModule():
    inipath = os.environ.get('TEST_INI', 'testing.ini')
    if os.path.isfile(inipath):
        parser = ConfigParser()
        parser.read(inipath)

        config.update(parser.items('testconfig'))

    else:
        raise unittest.SkipTest(
            'could not find testing.ini required to run integration tests')

class BackendTests(object):
    expires = -1
    wait = 0

    def _makeOne(self):
        from anykeystore import create_store_from_settings
        try:
            store = create_store_from_settings(config, prefix=self.key + '.')
        except ImportError as e:
            raise unittest.SkipTest(str(e))
        return store

    def test_it(self):
        store = self._makeOne()
        store.store('foo', 'bar')
        value = store.retrieve('foo')
        self.assertEqual(value, 'bar')

    def test_delete(self):
        store = self._makeOne()
        store.store('foo', 'bar')
        store.delete('foo')
        self.assertRaises(KeyError, store.retrieve, 'foo')

    def test_retrieve_expired(self):
        store = self._makeOne()
        store.store('foo', 'bar', expires=self.expires)
        time.sleep(self.wait)
        self.assertRaises(KeyError, store.retrieve, 'foo')

    def test_purge(self):
        store = self._makeOne()
        store.store('foo', 'bar', expires=self.expires)
        time.sleep(self.wait)
        store.purge_expired()
        self.assertRaises(KeyError, store.retrieve, 'foo')

class TestMemory(unittest.TestCase, BackendTests):
    key = 'memory'

class TestSQLA(unittest.TestCase, BackendTests):
    key = 'sqla'

class TestMemcached(unittest.TestCase, BackendTests):
    key = 'memcached'
    expires = 1
    wait = 2

class TestMongoDB(unittest.TestCase, BackendTests):
    key = 'mongodb'

class TestRedis(unittest.TestCase, BackendTests):
    key = 'redis'
    expires = 1
    wait = 2

if __name__ == '__main__':
    unittest.main()
