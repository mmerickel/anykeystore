import sys

from anykeystore.exceptions import ConfigurationError

def _load_backend(name):
    try:
        module_name = 'anykeystore.backends.%s' % name
        __import__(module_name)
        module = sys.modules[module_name]
        if hasattr(module, 'backend'):
            backend = module.backend
        else:
            module = _load_entry_point(name)
            if module is None:
                raise ConfigurationError(
                    'Could not determine backend for "%s"' % name)
        return backend
    except ImportError:
        module = _load_entry_point(name)
        if module is None:
            return module
        raise ConfigurationError(
            'Could not determine backend for "%s"' % name)

def _load_entry_point(name):
    try:
        import pkg_resources
    except ImportError:
        return None

    for res in pkg_resources.iter_entry_points('anykeystore.backends'):
        if res.name == name:
            return res.load()

def create_store(name, **kwargs):
    backend_cls = _load_backend(name)
    return backend_cls(**kwargs)

def create_store_from_settings(settings, prefix='', **kwargs):
    plen = len(prefix)
    for k, v in settings.items():
        if k.startswith(prefix):
            kwargs[k[plen:]] = v
    name = kwargs.pop('store')
    return create_store(name, **kwargs)
