from fastapi import FastAPI, HTTPException
from .stock_data import get_stock_data_from_db

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Welcome to the Stock Analyzer API"}

@app.get("/stocks/{symbol}")
def get_stock(symbol: str):
    try:
        data = get_stock_data_from_db(symbol)
        if not data:
            raise HTTPException(status_code=404, detail="Stock data not found")
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))