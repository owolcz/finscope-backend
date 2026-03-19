import httpx
import os
from services.cache import (
    get_cached, set_cached,
    quote_cache, history_cache,
    overview_cache, search_cache, market_cache
)

API_KEY = os.getenv("ALPHA_VANTAGE_KEY")
BASE_URL = "https://www.alphavantage.co/query"


async def get_stock_quote(symbol: str):
    """Aktualna cena akcji"""
    cached = get_cached(quote_cache, symbol)
    if cached:
        print(f"[CACHE HIT] quote:{symbol}")
        return cached

    print(f"[CACHE MISS] quote:{symbol}")
    async with httpx.AsyncClient() as client:
        response = await client.get(BASE_URL, params={
            "function": "GLOBAL_QUOTE",
            "symbol": symbol,
            "apikey": API_KEY
        })
        data = response.json()
        quote = data.get("Global Quote", {})

        if not quote:
            return None

        result = {
            "symbol": quote.get("01. symbol"),
            "price": float(quote.get("05. price", 0)),
            "change": float(quote.get("09. change", 0)),
            "change_percent": quote.get("10. change percent", "0%"),
            "volume": int(quote.get("06. volume", 0)),
            "last_updated": quote.get("07. latest trading day")
        }

    set_cached(quote_cache, symbol, result)
    return result


async def get_stock_history(symbol: str):
    """Historia cen z ostatnich 100 dni"""
    cached = get_cached(history_cache, symbol)
    if cached:
        print(f"[CACHE HIT] history:{symbol}")
        return cached

    print(f"[CACHE MISS] history:{symbol}")
    async with httpx.AsyncClient() as client:
        response = await client.get(BASE_URL, params={
            "function": "TIME_SERIES_DAILY",
            "symbol": symbol,
            "outputsize": "compact",
            "apikey": API_KEY
        })
        data = response.json()
        time_series = data.get("Time Series (Daily)", {})

        if not time_series:
            return None

        history = []
        for date, values in time_series.items():
            history.append({
                "date": date,
                "open": float(values.get("1. open", 0)),
                "high": float(values.get("2. high", 0)),
                "low": float(values.get("3. low", 0)),
                "close": float(values.get("4. close", 0)),
                "volume": int(values.get("5. volume", 0))
            })

        history.sort(key=lambda x: x["date"], reverse=True)

    set_cached(history_cache, symbol, history)
    return history


async def get_company_overview(symbol: str):
    """Informacje o spółce"""
    cached = get_cached(overview_cache, symbol)
    if cached:
        print(f"[CACHE HIT] overview:{symbol}")
        return cached

    print(f"[CACHE MISS] overview:{symbol}")
    async with httpx.AsyncClient() as client:
        response = await client.get(BASE_URL, params={
            "function": "OVERVIEW",
            "symbol": symbol,
            "apikey": API_KEY
        })
        data = response.json()

        if not data or "Symbol" not in data:
            return None

        result = {
            "symbol": data.get("Symbol"),
            "name": data.get("Name"),
            "description": data.get("Description"),
            "sector": data.get("Sector"),
            "industry": data.get("Industry"),
            "market_cap": data.get("MarketCapitalization"),
            "pe_ratio": data.get("PERatio"),
            "52_week_high": data.get("52WeekHigh"),
            "52_week_low": data.get("52WeekLow"),
            "dividend_yield": data.get("DividendYield"),
            "country": data.get("Country")
        }

    set_cached(overview_cache, symbol, result)
    return result


async def search_symbol(keywords: str):
    """Wyszukiwanie spółek"""
    cached = get_cached(search_cache, keywords)
    if cached:
        print(f"[CACHE HIT] search:{keywords}")
        return cached

    print(f"[CACHE MISS] search:{keywords}")
    async with httpx.AsyncClient() as client:
        response = await client.get(BASE_URL, params={
            "function": "SYMBOL_SEARCH",
            "keywords": keywords,
            "apikey": API_KEY
        })
        data = response.json()
        matches = data.get("bestMatches", [])

        result = [
            {
                "symbol": m.get("1. symbol"),
                "name": m.get("2. name"),
                "type": m.get("3. type"),
                "region": m.get("4. region"),
                "currency": m.get("8. currency"),
                "match_score": m.get("9. matchScore")
            }
            for m in matches
        ]

    set_cached(search_cache, keywords, result)
    return result


async def get_market_status():
    """Status rynków"""
    cached = get_cached(market_cache, "status")
    if cached:
        print(f"[CACHE HIT] market_status")
        return cached

    print(f"[CACHE MISS] market_status")
    async with httpx.AsyncClient() as client:
        response = await client.get(BASE_URL, params={
            "function": "MARKET_STATUS",
            "apikey": API_KEY
        })
        data = response.json()
        result = data.get("markets", [])

    set_cached(market_cache, "status", result)
    return result