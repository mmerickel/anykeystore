import unittest
from datetime import timedelta

class TestCoerceTimedelta(unittest.TestCase):
    def _callFUT(self, value):
        from anykeystore.utils import coerce_timedelta
        return coerce_timedelta(value)

    def test_coerce_with_int(self):
        result = self._callFUT(20)
        self.assertEqual(result, timedelta(seconds=20))

    def test_coerce_with_timedelta(self):
        dt = timedelta(seconds=1)
        result = self._callFUT(dt)
        self.assertEqual(result, dt)

class TestSplitlines(unittest.TestCase):
    def _callFUT(self, value):
        from anykeystore.utils import splitlines
        return splitlines(value)

    def test_it_single_line(self):
        result = self._callFUT('localhost:11211')
        self.assertEqual(result, ['localhost:11211'])

    def test_it_multiple_lines(self):
        result = self._callFUT(' localhost:11211  \n\tfoo:80')
        self.assertEqual(result, ['localhost:11211', 'foo:80'])
