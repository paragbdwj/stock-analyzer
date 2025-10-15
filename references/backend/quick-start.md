# Quick Start Guide

This guide will get you up and running with the Stock Analyzer in 5 minutes.

## Prerequisites

- Python 3.9 or higher
- Docker (for TimescaleDB)
- Internet connection

## Installation (macOS/Linux)

### Step 1: Start TimescaleDB

```bash
# Start TimescaleDB database
docker-compose up -d

# Verify it's running
docker-compose ps
```

### Step 2: Setup Python Environment

### Option 1: Automated Setup (Recommended)

```bash
# Make setup script executable
chmod +x setup.sh

# Run setup
./setup.sh
```

### Option 2: Manual Setup

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python init_db.py
```

## Installation (Windows)

### Step 1: Start TimescaleDB

```cmd
# Start TimescaleDB database
docker-compose up -d

# Verify it's running
docker-compose ps
```

### Step 2: Setup Python Environment

```cmd
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python init_db.py
```

## Start the Server

```bash
# Make sure virtual environment is activated
python run.py
```

You should see:
```
============================================================
Stock Analyzer API
============================================================
Starting server at http://0.0.0.0:8000
Documentation available at http://localhost:8000/docs
============================================================
```

## Pre-load Stock Data (Optional but Recommended)

Before testing, you can bulk load historical stock data into TimescaleDB for faster queries:

```bash
# Load top 30 NSE stocks (1 year of data)
python load_data.py --exchange NSE --top-n 30

# Or use the Makefile
make load-nse

# Load NASDAQ stocks
make load-nasdaq

# Load specific tickers
python load_data.py --tickers RELIANCE.NS TCS.NS INFY.NS AAPL MSFT

# Check what's in the database
python load_data.py --info
# Or
make cache-info
```

This step is optional because data is automatically fetched and cached when you use the API, but pre-loading makes subsequent queries much faster.

## Test the API

### Option 1: Using the Interactive Docs (Easiest)

1. Open http://localhost:8000/docs in your browser
2. Try the `/health` endpoint by clicking "Try it out" → "Execute"
3. You should see: `{"status": "healthy", "version": "1.0.0"}`

### Option 2: Using cURL

```bash
# Health check
curl http://localhost:8000/health

# Get available exchanges
curl http://localhost:8000/exchanges

# Analyze a stock
curl http://localhost:8000/analyze/RELIANCE.NS
```

### Option 3: Run Example Script

```bash
# Make sure the API server is running in another terminal
python examples/example_usage.py
```

## Your First Scan

Use the interactive docs at http://localhost:8000/docs:

1. Go to **POST /scan**
2. Click "Try it out"
3. Use this example request:

```json
{
  "exchange": "NSE",
  "technical_filters": [
    {"field": "rsi", "operator": "<", "value": 40}
  ],
  "filter_logic": "AND"
}
```

4. Click "Execute"
5. See the results!

## Common Use Cases

### Find Oversold Stocks

```json
{
  "exchange": "NSE",
  "technical_filters": [
    {"field": "rsi", "operator": "<", "value": 30}
  ]
}
```

### Find Stocks with Golden Cross Pattern

```json
{
  "exchange": "NASDAQ",
  "tickers": ["AAPL", "MSFT", "GOOGL"],
  "technical_filters": [
    {"field": "sma_50", "operator": ">", "value": 0}
  ]
}
```

### Find Undervalued Large Cap Stocks

```json
{
  "exchange": "NSE",
  "fundamental_filters": [
    {"field": "trailing_pe", "operator": "<", "value": 15},
    {"field": "market_cap", "operator": ">", "value": 100000000000}
  ],
  "filter_logic": "AND"
}
```

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Explore all endpoints at http://localhost:8000/docs
- Customize filters in `config.json`
- Add your FMP API key in `.env` for enhanced fundamental data (optional)

## Troubleshooting

**Issue**: "Command not found: python3"
- Try `python` instead of `python3`

**Issue**: "Connection refused" or "Database connection failed"
- Make sure TimescaleDB is running: `docker-compose up -d`
- Check if it's healthy: `docker-compose ps`
- Initialize the database: `python init_db.py`

**Issue**: "No data for ticker"
- Check if the ticker symbol is correct
- Try adding the exchange suffix (e.g., `.NS` for NSE)

**Issue**: Scan is slow
- First run downloads data, subsequent runs use cached data from TimescaleDB
- Reduce the number of tickers or use specific ticker list
- Check database connection and performance

**Issue**: Docker not installed
- Install Docker from https://www.docker.com/get-started
- Or follow manual TimescaleDB installation in [TIMESCALEDB_SETUP.md](TIMESCALEDB_SETUP.md)

## Need Help?

- Check the API documentation: http://localhost:8000/docs
- Read the [README.md](README.md)
- Review example scripts in `examples/`

---

Happy Scanning! 📊

