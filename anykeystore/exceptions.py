class ConfigurationError(Exception):
    """ Raised when configuration fails on a backend."""

    def __init__(self, message, exc=None):
        self.message = message
        self.exc = exc
