"""
Note:
This is designed to be used with https://github.com/niwibe/django-redis backend
"""
from django.conf import settings
from redis import WatchError
from redis_cache.cache import RedisCache

from cascache.exceptions import NoneValueError


MAX_RETRIES = settings.get('CAS_CACHE_MAX_RETRIES', 10)


class CASMixin(object):
    def cas(self, key, update_func, timeout=0, version=None):
        key = self.make_key(key, version=version)
        with self.client.pipeline() as pipe:
            i = 0
            while i < MAX_RETRIES:
                try:
                    pipe.watch(key)
                    current_val = pipe.get(key)
                    assert current_val is not None
                    new_val = update_func(current_val)
                    if new_val is None:
                        raise NoneValueError('Your update_func must not return None')
                    pipe.multi()
                    result = pipe.set(key, new_val, timeout=timeout)
                    pipe.execute()
                    break
                except WatchError:
                    i += 1
            else:
                return False
        return result


class RedisCASCache(CASMixin, RedisCache):
    pass
