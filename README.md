# FinScope Backend

Backend dla aplikacji finansowej iOS. Zbudowany w Python + FastAPI, agreguje dane z Alpha Vantage API.

## Wymagania
- Python 3.x
- Klucz API z [Alpha Vantage](https://www.alphavantage.co/support/#api-key) (darmowy)

## Uruchomienie

### 1. Sklonuj repozytorium
```
git clone https://github.com/TWOJ_LOGIN/finance-app-backend.git
cd finance-app-backend
```

### 2. Stwórz wirtualne środowisko
```
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Zainstaluj zależności
```
pip install -r requirements.txt
```

### 4. Skonfiguruj klucz API
```
cp .env.example .env
```
Otwórz plik `.env` i wpisz swój klucz API z Alpha Vantage.

### 5. Uruchom serwer
```
uvicorn main:app --reload
```

Serwer działa na http://localhost:8000
Dokumentacja API: http://localhost:8000/docs

## Endpointy
| Endpoint | Opis |
|---|---|
| GET /stocks/{symbol}/quote | Aktualna cena akcji |
| GET /stocks/{symbol}/history | Historia cen (100 dni) |
| GET /stocks/{symbol}/overview | Informacje o spółce |
| GET /search?q={query} | Wyszukiwanie spółek |
| GET /search/market-status | Status rynków |
