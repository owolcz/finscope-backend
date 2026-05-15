# Router akcji – endpointy do pobierania kursu, historii, przeglądu spółki i wiadomości.
from fastapi import APIRouter, HTTPException, Query
from services.finnhub import (
    get_stock_quote,
    get_stock_history,
    get_company_overview,
    get_company_news,
    get_asset_quote
)

router = APIRouter()

# Zwraca aktualny kurs akcji dla podanego symbolu.
@router.get("/{symbol}/quote")
async def stock_quote(symbol: str):
    quote = await get_stock_quote(symbol.upper())
    if not quote:
        raise HTTPException(status_code=404, detail=f"No data for {symbol}")
    return quote


# Zwraca historię cenową akcji; parametr range określa zakres: 1W, 1M lub 3M.
@router.get("/{symbol}/history")
async def stock_history(
    symbol: str,
    range: str = Query(default="1M")
):
    history = await get_stock_history(symbol.upper())
    if not history:
        raise HTTPException(status_code=404, detail=f"No history for {symbol}")

    range_map = {"1W": 7, "1M": 30, "3M": 90}
    days = range_map.get(range.upper(), 30)
    trimmed = history[:days]

    return {"symbol": symbol.upper(), "range": range, "history": trimmed}


# Zwraca podstawowe informacje o spółce (sektor, P/E, kapitalizacja itp.).
@router.get("/{symbol}/overview")
async def stock_overview(symbol: str):
    overview = await get_company_overview(symbol.upper())
    if not overview:
        raise HTTPException(status_code=404, detail=f"No data for {symbol}")
    return overview


# Zwraca kurs dla aktywów innych niż akcje (np. kryptowaluty, forex) via yfinance.
@router.get("/assets/{symbol}/quote")
async def asset_quote(symbol: str):
    quote = await get_asset_quote(symbol)
    if not quote:
        raise HTTPException(status_code=404, detail=f"No data for {symbol}")
    return quote


# Zwraca ostatnie wiadomości z ostatnich 7 dni dla podanego symbolu.
@router.get("/{symbol}/news")
async def stock_news(symbol: str):
    news = await get_company_news(symbol.upper())
    return {"symbol": symbol.upper(), "news": news}
