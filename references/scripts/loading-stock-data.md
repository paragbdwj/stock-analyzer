# Loading Stock Data into TimescaleDB

This guide explains how to populate the TimescaleDB database with historical stock data using the `load_data.py` script.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Loading Specific Tickers](#loading-specific-tickers)
- [Loading Exchange Data](#loading-exchange-data)
- [Cache Management](#cache-management)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before loading data, ensure:

1. **Docker is running** with TimescaleDB container
   ```bash
   docker ps
   # Should show: stock_analyzer_timescaledb
   ```

2. **Database is initialized**
   ```bash
   python3 init_db.py
   ```

3. **Virtual environment is activated**
   ```bash
   source venv/bin/activate
   ```

4. **All dependencies are installed**
   ```bash
   pip install -r requirements.txt
   ```

---

## Quick Start

### Load RELIANCE.NS (1 Year Data)

```bash
python3 load_data.py --tickers RELIANCE.NS --period 1y
```

**Result:**
- Ticker: RELIANCE.NS
- Records: ~252 data points (1 year of trading days)
- Date Range: Last 365 days
- Storage: Cached in TimescaleDB

---

## Loading Specific Tickers

### Single Ticker
```bash
python3 load_data.py --tickers AAPL --period 1y
```

### Multiple Tickers
```bash
python3 load_data.py --tickers RELIANCE.NS TCS.NS INFY.NS --period 1y
```

### Indian Stocks (NSE/BSE)
```bash
# NSE stocks (add .NS suffix)
python3 load_data.py --tickers RELIANCE.NS HDFCBANK.NS INFY.NS TCS.NS

# BSE stocks (add .BO suffix)
python3 load_data.py --tickers RELIANCE.BO TCS.BO
```

### US Stocks
```bash
python3 load_data.py --tickers AAPL MSFT GOOGL TSLA AMZN --period 2y
```

---

## Loading Exchange Data

### Top N Stocks from Exchange

**NSE Top 30:**
```bash
python3 load_data.py --exchange NSE --top-n 30 --period 1y
```

**NASDAQ Top 50:**
```bash
python3 load_data.py --exchange NASDAQ --top-n 50 --period 1y
```

**All Stocks from Exchange:**
```bash
python3 load_data.py --exchange NYSE --period 1y
```

### Supported Exchanges
- `NSE` - National Stock Exchange (India)
- `BSE` - Bombay Stock Exchange (India)
- `NASDAQ` - NASDAQ (US)
- `NYSE` - New York Stock Exchange (US)

---

## Time Periods

Available period options:

| Period | Description |
|--------|-------------|
| `1d` | 1 day |
| `5d` | 5 days |
| `1mo` | 1 month |
| `3mo` | 3 months |
| `6mo` | 6 months |
| `1y` | 1 year (default) |
| `2y` | 2 years |
| `5y` | 5 years |
| `10y` | 10 years |
| `ytd` | Year to date |
| `max` | Maximum available |

**Example:**
```bash
# Load 5 years of data
python3 load_data.py --tickers AAPL --period 5y

# Load maximum available data
python3 load_data.py --tickers MSFT --period max
```

---

## Cache Management

### View Cache Information

```bash
python3 load_data.py --info
```

**Output:**
```
Storage Type: TimescaleDB
Total Tickers: 1
Total Records: 252
Date Range: 2024-10-13 to 2025-10-13

Database Size:
  Prices Table: 32 kB
  Metadata Table: 56 kB

Cached Tickers (1):
  - RELIANCE.NS
```

### Clear Cache

**Clear specific ticker:**
```bash
python3 load_data.py --clear --ticker AAPL
```

**Clear all cache:**
```bash
python3 load_data.py --clear
# Confirmation required: type 'yes'
```

### Force Refresh

Force re-download data even if cached:
```bash
python3 load_data.py --tickers RELIANCE.NS --force-refresh
```

---

## Examples

### Example 1: Load Top Indian Stocks
```bash
# Load Nifty 50 major stocks
python3 load_data.py --tickers \
  RELIANCE.NS TCS.NS HDFCBANK.NS INFY.NS ICICIBANK.NS \
  SBIN.NS BHARTIARTL.NS ITC.NS LT.NS KOTAKBANK.NS \
  --period 1y
```

### Example 2: Load FAANG Stocks
```bash
# Load Facebook, Apple, Amazon, Netflix, Google
python3 load_data.py --tickers META AAPL AMZN NFLX GOOGL --period 2y
```

### Example 3: Load and Update Daily
```bash
# Morning routine: update all cached stocks
python3 load_data.py --exchange NSE --top-n 50 --force-refresh --period 1d
```

### Example 4: Historical Analysis (10 Years)
```bash
python3 load_data.py --tickers RELIANCE.NS --period 10y
```

---

## Using Loaded Data

### 1. Start Backend API

```bash
# Option 1: Using run.py
python3 run.py

# Option 2: Using Make
make run

# Option 3: Using uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Access via Frontend

- Open browser: http://localhost:3000
- Navigate to **Analyzer** page
- Enter ticker: `RELIANCE.NS`
- Click **Analyze**
- Data will be fetched from cache (instant!)

### 3. Access via API

```bash
# Analyze using cached data
curl "http://localhost:8000/api/analyze/RELIANCE.NS?use_cache=true"

# Get technical indicators
curl "http://localhost:8000/api/technical/RELIANCE.NS"

# Get fundamental data
curl "http://localhost:8000/api/fundamental/RELIANCE.NS"
```

---

## Troubleshooting

### Issue: ModuleNotFoundError

**Error:**
```
ModuleNotFoundError: No module named 'pandas_ta'
```

**Solution:**
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Issue: Database Connection Failed

**Error:**
```
❌ Database connection failed!
```

**Solutions:**

1. **Check Docker is running:**
   ```bash
   docker ps
   ```

2. **Start TimescaleDB:**
   ```bash
   docker-compose up -d
   ```

3. **Wait for database to be ready:**
   ```bash
   docker logs stock_analyzer_timescaledb
   # Wait for: "database system is ready to accept connections"
   ```

4. **Initialize database:**
   ```bash
   python3 init_db.py
   ```

### Issue: Ticker Not Found

**Error:**
```
Failed tickers: INVALID.NS
```

**Solution:**
- Verify ticker symbol on Yahoo Finance
- For Indian stocks, use correct suffix:
  - NSE: `.NS` (e.g., RELIANCE.NS)
  - BSE: `.BO` (e.g., RELIANCE.BO)
- For US stocks, no suffix needed (e.g., AAPL)

### Issue: Slow Data Loading

**Tips:**
- Load smaller batches (10-20 tickers at a time)
- Use shorter periods for initial testing
- Check internet connection
- Yahoo Finance may rate-limit; add delays between requests

---

## Data Load Summary

### Typical Load Times

| Scenario | Time | Records |
|----------|------|---------|
| 1 stock, 1 year | ~1-2 seconds | ~252 |
| 10 stocks, 1 year | ~10-15 seconds | ~2,520 |
| 50 stocks, 1 year | ~1-2 minutes | ~12,600 |
| 1 stock, 10 years | ~5-10 seconds | ~2,520 |

### Database Size Estimates

| Scenario | Approximate Size |
|----------|------------------|
| 1 stock, 1 year | ~30 KB |
| 100 stocks, 1 year | ~3 MB |
| 500 stocks, 1 year | ~15 MB |
| 100 stocks, 10 years | ~30 MB |

---

## Best Practices

1. **Start Small**: Load a few tickers first to test
2. **Use Cache**: Enable caching for faster subsequent queries
3. **Regular Updates**: Refresh data daily or weekly
4. **Backup Data**: Consider backing up the database periodically
5. **Monitor Size**: Use `--info` to monitor database growth
6. **Clean Old Data**: Use cache clear for outdated tickers

---

## Advanced Usage

### Automated Daily Updates

Create a cron job to update data daily:

```bash
# Edit crontab
crontab -e

# Add this line (runs at 9 AM daily)
0 9 * * * cd /path/to/stock-analyzer && source venv/bin/activate && python3 load_data.py --exchange NSE --top-n 50 --force-refresh --period 1d >> /tmp/stock_update.log 2>&1
```

### Bulk Loading Script

Create a custom script for your watchlist:

```bash
#!/bin/bash
# my_stocks.sh

cd /path/to/stock-analyzer
source venv/bin/activate

# Load my watchlist
python3 load_data.py --tickers \
  RELIANCE.NS TCS.NS INFY.NS \
  AAPL MSFT GOOGL \
  --period 1y \
  --force-refresh

echo "✓ Watchlist updated!"
```

---

## Support

For issues or questions:
1. Check this documentation
2. Review API examples in `references/backend/api-examples.md`
3. Check logs in the terminal output
4. Review database status with `--info` flag

---

**Last Updated:** October 14, 2025
**Script Location:** `/load_data.py`
**Database:** TimescaleDB (PostgreSQL extension)

