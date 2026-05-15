from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_root_zwraca_ok():
    # endpoint główny powinien zwracać status ok
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health_zwraca_healthy():
    # endpoint healthcheck powinien zwracać status healthy
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_stock_quote_zwraca_200():
    # poprawny symbol powinien zwrócić dane kursu z kodem 200
    mock_data = {
        "symbol": "AAPL", "price": 150.0, "change": 1.0,
        "change_percent": "0.67%", "volume": 0, "last_updated": "2024-01-01"
    }
    with patch("routers.stocks.get_stock_quote", AsyncMock(return_value=mock_data)):
        response = client.get("/stocks/AAPL/quote")

    assert response.status_code == 200
    assert response.json()["symbol"] == "AAPL"
    assert response.json()["price"] == 150.0


def test_stock_quote_zwraca_404_gdy_brak_symbolu():
    # nieistniejący symbol powinien zwrócić kod 404
    with patch("routers.stocks.get_stock_quote", AsyncMock(return_value=None)):
        response = client.get("/stocks/INVALID/quote")

    assert response.status_code == 404


def test_stock_history_zwraca_200_z_historia():
    # endpoint historii powinien zwrócić symbol, zakres i listę świec
    mock_history = [
        {"date": "2024-01-01", "open": 100.0, "high": 110.0, "low": 95.0, "close": 105.0, "volume": 1000}
    ]
    with patch("routers.stocks.get_stock_history", AsyncMock(return_value=mock_history)):
        response = client.get("/stocks/AAPL/history?range=1W")

    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == "AAPL"
    assert data["range"] == "1W"
    assert len(data["history"]) == 1


def test_search_zwraca_wyniki():
    # wyszukiwanie powinno zwrócić zapytanie i listę pasujących wyników
    mock_results = [{"symbol": "AAPL", "name": "Apple Inc.", "type": "Common Stock"}]
    with patch("routers.search.search_symbol", AsyncMock(return_value=mock_results)):
        response = client.get("/search/?q=apple")

    assert response.status_code == 200
    assert response.json()["query"] == "apple"
    assert len(response.json()["results"]) == 1


def test_search_bez_parametru_zwraca_422():
    # brak parametru q powinien zwrócić błąd walidacji 422
    response = client.get("/search/")
    assert response.status_code == 422
