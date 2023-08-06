# encoding: utf-8

import time


class cacheonceproperty(property):
    """property with cache-once extension."""

    def __init__(self, fget, *args, **kwargs):
        if args or kwargs:
            raise ValueError('cacheonceproperty is only for getters')
        super(cacheonceproperty, self).__init__(fget)
        self._cache = {}

    def __get__(self, obj, klass):
        obj_key = self._cache_key(obj, klass)
        if obj_key not in self._cache:
            cache = super(cacheonceproperty, self).__get__(obj, klass)
            self._cache[obj_key] = cache
        return self._cache[obj_key]

    def _cache_key(self, obj, klass):
        return hex(id(obj)) + hex(int(time.time()))
