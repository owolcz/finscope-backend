from fastapi import APIRouter, Query
from services.finnhub import search_symbol, get_market_status

router = APIRouter()

@router.get("/")
async def search(q: str = Query(..., min_length=1)):
    results = await search_symbol(q)
    return {"query": q, "results": results}


@router.get("/market-status")
async def market_status():
    status = await get_market_status()
    return {"markets": status}
