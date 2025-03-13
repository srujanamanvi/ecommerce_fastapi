import time


class Cache:
    def __init__(self, ttl_seconds=300):
        self.cache = {}
        self.ttl_seconds = ttl_seconds

    def get(self, key):
        if key in self.cache:
            value, expiry = self.cache[key]
            if expiry > time.time():
                return value
            else:
                del self.cache[key]
        return None

    def set(self, key, value):
        self.cache[key] = (value, time.time() + self.ttl_seconds)

    def invalidate(self, key_prefix=None):
        if key_prefix:
            keys_to_delete = [k for k in self.cache.keys() if k.startswith(key_prefix)]
            for key in keys_to_delete:
                del self.cache[key]
        else:
            self.cache.clear()


# Create cache instances with different TTLs
order_cache = Cache(ttl_seconds=300)
