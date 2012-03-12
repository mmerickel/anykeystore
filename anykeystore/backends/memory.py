from datetime import datetime

from anykeystore.compat import iteritems_
from anykeystore.interfaces import KeyValueStore
from anykeystore.utils import coerce_timedelta

class MemoryStore(KeyValueStore):
    """ In-memory storage. Not persistent."""
    def __init__(self):
        self._store = {}

    def retrieve(self, key):
        data = self._store.get(key)
        if data:
            value, expires = data
            if expires is None or datetime.utcnow() < expires:
                return value
        raise KeyError

    def store(self, key, value, expires=None):
        expiration = None
        if expires:
            expiration = datetime.utcnow() + coerce_timedelta(expires)
        self._store[key] = (value, expiration)

    def delete(self, key):
        if key in self._store:
            del self._store[key]

    def purge_expired(self):
        now = datetime.utcnow()
        to_delete = []

        # Record the keys to delete, there may be a lot, so we use iteritems
        # which doesn't let us change it while iterating
        for key, value in iteritems_(self._store):
            if value[1] is not None and now > value[1]:
                to_delete.append(key)
        for key in to_delete:
            del self._store[key]
        return True

backend = MemoryStore
