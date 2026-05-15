from unittest.mock import AsyncMock, MagicMock, patch
import pytest

from services.finnhub import get_stock_quote, search_symbol
from services.cache import quote_cache, search_cache


@pytest.fixture(autouse=True)
def wyczysc_cache():
    # przed każdym testem czyścimy cache, żeby testy nie wpływały na siebie
    quote_cache.clear()
    search_cache.clear()


async def test_get_stock_quote_zwraca_sformatowane_dane():
    # poprawna odpowiedź z API powinna być przetworzona na oczekiwany format
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "c": 150.0, "d": 2.5, "dp": 1.69, "t": 1700000000
    }

    with patch("httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
        result = await get_stock_quote("AAPL")

    assert result["symbol"] == "AAPL"
    assert result["price"] == 150.0
    assert result["change"] == 2.5
    assert "%" in result["change_percent"]


async def test_get_stock_quote_zwraca_none_gdy_brak_danych():
    # gdy API zwraca cenę 0 (brak danych), funkcja powinna zwrócić None
    mock_response = MagicMock()
    mock_response.json.return_value = {"c": 0}

    with patch("httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
        result = await get_stock_quote("INVALID")

    assert result is None


async def test_get_stock_quote_uzywa_cache():
    # jeśli dane są w cache, nie powinno być żadnego wywołania do API
    quote_cache["AAPL"] = {"symbol": "AAPL", "price": 999.0}

    with patch("httpx.AsyncClient") as mock_client:
        result = await get_stock_quote("AAPL")
        mock_client.assert_not_called()

    assert result["price"] == 999.0


async def test_search_symbol_filtruje_tylko_common_stock():
    # wyniki powinny zawierać tylko Common Stock bez kropki w symbolu
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "result": [
            {"symbol": "AAPL",   "description": "Apple Inc.",   "type": "Common Stock"},
            {"symbol": "AAPL.L", "description": "Apple London", "type": "Common Stock"},  # kropka = odfiltrowany
            {"symbol": "QQQM",   "description": "ETF Fund",     "type": "ETF"},           # nie Common Stock
        ]
    }

    with patch("httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
        result = await search_symbol("apple")

    assert len(result) == 1
    assert result[0]["symbol"] == "AAPL"


async def test_search_symbol_zwraca_pusta_liste_gdy_brak_wynikow():
    # brak wyników z API powinien skutkować pustą listą, nie błędem
    mock_response = MagicMock()
    mock_response.json.return_value = {"result": []}

    with patch("httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
        result = await search_symbol("xyznotexist")

    assert result == []
