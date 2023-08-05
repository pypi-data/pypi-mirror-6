"""
Note:
This is designed to be used with https://github.com/niwibe/django-redis backend
"""
from django.conf import settings
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from redis import WatchError
from redis.client import BasePipeline
from redis_cache.cache import RedisCache

from cascache.exceptions import NoneValueError


MAX_RETRIES = getattr(settings, 'CAS_CACHE_MAX_RETRIES', 10)


class CASMixin(object):
    def cas(self, key, update_func, timeout=DEFAULT_TIMEOUT, version=None,
            client=None):
        if not client:
            client = self.raw_client
        if not isinstance(client, BasePipeline):
            pipe = client.pipeline()

        i = 0
        while i < MAX_RETRIES:
            try:
                pipe.watch(key)
                current_val = self.get(key, version=version, client=pipe)
                assert current_val is not None
                new_val = update_func(current_val)
                if new_val is None:
                    raise NoneValueError('Your update_func must not return None')
                pipe.multi()
                result = self.set(key, new_val, timeout=timeout,
                                  version=version, client=pipe)
                pipe.execute()
                break
            except WatchError:
                i += 1
            finally:
                pipe.reset()
        else:
            return False
        return result

    def cas_many(self, key_to_func_map, timeout=DEFAULT_TIMEOUT, version=None,
                 client=None):
        if not client:
            client = self.raw_client
        if not isinstance(client, BasePipeline):
            pipe = client.pipeline()

        keys = key_to_func_map.keys()
        i = 0
        while i < MAX_RETRIES:
            try:
                pipe.watch(*keys)
                current_vals = self.get_many(keys, version=version, client=pipe)
                new_vals = {}
                for key, val in current_vals.items():
                    assert val is not None
                    new_val = key_to_func_map[key](val)
                    if new_val is None:
                        raise NoneValueError('Your update_func must not return None')
                    new_vals[key] = new_val
                pipe.multi()
                result = self.set_many(new_vals, timeout=timeout,
                                       version=version, client=pipe)
                pipe.execute()
                break
            except WatchError:
                i += 1
            finally:
                pipe.reset()
        else:
            return False
        return result


class RedisCASCache(CASMixin, RedisCache):
    pass
