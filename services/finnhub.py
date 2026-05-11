import asyncio
import httpx
import os
import yfinance as yf
from datetime import datetime, timedelta, timezone
import zoneinfo
from services.cache import (
    get_cached, set_cached,
    quote_cache, history_cache,
    overview_cache, search_cache, market_cache
)

API_KEY = os.getenv("FINNHUB_KEY")
BASE_URL = "https://finnhub.io/api/v1"

_MARKET_EXCHANGES = [
    {"region": "United States",  "primary_exchanges": "NYSE, NASDAQ",            "tz": "America/New_York", "local_open": "09:30", "local_close": "16:00"},
    {"region": "United Kingdom", "primary_exchanges": "London Stock Exchange",   "tz": "Europe/London",    "local_open": "08:00", "local_close": "16:30"},
    {"region": "Canada",         "primary_exchanges": "Toronto Stock Exchange",  "tz": "America/Toronto",  "local_open": "09:30", "local_close": "16:00"},
    {"region": "Germany",        "primary_exchanges": "Frankfurt Stock Exchange", "tz": "Europe/Berlin",   "local_open": "09:00", "local_close": "17:30"},
]

def _is_market_open(tz_name: str, open_str: str, close_str: str) -> bool:
    tz = zoneinfo.ZoneInfo(tz_name)
    now = datetime.now(tz)
    if now.weekday() >= 5:
        return False
    def t(s):
        h, m = map(int, s.split(":"))
        return now.replace(hour=h, minute=m, second=0, microsecond=0)
    return t(open_str) <= now < t(close_str)


async def get_stock_quote(symbol: str):
    cached = get_cached(quote_cache, symbol)
    if cached and cached.get("price", 0) != 0:
        return cached

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/quote", params={
            "symbol": symbol,
            "token": API_KEY
        })
        data = response.json()

    if not data or data.get("c") == 0:
        return None

    ts = data.get("t")
    last_updated = datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d") if ts else None

    result = {
        "symbol": symbol,
        "price": float(data.get("c", 0)),
        "change": float(data.get("d", 0)),
        "change_percent": f"{float(data.get('dp', 0)):.2f}%",
        "volume": 0,
        "last_updated": last_updated
    }

    set_cached(quote_cache, symbol, result)
    return result


async def get_stock_history(symbol: str):
    cached = get_cached(history_cache, symbol)
    if cached:
        return cached

    loop = asyncio.get_event_loop()

    def fetch():
        ticker = yf.Ticker(symbol)
        return ticker.history(period="6mo")

    data = await loop.run_in_executor(None, fetch)

    if data.empty:
        return None

    history = [
        {
            "date":   date.strftime("%Y-%m-%d"),
            "open":   float(row["Open"]),
            "high":   float(row["High"]),
            "low":    float(row["Low"]),
            "close":  float(row["Close"]),
            "volume": int(row["Volume"]),
        }
        for date, row in data.iterrows()
    ]
    history.sort(key=lambda x: x["date"], reverse=True)

    set_cached(history_cache, symbol, history)
    return history


async def get_asset_quote(symbol: str):
    cached = get_cached(quote_cache, symbol)
    if cached and cached.get("price", 0) != 0:
        return cached

    loop = asyncio.get_event_loop()

    def fetch():
        hist = yf.Ticker(symbol).history(period="5d")
        if hist.empty or len(hist) < 1:
            return None
        price = float(hist["Close"].iloc[-1])
        prev  = float(hist["Close"].iloc[-2]) if len(hist) >= 2 else price
        change = price - prev
        pct    = (change / prev * 100) if prev else 0
        return {
            "symbol":         symbol,
            "price":          price,
            "change":         change,
            "change_percent": f"{pct:.2f}%",
            "volume":         0,
            "last_updated":   hist.index[-1].strftime("%Y-%m-%d"),
        }

    result = await loop.run_in_executor(None, fetch)
    if result and result["price"] != 0:
        set_cached(quote_cache, symbol, result)
    return result


async def get_company_overview(symbol: str):
    cached = get_cached(overview_cache, symbol)
    if cached:
        return cached

    loop = asyncio.get_event_loop()

    def fetch():
        return yf.Ticker(symbol).info

    info = await loop.run_in_executor(None, fetch)

    if not info or not info.get("symbol"):
        return None

    market_cap_raw = info.get("marketCap")
    market_cap = str(market_cap_raw) if market_cap_raw else None

    result = {
        "symbol":       info.get("symbol", symbol),
        "name":         info.get("longName") or info.get("shortName"),
        "description":  info.get("longBusinessSummary"),
        "sector":       info.get("sector"),
        "industry":     info.get("industry"),
        "market_cap":   market_cap,
        "pe_ratio":     str(info["trailingPE"])    if info.get("trailingPE")      else None,
        "52_week_high": str(info["fiftyTwoWeekHigh"]) if info.get("fiftyTwoWeekHigh") else None,
        "52_week_low":  str(info["fiftyTwoWeekLow"])  if info.get("fiftyTwoWeekLow")  else None,
        "dividend_yield": str(info["dividendYield"]) if info.get("dividendYield") else None,
        "country":      info.get("country"),
    }

    set_cached(overview_cache, symbol, result)
    return result


async def get_company_news(symbol: str):
    cache_key = f"news:{symbol}"
    cached = get_cached(market_cache, cache_key)
    if cached:
        return cached

    now = datetime.now(tz=timezone.utc)
    date_to   = now.strftime("%Y-%m-%d")
    date_from = (now - timedelta(days=7)).strftime("%Y-%m-%d")

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/company-news", params={
            "symbol":  symbol,
            "from":    date_from,
            "to":      date_to,
            "token":   API_KEY
        })
        data = response.json()

    if not isinstance(data, list):
        return []

    result = [
        {
            "headline": item.get("headline"),
            "summary":  item.get("summary"),
            "source":   item.get("source"),
            "url":      item.get("url"),
            "image":    item.get("image"),
            "datetime": item.get("datetime"),
        }
        for item in data[:10]
        if item.get("headline")
    ]

    set_cached(market_cache, cache_key, result)
    return result


async def search_symbol(keywords: str):
    cached = get_cached(search_cache, keywords)
    if cached:
        return cached

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/search", params={
            "q":     keywords,
            "token": API_KEY
        })
        data = response.json()

    result = [
        {
            "symbol":      m.get("symbol"),
            "name":        m.get("description"),
            "type":        m.get("type"),
            "region":      None,
            "currency":    None,
            "match_score": None,
        }
        for m in data.get("result", [])
        if m.get("type") == "Common Stock" and "." not in m.get("symbol", ".")
    ]

    if result:
        set_cached(search_cache, keywords, result)
    return result


async def get_market_status():
    result = [
        {
            "region":            ex["region"],
            "primary_exchanges": ex["primary_exchanges"],
            "local_open":        ex["local_open"],
            "local_close":       ex["local_close"],
            "current_status":    "open" if _is_market_open(ex["tz"], ex["local_open"], ex["local_close"]) else "closed",
            "notes":             "",
        }
        for ex in _MARKET_EXCHANGES
    ]
    return result
