from cachetools import TTLCache
from services.cache import get_cached, set_cached


def test_get_cached_zwraca_none_gdy_puste():
    # pusty cache powinien zwrócić None dla dowolnego klucza
    cache = TTLCache(maxsize=10, ttl=60)
    assert get_cached(cache, "AAPL") is None


def test_set_i_get_cached_dziala():
    # zapisana wartość powinna być możliwa do odczytania tym samym kluczem
    cache = TTLCache(maxsize=10, ttl=60)
    set_cached(cache, "AAPL", {"price": 150.0})
    assert get_cached(cache, "AAPL") == {"price": 150.0}


def test_rozne_klucze_nie_koliduja():
    # dwa różne symbole powinny przechowywać niezależne wartości
    cache = TTLCache(maxsize=10, ttl=60)
    set_cached(cache, "AAPL", {"price": 150.0})
    set_cached(cache, "GOOG", {"price": 200.0})
    assert get_cached(cache, "AAPL") == {"price": 150.0}
    assert get_cached(cache, "GOOG") == {"price": 200.0}


def test_nadpisanie_wartosci_w_cache():
    # ponowny zapis pod tym samym kluczem powinien nadpisać poprzednią wartość
    cache = TTLCache(maxsize=10, ttl=60)
    set_cached(cache, "AAPL", {"price": 100.0})
    set_cached(cache, "AAPL", {"price": 999.0})
    assert get_cached(cache, "AAPL") == {"price": 999.0}
