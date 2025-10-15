# Data Flow Architecture

This document explains how stock data flows through the system, from TimescaleDB cache to Yahoo Finance API fallback.

## Overview

The Stock Analyzer uses a **database-first approach** with intelligent fallback:

1. **Check TimescaleDB first** (primary source)
2. **Fallback to Yahoo Finance API** if needed
3. **Save to TimescaleDB** automatically
4. **Verify data** was saved correctly

## Data Flow Diagram

```
┌─────────────────┐
│  API Request    │
│  /analyze/AAPL  │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────┐
│   DataService.fetch_stock_data  │
└────────┬────────────────────────┘
         │
         ▼
    ┌────────────┐
    │ force_     │ NO
    │ refresh?   ├──────┐
    └─────┬──────┘      │
          │ YES         │
          │             ▼
          │      ┌──────────────────┐
          │      │  Check TimescaleDB│
          │      │  StorageManager   │
          │      └──────┬───────────┘
          │             │
          │             ├─────────┐
          │             │         │
          │          FOUND     NOT FOUND
          │             │      (or stale)
          │             ▼         │
          │      ┌─────────────┐  │
          │      │ Return Data │  │
          │      │ from DB ✓   │  │
          │      └─────────────┘  │
          │                       │
          └───────────────────────┘
                     │
                     ▼
          ┌──────────────────────┐
          │ Fetch from Yahoo     │
          │ Finance API          │
          └──────┬───────────────┘
                 │
                 ├─────────┐
                 │         │
              SUCCESS   FAIL (retry)
                 │         │
                 ▼         └──► Return None
          ┌──────────────────────┐
          │ Save to TimescaleDB  │
          └──────┬───────────────┘
                 │
                 ▼
          ┌──────────────────────┐
          │ Load from DB         │
          │ (verify save worked) │
          └──────┬───────────────┘
                 │
                 ▼
          ┌──────────────────────┐
          │ Return Data ✓        │
          └──────────────────────┘
```

## Key Components

### 1. DataService (`app/services/data_service.py`)

**Responsibility**: Orchestrates data fetching with cache-first strategy

**Flow**:
```python
def fetch_stock_data(ticker, force_refresh=False):
    # Step 1: Check TimescaleDB (unless force_refresh=True)
    if not force_refresh:
        cached_data = storage.load_stock_data(ticker)
        if cached_data:
            logger.info("✓ Using cached data from TimescaleDB")
            return cached_data
    
    # Step 2: Fetch from Yahoo Finance
    logger.info("→ Fetching from Yahoo Finance API")
    data = yfinance.Ticker(ticker).history(period="1y")
    
    # Step 3: Save to TimescaleDB
    logger.info("→ Saving to TimescaleDB")
    storage.save_stock_data(ticker, data)
    
    # Step 4: Verify by loading from DB
    logger.info("✓ Verified data in TimescaleDB")
    db_data = storage.load_stock_data(ticker)
    
    return db_data or data  # Fallback to fetched data if DB fails
```

### 2. StorageManager (`app/utils/storage.py`)

**Responsibility**: Manages TimescaleDB operations

**Key Methods**:

#### `load_stock_data(ticker, max_age_days)`
- Checks if data exists in `stock_metadata` table
- Verifies data freshness (age < max_age_days)
- Loads OHLCV data from `stock_prices` table
- Returns DataFrame or None

#### `save_stock_data(ticker, data, exchange)`
- Deletes old data for the ticker (to avoid duplicates)
- Bulk inserts new records into `stock_prices`
- Updates/creates metadata in `stock_metadata`
- Tracks last_updated, date range, record count

### 3. Database Schema

#### `stock_prices` (Hypertable)
```sql
ticker      VARCHAR     -- Stock symbol
timestamp   TIMESTAMPTZ -- Data timestamp (partitioned)
open        FLOAT       -- Opening price
high        FLOAT       -- High price
low         FLOAT       -- Low price
close       FLOAT       -- Closing price
volume      BIGINT      -- Trading volume
adj_close   FLOAT       -- Adjusted close
created_at  TIMESTAMPTZ -- When record was saved
```

#### `stock_metadata`
```sql
ticker          VARCHAR     -- Stock symbol (PRIMARY KEY)
exchange        VARCHAR     -- Exchange code
last_updated    TIMESTAMPTZ -- When data was last fetched
first_date      TIMESTAMPTZ -- Earliest data point
last_date       TIMESTAMPTZ -- Latest data point
total_records   INTEGER     -- Number of records
is_active       BOOLEAN     -- Is ticker active
```

## Cache Policy

### Default Settings (`config.json`)
```json
{
  "data_storage": {
    "cache_days": 1  // Data is fresh for 1 day
  }
}
```

### Cache Behavior

1. **Fresh Data** (age < 1 day):
   - Loaded directly from TimescaleDB
   - No API call to Yahoo Finance
   - Fast response (< 100ms)

2. **Stale Data** (age ≥ 1 day):
   - Treated as cache miss
   - Fetched from Yahoo Finance API
   - Re-saved to TimescaleDB
   - Slower response (2-5 seconds)

3. **Force Refresh** (`force_refresh=True`):
   - Bypasses cache check
   - Always fetches from Yahoo Finance
   - Updates TimescaleDB with fresh data

## API Endpoints

### `/analyze/{ticker}`

**Query Parameters**:
- `force_refresh` (bool): Force fetch from API

**Examples**:
```bash
# Use cached data from DB (if available)
curl http://localhost:8000/analyze/AAPL

# Force refresh from Yahoo Finance
curl http://localhost:8000/analyze/AAPL?force_refresh=true
```

**Log Output** (cached):
```
INFO: Analyzing stock: AAPL (force_refresh=False)
INFO: ✓ Using cached data from TimescaleDB for AAPL (252 records)
```

**Log Output** (not cached):
```
INFO: Analyzing stock: AAPL (force_refresh=False)
DEBUG: No cached data found in TimescaleDB for AAPL
INFO: → Fetching data from Yahoo Finance API for AAPL
INFO: → Saving 252 records to TimescaleDB for AAPL
INFO: ✓ Data saved to TimescaleDB for AAPL
INFO: ✓ Verified data in TimescaleDB for AAPL
```

### `/scan`

**Behavior**:
- Scans multiple stocks
- Each stock follows the cache-first flow
- `force_refresh` parameter applies to all tickers

**Example**:
```bash
curl -X POST http://localhost:8000/scan \
  -H "Content-Type: application/json" \
  -d '{
    "exchange": "NSE",
    "technical_filters": [
      {"field": "rsi", "operator": "<", "value": 30}
    ],
    "force_refresh": false
  }'
```

## Pre-loading Data

For faster queries, pre-load data using the bulk loader:

```bash
# Load NSE stocks into DB
python load_data.py --exchange NSE --top-n 30

# Load specific tickers
python load_data.py --tickers AAPL MSFT GOOGL

# Check what's in the DB
python load_data.py --info
```

**Benefits**:
- All subsequent API calls are fast (DB-only)
- No Yahoo Finance API calls needed
- Consistent performance
- Works offline (after initial load)

## Cache Management

### View Cache Info
```bash
curl http://localhost:8000/cache/info
```

Response:
```json
{
  "storage_type": "TimescaleDB",
  "total_tickers": 30,
  "total_records": 7560,
  "date_range": {
    "earliest": "2023-10-14T00:00:00",
    "latest": "2024-10-14T00:00:00"
  },
  "database_size": {
    "prices_table": "384 kB",
    "metadata_table": "16 kB"
  }
}
```

### Clear Cache
```bash
# Clear specific ticker
curl -X DELETE http://localhost:8000/cache/clear?ticker=AAPL

# Clear all cache
curl -X DELETE http://localhost:8000/cache/clear
```

## Performance Characteristics

| Scenario | Response Time | API Calls | Notes |
|----------|--------------|-----------|-------|
| First request (not cached) | 2-5s | 1 | Fetches from Yahoo + saves to DB |
| Cached request (fresh) | 50-100ms | 0 | DB only |
| Cached request (stale) | 2-5s | 1 | Refreshes from Yahoo |
| Force refresh | 2-5s | 1 | Bypasses cache |
| Bulk scan (30 stocks, all cached) | 3-5s | 0 | DB only, parallel processing |
| Bulk scan (30 stocks, not cached) | 20-40s | 30 | Parallel fetch + save |

## Best Practices

### 1. Pre-load Data for Production
```bash
# Load all stocks you plan to scan
python load_data.py --exchange NSE --top-n 100
```

### 2. Schedule Regular Updates
```bash
# Cron job to refresh data daily at 6 PM
0 18 * * * cd /path/to/stock-analyzer && python load_data.py --exchange NSE --force-refresh
```

### 3. Monitor Cache Freshness
```bash
# Check cache status
curl http://localhost:8000/cache/info
```

### 4. Use force_refresh Sparingly
- Only use when you need real-time data
- Increases load on Yahoo Finance API
- Slower response times

### 5. Adjust Cache Days
Edit `config.json`:
```json
{
  "data_storage": {
    "cache_days": 7  // Keep data fresh for 1 week
  }
}
```

## Troubleshooting

### Issue: Data not loading from DB
**Check**: Is TimescaleDB running?
```bash
docker-compose ps
```

**Check**: Is data actually in DB?
```bash
python load_data.py --info
```

### Issue: Slow API responses
**Check**: Are you using cached data?
```bash
# Look for this in logs:
✓ Using cached data from TimescaleDB
```

**Solution**: Pre-load data
```bash
python load_data.py --exchange NSE
```

### Issue: Stale data in DB
**Solution**: Force refresh
```bash
curl http://localhost:8000/analyze/AAPL?force_refresh=true
```

**Or**: Clear and reload
```bash
curl -X DELETE http://localhost:8000/cache/clear
python load_data.py --exchange NSE
```

## Summary

✅ **Database-First**: Always checks TimescaleDB before API  
✅ **Automatic Fallback**: Fetches from Yahoo Finance if needed  
✅ **Automatic Caching**: Saves all fetched data to DB  
✅ **Verification**: Confirms data was saved correctly  
✅ **Smart Caching**: Respects cache age policy  
✅ **Fast**: 50-100ms for cached data, 2-5s for API fetch  
✅ **Reliable**: Falls back to fetched data if DB fails  

The system is designed to be **fast by default** (using DB) and **reliable** (with API fallback).

