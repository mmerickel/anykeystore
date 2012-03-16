import sys

# True if we are running on Python 3.
PY3 = sys.version_info[0] == 3

try: # pragma: no cover
    import cPickle as pickle
except ImportError: # pragma: no cover
    import pickle

if PY3: # pragma: no cover
    def iteritems_(d):
        return d.items()
    def itervalues_(d):
        return d.values()
    def iterkeys_(d):
        return d.keys()
else: # pragma: no cover
    def iteritems_(d):
        return d.iteritems()
    def itervalues_(d):
        return d.itervalues()
    def iterkeys_(d):
        return d.iterkeys()

if PY3: #pragma: no cover
    basestring = str
else: # pragma: no cover
    basestring = basestring

try: # pragma: no cover
    import configparser
except ImportError: # pragma: no cover
    import ConfigParser as configparser
