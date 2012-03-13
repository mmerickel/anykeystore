from datetime import datetime

from pymongo import Connection
from pymongo.binary import Binary

from anykeystore.compat import pickle
from anykeystore.interfaces import KeyValueStore
from anykeystore.utils import coerce_timedelta


class MongoDBStore(KeyValueStore):
    """ Simple storage via MongoDB.

    :param db: The name of the mongo database.
    :param collection: Optional (default="key_storage").
                       The document collection within the database.
    :param host: MongoDB server host.
    :param port: MongoDB server port.
    """

    def __init__(self,
                 db,
                 collection='anykeystore',
                 host='localhost',
                 port=27017):
        self.host = host
        self.port = int(port)
        self.db = db
        self.collection = collection

    def _get_conn(self):
        db_conn = Connection(self.host, self.port, slave_okay=False)
        conn = db_conn[self.db]
        #Set arbitrary limit on how large user_store session can grow to
        #http://www.mongodb.org/display/DOCS/Capped+Collections
        if not self.collection in conn.collection_names(): # pragma: no cover
            conn.create_collection(self.collection)
        return conn

    def retrieve(self, key):
        c = self._get_conn()
        data = c[self.collection].find_one({'key': key})
        if data:
            expires = data['expires']
            if expires is None or datetime.utcnow() < expires:
                return pickle.loads(data['value'])
        raise KeyError

    def store(self, key, value, expires=None):
        expiration = None
        if expires is not None:
            expiration = datetime.utcnow() + coerce_timedelta(expires)
        c = self._get_conn()
        c[self.collection].update(
            {'key': key},
            {
                '$set': {
                    'value': Binary(pickle.dumps(value)),
                    'expires': expiration,
                },
            },
            upsert=True,
            safe=True,
        )

    def delete(self, key):
        c = self._get_conn()
        c[self.collection].remove({'key': key}, safe=True)

    def purge_expired(self):
        c = self._get_conn()
        c[self.collection].remove(
            {'expires': {'$lte': datetime.utcnow()}},
            safe=True,
        )

backend = MongoDBStore
