class Cache(object):

    def has(self, key):
        raise NotImplementedError

    def get(self, key):
        raise NotImplementedError

    def set(self, key, value, ex=None):
        raise NotImplementedError

    def delete(self, key):
        raise NotImplementedError

    @classmethod
    def get_cache(cls):
        from .redis_opt import cache_opt
        return cache_opt
