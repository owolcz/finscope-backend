# Router wyszukiwania – obsługuje wyszukiwanie symboli akcji.
from fastapi import APIRouter, Query
from services.finnhub import search_symbol

router = APIRouter()

# Wyszukuje akcje pasujące do podanego zapytania.
@router.get("/")
async def search(q: str = Query(..., min_length=1)):
    results = await search_symbol(q)
    return {"query": q, "results": results}
