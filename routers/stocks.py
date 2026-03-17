from fastapi import APIRouter, HTTPException
from services.alpha_vantage import (
    get_stock_quote,
    get_stock_history,
    get_company_overview
)

router = APIRouter()

@router.get("/{symbol}/quote")
async def stock_quote(symbol: str):
    """Aktualna cena akcji. Przykład: /stocks/AAPL/quote"""
    quote = await get_stock_quote(symbol.upper())
    if not quote:
        raise HTTPException(status_code=404, detail=f"Brak danych dla {symbol}")
    return quote


@router.get("/{symbol}/history")
async def stock_history(symbol: str):
    """Historia cen z ostatnich 100 dni. Przykład: /stocks/AAPL/history"""
    history = await get_stock_history(symbol.upper())
    if not history:
        raise HTTPException(status_code=404, detail=f"Brak historii dla {symbol}")
    return {"symbol": symbol.upper(), "history": history}


@router.get("/{symbol}/overview")
async def stock_overview(symbol: str):
    """Informacje o spółce. Przykład: /stocks/AAPL/overview"""
    overview = await get_company_overview(symbol.upper())
    if not overview:
        raise HTTPException(status_code=404, detail=f"Brak danych dla {symbol}")
    return overview