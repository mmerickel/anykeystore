from datetime import datetime

from anykeystore.compat import pickle
from anykeystore.interfaces import KeyValueStore
from anykeystore.utils import coerce_timedelta


class MongoDBStore(KeyValueStore):
    """ Simple storage via MongoDB.

    :param db: The name of the database.
    :param collection: Optional (default="anykeystore").
                       The document collection within the database.
    :param host: MongoDB server host.
    :param port: MongoDB server port.
    """

    def __init__(self,
                 db,
                 collection='anykeystore',
                 host='localhost',
                 port=27017,
                 backend_api=None):
        self.host = host
        self.port = int(port)
        self.db = db
        self.collection = collection
        self.backend_api = backend_api

    @classmethod
    def backend_api(cls):
        import pymongo
        import pymongo.binary
        return pymongo

    def _get_conn(self):
        db_conn = self.backend_api.Connection(
            self.host, self.port, slave_okay=False)
        conn = db_conn[self.db]
        if not self.collection in conn.collection_names():
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
        api = self.backend_api
        c[self.collection].update(
            {'key': key},
            {
                '$set': {
                    'value': api.binary.Binary(pickle.dumps(value)),
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
