from cachetools import TTLCache

# TTLCache(maxsize, ttl)
# maxsize – ile różnych kluczy maksymalnie zapamiętujemy
# ttl – czas życia w sekundach
# 86400 sekund = 24 godziny

# Na czas developmentu wszystko cachujemy na 24h
# Później wystarczy zmienić liczby poniżej
DEV_TTL = 86400  # 24 godziny

quote_cache = TTLCache(maxsize=100, ttl=DEV_TTL)
history_cache = TTLCache(maxsize=100, ttl=DEV_TTL)
overview_cache = TTLCache(maxsize=100, ttl=DEV_TTL)
search_cache = TTLCache(maxsize=100, ttl=DEV_TTL)
market_cache = TTLCache(maxsize=10, ttl=DEV_TTL)


def get_cached(cache, key):
    """Pobiera dane z cache, zwraca None jeśli nie ma"""
    return cache.get(key)


def set_cached(cache, key, value):
    """Zapisuje dane do cache"""
    cache[key] = value