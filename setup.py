from setuptools import setup, find_packages
import sys, os

here = os.path.abspath(os.path.dirname(__file__))
try:
    README = open(os.path.join(here, 'README.rst')).read()
    CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()
except IOError:
    README = CHANGES = ''

requires = []

setup(
    name='anykeystore',
    version='0.1a2',
    description="A key-value store supporting multiple backends.",
    long_description=README + '\n\n' + CHANGES,
    # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 3 - Alpha',
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        'Topic :: Database',
        'License :: OSI Approved :: MIT License',
    ],
    keywords='',
    author='Michael Merickel',
    author_email='oss@m.merickel.org',
    url='',
    license='MIT',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=requires,
    test_suite="anykeystore.tests",
    entry_points="""\
    """,
)
