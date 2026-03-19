from fastapi import APIRouter, HTTPException, Query
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
async def stock_history(
    symbol: str,
    range: str = Query(default="1M", description="Zakres: 1W, 1M, 3M")
):
    """
    Historia cen z filtrowaniem po zakresie.
    Przykład: /stocks/AAPL/history?range=1M
    """
    history = await get_stock_history(symbol.upper())
    if not history:
        raise HTTPException(status_code=404, detail=f"Brak historii dla {symbol}")

    # Historia jest posortowana od najnowszej – przycinamy do wybranego zakresu
    range_map = {
        "1W": 7,
        "1M": 30,
        "3M": 90
    }

    days = range_map.get(range.upper(), 30)  # domyślnie 30 dni
    trimmed = history[:days]  # bierzemy pierwsze N wpisów (najnowsze)

    return {"symbol": symbol.upper(), "range": range, "history": trimmed}


@router.get("/{symbol}/overview")
async def stock_overview(symbol: str):
    """Informacje o spółce. Przykład: /stocks/AAPL/overview"""
    overview = await get_company_overview(symbol.upper())
    if not overview:
        raise HTTPException(status_code=404, detail=f"Brak danych dla {symbol}")
    return overview