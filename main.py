from fastapi import FastAPI
from dotenv import load_dotenv
from routers import stocks, search

load_dotenv()

app = FastAPI(
    title="Finance App API",
    description="Backend dla aplikacji finansowej iOS",
    version="1.0.0"
)

app.include_router(stocks.router, prefix="/stocks", tags=["Stocks"])
app.include_router(search.router, prefix="/search", tags=["Search"])

@app.get("/")
async def root():
    return {"status": "ok", "message": "Finance API działa!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}