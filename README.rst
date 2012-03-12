===========
anykeystore
===========

A generic interface wrapping multiple different backends to provide a
consistent key-value storage API. This library is intended to be used by other
libraries that require some form of generic storage.

Usage
=====

    from anykeystore import create_store

    store = create_store(
        'sqla', url='postgres+psycopg2://bob@localhost/mydb')

.. code-block:: python

    settings = {
        'mystore.store': 'sqla',
        'mystore.url': 'mysql://bob@localhost/mydb',
    }

    store = create_store_from_settings(settings, prefix='mystore.')
