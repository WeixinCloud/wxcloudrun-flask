import redis
from ..cache import Cache
from config import settings


class RedisOpt(Cache):

    def __init__(self):
        pool = redis.ConnectionPool(**settings.redis)
        self.connector = redis.Redis(connection_pool=pool)

    def lock(self, key, ex=None):
        response = self.connector.set(key, 'lock', nx=True, ex=ex)
        if response:
            return True
        return False

    def has(self, key):
        r = self.connector.exists(key)
        return r == 1

    def get(self, key):
        r = self.connector.get(key)
        if r is None:
            return None
        return str(r, 'utf-8')

    def set(self, key, value, ex=None):
        self.connector.set(key, value, ex=ex)

    def delete(self, key):
        self.connector.delete(key)


cache_opt = RedisOpt()
