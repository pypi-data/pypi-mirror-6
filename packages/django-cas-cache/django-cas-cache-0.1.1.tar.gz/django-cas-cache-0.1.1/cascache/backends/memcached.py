from django.conf import settings
from django.core.cache.backends.memcached import MemcachedCache, PyLibMCCache

MAX_RETRIES = settings.get('CAS_CACHE_MAX_RETRIES', 10)


class NoneValueError(Exception):
    pass


class CASMixin(object):
    def cas(self, key, update_func, timeout=0, version=None):
        key = self.make_key(key, version=version)
        i = 0
        while i < MAX_RETRIES:
            current_val = self._cache.gets(key)
            assert current_val is not None
            new_val = update_func(current_val)
            if new_val is None:
                raise NoneValueError('Your update_func must not return None')
            result = self._cache.cas(key, update_func(current_val))
            if result:
                break
            i += 1
        else:
            return 0
        return result


class MemcachedCASCache(CASMixin, MemcachedCache):
    def __init__(self, server, params):
        super(MemcachedCASCache, self).__init__(server, params)
        self._cache.cache_cas = True

    def close(self, **kwargs):
        self._cache.reset_cas()
        super(MemcachedCASCache, self).close(**kwargs)


class PyLibMCCASCache(CASMixin, PyLibMCCache):
    pass
