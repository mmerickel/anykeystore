from setuptools import setup, find_packages
import sys, os

py_version = sys.version_info[:2]

PY3 = py_version[0] == 3

if PY3:
    if py_version < (3, 2):
        raise RuntimeError('On Python 3, Pyramid requires Python 3.2 or better')
else:
    if py_version < (2, 6):
        raise RuntimeError('On Python 2, Pyramid requires Python 2.6 or better')

here = os.path.abspath(os.path.dirname(__file__))
try:
    README = open(os.path.join(here, 'README.rst')).read()
    CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()
except IOError:
    README = CHANGES = ''

requires = []

setup(
    name='anykeystore',
    version='0.3',
    description="A key-value store supporting multiple backends.",
    long_description=README + '\n\n' + CHANGES,
    # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 3 - Beta',
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        'Topic :: Database',
        'License :: OSI Approved :: MIT License',
    ],
    keywords='',
    author='Michael Merickel',
    author_email='oss@m.merickel.org',
    url='',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=requires,
    extras_require={
        'testing': [
            'nose',
            'mock',
            'nose-testconfig',
        ],
        'sqla': [
            'sqlalchemy',
        ],
        'mongodb': [
            'pymongo',
        ],
        'redis': [
            'redis',
        ],
        'memcached': [
            'python3-memcache' if PY3 else 'python-memcache',
        ],
    },
    entry_points="""\
    """,
)
