from ..cache import Cache


class LocalOpt(Cache):

    def __init__(self):
        self.memory = {}

    def has(self, key):
        return key in self.memory

    def get(self, key):
        return self.memory.get(key, None)

    def set(self, key, value, ex=None):
        self.memory[key] = value

    def delete(self, key):
        self.memory.pop(key, None)


cache_opt = LocalOpt()
