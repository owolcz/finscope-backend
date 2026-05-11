from cachetools import TTLCache

CACHE_TTL = 86400

quote_cache    = TTLCache(maxsize=100, ttl=CACHE_TTL)
history_cache  = TTLCache(maxsize=100, ttl=CACHE_TTL)
overview_cache = TTLCache(maxsize=100, ttl=CACHE_TTL)
search_cache   = TTLCache(maxsize=100, ttl=CACHE_TTL)
market_cache   = TTLCache(maxsize=10,  ttl=CACHE_TTL)


def get_cached(cache, key):
    return cache.get(key)


def set_cached(cache, key, value):
    cache[key] = value
