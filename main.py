# Punkt wejścia aplikacji FastAPI – ładuje zmienne środowiskowe i rejestruje routery.
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from routers import stocks, search

app = FastAPI(title="FinScope API", version="1.0.0")

app.include_router(stocks.router, prefix="/stocks", tags=["Stocks"])
app.include_router(search.router, prefix="/search", tags=["Search"])

# Zwraca potwierdzenie, że API działa.
@app.get("/")
async def root():
    return {"status": "ok"}

# Endpoint healthcheck dla monitoringu.
@app.get("/health")
async def health_check():
    return {"status": "healthy"}
