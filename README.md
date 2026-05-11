# FinScope Backend

Backend dla aplikacji iOS FinScope. Zbudowany w Python + FastAPI, pobiera dane z Finnhub API.

## Wymagania

- Python 3.9+
- Klucz API z [Finnhub](https://finnhub.io) (darmowy plan wystarczy)

## Uruchomienie

### 1. Sklonuj repozytorium
```
git clone https://github.com/owolcz/finscope-backend.git
cd finscope-backend
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
Otwórz plik `.env` i wpisz swój klucz z Finnhub:
```
FINNHUB_KEY=twoj_klucz_tutaj
```

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
| GET /stocks/{symbol}/history | Historia cen (6 miesięcy) |
| GET /stocks/{symbol}/overview | Informacje o spółce |
| GET /stocks/{symbol}/news | Najnowsze wiadomości |
| GET /stocks/assets/{symbol}/quote | Cena kryptowaluty lub waluty forex |
| GET /search?q={query} | Wyszukiwanie spółek |
| GET /search/market-status | Status giełd |
