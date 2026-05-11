from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from routers import stocks, search

app = FastAPI(title="FinScope API", version="1.0.0")

app.include_router(stocks.router, prefix="/stocks", tags=["Stocks"])
app.include_router(search.router, prefix="/search", tags=["Search"])

@app.get("/")
async def root():
    return {"status": "ok"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
