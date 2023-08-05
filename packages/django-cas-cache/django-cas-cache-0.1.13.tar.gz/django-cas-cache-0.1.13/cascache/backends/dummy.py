from django.core.cache.backends.dummy import DummyCache

from cascache.compatibility import DEFAULT_TIMEOUT


class CASMixin(object):
    def cas(self, key, update_func, timeout=DEFAULT_TIMEOUT, version=None):
        key = self.make_key(key, version=version)
        self.validate_key(key)
        return True


class DummyCASCache(CASMixin, DummyCache):
    pass
