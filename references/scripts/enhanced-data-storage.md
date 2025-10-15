# Enhanced Data Storage - Fundamentals & Technical Indicators

## Overview

The stock analyzer now supports storing **fundamental data** and **technical indicators** alongside OHLCV (Open, High, Low, Close, Volume) data in TimescaleDB. This enhancement provides a comprehensive data foundation for stock analysis.

## What's New

### 1. **20-Year Historical Data (Default)**
- Changed default period from `1y` to `20y`
- Supports all Yahoo Finance periods: `1d`, `5d`, `1mo`, `3mo`, `6mo`, `1y`, `2y`, `5y`, `10y`, `20y`, `ytd`, `max`
- Use `max` to get all available historical data for a stock

### 2. **Fundamental Data Storage**
Automatically fetches and stores fundamental metrics including:

#### Valuation Metrics
- Trailing P/E Ratio
- Forward P/E Ratio
- Price to Book (P/B)
- Price to Sales (P/S)
- PEG Ratio

#### Financial Health Metrics
- Market Cap
- Enterprise Value
- Debt to Equity
- Current Ratio
- Quick Ratio

#### Profitability Metrics
- Profit Margin
- Operating Margin
- Return on Assets (ROA)
- Return on Equity (ROE)

#### Growth & Dividend Metrics
- Revenue Growth
- Earnings Growth
- Dividend Yield
- Payout Ratio

#### Risk Metrics
- Beta

#### Company Information
- Sector
- Industry

### 3. **Technical Indicators Storage**
Automatically calculates and stores technical indicators for each trading day:

#### Moving Averages
- SMA: 20, 50, 100, 200-day
- EMA: 12, 26, 50, 200-day

#### Momentum Indicators
- RSI (Relative Strength Index)
- MACD (with signal line and histogram)
- Stochastic Oscillator (K and D)

#### Volatility Indicators
- ATR (Average True Range)
- Bollinger Bands (upper, middle, lower)
- 20-day Rolling Volatility

#### Volume Indicators
- OBV (On-Balance Volume)
- 20-day Volume SMA

#### Trend Indicators
- ADX (Average Directional Index)
- DI+ and DI- (Directional Indicators)

#### Derived Metrics
- Daily Returns
- Cumulative Returns
- 20-day Volatility

## Database Schema

### New Tables

#### 1. `stock_fundamentals`
```sql
CREATE TABLE stock_fundamentals (
    ticker VARCHAR(20) PRIMARY KEY,
    timestamp TIMESTAMP PRIMARY KEY,
    trailing_pe FLOAT,
    forward_pe FLOAT,
    price_to_book FLOAT,
    price_to_sales FLOAT,
    peg_ratio FLOAT,
    market_cap BIGINT,
    enterprise_value BIGINT,
    debt_to_equity FLOAT,
    current_ratio FLOAT,
    quick_ratio FLOAT,
    profit_margin FLOAT,
    operating_margin FLOAT,
    return_on_assets FLOAT,
    return_on_equity FLOAT,
    revenue_growth FLOAT,
    earnings_growth FLOAT,
    dividend_yield FLOAT,
    payout_ratio FLOAT,
    beta FLOAT,
    sector VARCHAR(100),
    industry VARCHAR(100),
    created_at TIMESTAMP
);
```

#### 2. `stock_technical_indicators` (TimescaleDB Hypertable)
```sql
CREATE TABLE stock_technical_indicators (
    ticker VARCHAR(20) PRIMARY KEY,
    timestamp TIMESTAMP PRIMARY KEY,
    sma_20 FLOAT,
    sma_50 FLOAT,
    sma_100 FLOAT,
    sma_200 FLOAT,
    ema_12 FLOAT,
    ema_26 FLOAT,
    ema_50 FLOAT,
    ema_200 FLOAT,
    rsi FLOAT,
    macd FLOAT,
    macd_signal FLOAT,
    macd_histogram FLOAT,
    atr FLOAT,
    bb_upper FLOAT,
    bb_middle FLOAT,
    bb_lower FLOAT,
    obv BIGINT,
    volume_sma_20 BIGINT,
    adx FLOAT,
    di_plus FLOAT,
    di_minus FLOAT,
    stoch_k FLOAT,
    stoch_d FLOAT,
    daily_return FLOAT,
    cumulative_return FLOAT,
    volatility_20d FLOAT,
    created_at TIMESTAMP
);
```

## Migration

### Step 1: Run Database Migration
```bash
# Create new tables and indexes
python migrate_db.py

# Check table information
python migrate_db.py --info
```

This will:
- Create `stock_fundamentals` table
- Create `stock_technical_indicators` table (as TimescaleDB hypertable)
- Add appropriate indexes for fast queries

## Usage

### Loading Data with All Features (Default)

```bash
# Load NSE top 30 stocks with 20 years of data, indicators, and fundamentals
python load_data.py --exchange NSE --top-n 30

# Load specific tickers with all features
python load_data.py --tickers AAPL MSFT GOOGL

# Load with maximum available data
python load_data.py --tickers RELIANCE.NS --period max
```

### Loading Data Selectively

```bash
# Load only OHLCV data (no indicators or fundamentals)
python load_data.py --exchange NSE --no-indicators --no-fundamentals

# Load OHLCV and indicators (skip fundamentals)
python load_data.py --tickers AAPL --no-fundamentals

# Load OHLCV and fundamentals (skip indicators)
python load_data.py --tickers AAPL --no-indicators
```

### Period Options

```bash
# Load 5 years of data
python load_data.py --tickers AAPL --period 5y

# Load 1 month of data
python load_data.py --tickers AAPL --period 1mo

# Load all available data (could be 20+ years)
python load_data.py --tickers AAPL --period max
```

## Programmatic Usage

### Using DataService

```python
from app.services.data_service import DataService

data_service = DataService()

# Fetch with all features
data = data_service.fetch_stock_data(
    ticker="AAPL",
    period="20y",
    include_indicators=True,
    include_fundamentals=True
)

# Fetch multiple stocks
results = data_service.fetch_multiple_stocks(
    tickers=["AAPL", "MSFT", "GOOGL"],
    period="20y",
    include_indicators=True,
    include_fundamentals=True
)
```

### Using StorageManager

```python
from app.utils.storage import StorageManager

storage = StorageManager()

# Load fundamental data
fundamentals = storage.load_fundamental_data("AAPL")
print(f"P/E Ratio: {fundamentals['trailing_pe']}")
print(f"Market Cap: ${fundamentals['market_cap']:,}")

# Load technical indicators
indicators = storage.load_technical_indicators("AAPL")
print(f"Latest RSI: {indicators['rsi'].iloc[-1]}")
print(f"Latest MACD: {indicators['macd'].iloc[-1]}")

# Load OHLCV data
prices = storage.load_stock_data("AAPL")
```

## API Integration

The backend API has been updated to support querying fundamentals and technical indicators:

### Endpoints (Coming Soon)

```
GET /api/fundamentals/{ticker}
GET /api/indicators/{ticker}
GET /api/indicators/{ticker}?start_date=2020-01-01&end_date=2024-01-01
```

## Performance Considerations

### Storage Requirements

- **OHLCV Data**: ~40 bytes per record
- **Technical Indicators**: ~150 bytes per record
- **Fundamental Data**: ~300 bytes per snapshot

**Example for 1 stock with 20 years of data (~5,000 trading days):**
- OHLCV: ~200 KB
- Technical Indicators: ~750 KB
- Fundamentals: ~300 bytes (single snapshot)
- **Total: ~950 KB per stock**

**For 100 stocks**: ~95 MB total storage

### Query Performance

TimescaleDB hypertables provide:
- Fast time-range queries
- Efficient compression for historical data
- Automatic data retention policies

### Caching Strategy

- **OHLCV Data**: Cached for 1 day (configurable)
- **Technical Indicators**: Cached with OHLCV data
- **Fundamental Data**: Cached for 30 days (less frequently updated)

## Best Practices

### 1. Initial Data Load
```bash
# Load comprehensive data for your watchlist
python load_data.py --tickers AAPL MSFT GOOGL AMZN NVDA --period max
```

### 2. Daily Updates
```bash
# Force refresh to get latest data
python load_data.py --tickers AAPL MSFT GOOGL --period 5d --force-refresh
```

### 3. Scheduled Updates
Use cron or systemd timers:
```bash
# Update daily at 6 PM (after market close)
0 18 * * 1-5 cd /path/to/stock-analyzer && python load_data.py --exchange NASDAQ --force-refresh
```

### 4. Bulk Loading
```bash
# Load entire exchange (may take several hours)
python load_data.py --exchange NASDAQ --period max

# Load in batches
python load_data.py --exchange NSE --top-n 50 --period max
```

## Data Quality

### Handling Missing Data
- Technical indicators may have `null` values for initial periods (e.g., first 200 days won't have SMA_200)
- Fundamental data depends on Yahoo Finance availability
- Some stocks may have incomplete historical data

### Validation
The system automatically:
- Validates data before storage
- Handles missing values gracefully
- Logs warnings for incomplete data

## Maintenance

### View Cache Information
```bash
python load_data.py --info
```

### Clear Cache
```bash
# Clear specific ticker
python load_data.py --clear --ticker AAPL

# Clear all cache
python load_data.py --clear
```

### Database Maintenance
```bash
# Check table sizes and indexes
python migrate_db.py --info

# Vacuum and analyze (PostgreSQL optimization)
psql -U stockuser -d stockdb -c "VACUUM ANALYZE;"
```

## Troubleshooting

### Issue: Technical indicators not calculating
**Solution**: Ensure you're loading daily data (`interval="1d"`). Technical indicators are only calculated for daily data.

### Issue: Fundamental data missing
**Solution**: Some stocks may not have fundamental data available from Yahoo Finance. Check the logs for specific errors.

### Issue: Database connection errors
**Solution**: Ensure TimescaleDB is running:
```bash
docker-compose up -d
```

### Issue: Slow loading times
**Solution**: 
- Reduce the number of concurrent workers in config
- Load in smaller batches
- Use `--no-indicators` or `--no-fundamentals` to speed up

## Future Enhancements

Potential additions:
1. **More Fundamental Metrics**: Cash flow, balance sheet items
2. **Additional Technical Indicators**: Ichimoku, Fibonacci levels, Volume Profile
3. **Sector/Industry Comparisons**: Store sector averages for comparison
4. **Real-time Data**: WebSocket support for live updates
5. **Data Quality Metrics**: Track data completeness and freshness
6. **Historical Fundamentals**: Store quarterly/annual historical fundamentals

## Related Documentation

- [TimescaleDB Setup](../backend/timescaledb-setup.md)
- [Data Flow](../backend/data-flow.md)
- [Loading Stock Data](./loading-stock-data.md)
- [API Examples](../backend/api-examples.md)

