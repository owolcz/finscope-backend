from fastapi import APIRouter, HTTPException, Query
from services.alpha_vantage import search_symbol, get_market_status

router = APIRouter()

@router.get("/")
async def search(q: str = Query(..., min_length=1, description="Nazwa lub symbol spółki")):
    """
    Wyszukiwanie spółek. Przykład: /search?q=Apple
    """
    results = await search_symbol(q)
    if not results:
        raise HTTPException(status_code=404, detail="Brak wyników")
    return {"query": q, "results": results}


@router.get("/market-status")
async def market_status():
    """Status rynków światowych – otwarte/zamknięte"""
    status = await get_market_status()
    return {"markets": status}