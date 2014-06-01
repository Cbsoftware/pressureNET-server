from django.conf import settings
from django.core.cache import cache

from rest_framework.throttling import BaseThrottle


def get_lock_key(api_key):
    return 'lock_{key}'.format(key=api_key)


class APIKeyLockThrottle(BaseThrottle):

    def allow_request(self, request, view):
        if 'api_key' in request.GET:
            api_key = request.GET['api_key']
            lock_key = get_lock_key(api_key)

            if lock_key in cache:
                return False
            else:
                cache.set(lock_key, True, timeout=settings.CACHE_LOCK_TIMEOUT)

        return True

    def wait(self):
        return 1
