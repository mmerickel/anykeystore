class KeyValueStore(object):
    """ Backend interface for storing and retrieving data."""

    def retrieve(self, key):
        """ This method retrieves the data for a key from the storage.

        :param key: The key to retrieve. Keys are always ascii-safe strings.
        """
        raise NotImplementedError

    def store(self, key, value, expires=None):
        """ This method stores value in the storage.

        For backend's that don't automatically expire data, some record should
        be kept with the key's data marking when it should have expired so that
        :meth:`~velruse.store.interface.purge_expired` can properly purge
        old data.

        :param key: The key to store the value under.
        :param value: The data to store.
        :param expires: Optional expiration time in seconds or a
                        :meth:`datetime.timedelta` object before the stored
                        data should be removed.
        """
        raise NotImplementedError

    def delete(self, key):
        """ This method deletes data from the storage.

        :param key: The key of the data to be removed.
        """
        raise NotImplementedError

    def purge_expired(self):
        """ This method purges all expired data from the storage.

        All expired data should be purged from the backend when this method
        is called. Backends that automatically expire old data must still
        implement this method, but can do nothing.
        """
        raise NotImplementedError
