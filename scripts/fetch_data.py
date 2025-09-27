import yfinance as yf
import argparse
import sys
import os

# Adjust the path to import from the app directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.stock_data import store_stock_data

def fetch_and_store_stock_data(symbol):
    """
    Fetches historical stock data for a given symbol and stores it.
    """
    stock = yf.Ticker(symbol)
    
    # Get historical market data
    hist = stock.history(period="max")
    
    if hist.empty:
        print(f"No data found for symbol: {symbol}")
        return
        
    print(f"Fetched {len(hist)} records for {symbol}")
    
    # Store the data
    store_stock_data(symbol.upper(), hist)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch and store stock data.")
    parser.add_argument("--symbol", type=str, required=True, help="Stock symbol to fetch data for (e.g., AAPL)")
    
    args = parser.parse_args()
    
    fetch_and_store_stock_data(args.symbol)