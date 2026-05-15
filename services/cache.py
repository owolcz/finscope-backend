# Moduł cache – globalne obiekty TTLCache (24h) i pomocnicze funkcje odczytu/zapisu.
from cachetools import TTLCache

CACHE_TTL = 86400  # 24 godziny w sekundach

quote_cache    = TTLCache(maxsize=100, ttl=CACHE_TTL)  # kursy akcji
history_cache  = TTLCache(maxsize=100, ttl=CACHE_TTL)  # historia cenowa
overview_cache = TTLCache(maxsize=100, ttl=CACHE_TTL)  # przeglądy spółek
search_cache   = TTLCache(maxsize=100, ttl=CACHE_TTL)  # wyniki wyszukiwania
market_cache   = TTLCache(maxsize=10,  ttl=CACHE_TTL)  # wiadomości spółek


# Zwraca wartość z cache lub None jeśli klucz nie istnieje.
def get_cached(cache, key):
    return cache.get(key)


# Zapisuje wartość pod danym kluczem w cache.
def set_cached(cache, key, value):
    cache[key] = value
