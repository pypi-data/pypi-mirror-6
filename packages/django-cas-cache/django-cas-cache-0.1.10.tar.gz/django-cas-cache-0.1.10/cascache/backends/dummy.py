from django.core.cache.backends.dummy import DummyCache


class CASMixin(object):
    def cas(self, key, update_func, timeout=0, version=None):
        key = self.make_key(key, version=version)
        self.validate_key(key)
        return True


class DummyCASCache(CASMixin, DummyCache):
    pass
