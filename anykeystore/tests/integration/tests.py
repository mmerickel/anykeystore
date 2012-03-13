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
    requires = []

    @classmethod
    def setUpClass(cls):
        try:
            for req in cls.requires:
                __import__(req)
        except ImportError:
            raise unittest.SkipTest(
                'unsatisfied dependency, tests require "%s"' % req)

    def _makeOne(self):
        from anykeystore import create_store_from_settings
        store = create_store_from_settings(config, prefix=self.key + '.')
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
        store.store('foo', 'bar', expires=1)
        time.sleep(2.5)
        self.assertRaises(KeyError, store.retrieve, 'foo')

    def test_it_purge(self):
        store = self._makeOne()
        store.store('foo', 'bar', expires=1)
        time.sleep(1.1)
        store.purge_expired()
        self.assertRaises(KeyError, store.retrieve, 'foo')

class TestMemory(unittest.TestCase, BackendTests):
    key = 'memory'
    requires = []

class TestSQLA(unittest.TestCase, BackendTests):
    key = 'sqla'
    requires = ['sqlalchemy']

class TestMemcached(unittest.TestCase, BackendTests):
    key = 'memcached'
    requires = ['memcached']

class TestMongoDB(unittest.TestCase, BackendTests):
    key = 'mongodb'
    requires = ['pymongo']

class TestRedis(unittest.TestCase, BackendTests):
    key = 'redis'
    requires = ['redis']

if __name__ == '__main__':
    unittest.main()
