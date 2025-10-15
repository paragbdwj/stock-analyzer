# Enhanced Data Storage - Quick Start Guide

## What's New? 🎉

Your stock analyzer now stores **20 years of historical data** along with **fundamental metrics** and **technical indicators** automatically!

## Summary of Changes

### 1. **Default Period Changed to 20 Years**
- Previous default: 1 year
- New default: 20 years (or `max` available data)
- Get the most comprehensive historical data by default

### 2. **Fundamental Data Stored**
Now automatically saves company fundamentals like:
- P/E Ratio, P/B Ratio, Market Cap
- Debt to Equity, Current Ratio
- Profit Margin, ROE, ROA
- Revenue Growth, Earnings Growth
- Beta, Dividend Yield
- Sector and Industry

### 3. **Technical Indicators Stored**
Automatically calculates and saves indicators for each trading day:
- **Moving Averages**: SMA (20, 50, 100, 200), EMA (12, 26, 50, 200)
- **Momentum**: RSI, MACD, Stochastic
- **Volatility**: ATR, Bollinger Bands
- **Volume**: OBV, Volume SMA
- **Trend**: ADX, Directional Indicators
- **Returns**: Daily Returns, Cumulative Returns

## Quick Start

### Step 1: Run Database Migration
```bash
python migrate_db.py
```

This creates two new tables:
- `stock_fundamentals` - Stores fundamental metrics
- `stock_technical_indicators` - Stores technical indicators (as TimescaleDB hypertable)

### Step 2: Load Data with All Features
```bash
# Load specific stocks with 20 years of data + indicators + fundamentals
python load_data.py --tickers AAPL MSFT GOOGL

# Load NSE top 30 stocks
python load_data.py --exchange NSE --top-n 30

# Load with maximum available data
python load_data.py --tickers RELIANCE.NS --period max
```

### Step 3: Verify Data
```bash
# Check what's in the database
python load_data.py --info
```

## Usage Examples

### Load Everything (Default Behavior)
```bash
python load_data.py --tickers AAPL
# ✓ 20 years of OHLCV data
# ✓ Technical indicators calculated
# ✓ Fundamental data fetched
```

### Load Only Price Data
```bash
python load_data.py --tickers AAPL --no-indicators --no-fundamentals
# ✓ Only OHLCV data, faster loading
```

### Load Different Time Periods
```bash
# 5 years of data
python load_data.py --tickers AAPL --period 5y

# All available data (might be 30+ years!)
python load_data.py --tickers AAPL --period max

# Last 6 months
python load_data.py --tickers AAPL --period 6mo
```

### Bulk Loading
```bash
# Load an entire exchange
python load_data.py --exchange NASDAQ --top-n 50

# Load multiple specific stocks
python load_data.py --tickers AAPL MSFT GOOGL AMZN TSLA NVDA META
```

## Programmatic Usage

```python
from app.services.data_service import DataService
from app.utils.storage import StorageManager

# Initialize services
data_service = DataService()
storage = StorageManager()

# Fetch data with all features
data = data_service.fetch_stock_data(
    ticker="AAPL",
    period="20y",
    include_indicators=True,
    include_fundamentals=True
)

# Load fundamental data
fundamentals = storage.load_fundamental_data("AAPL")
print(f"P/E Ratio: {fundamentals['trailing_pe']}")
print(f"Market Cap: ${fundamentals['market_cap']:,}")
print(f"Beta: {fundamentals['beta']}")

# Load technical indicators
indicators = storage.load_technical_indicators("AAPL")
print(f"Latest RSI: {indicators['rsi'].iloc[-1]:.2f}")
print(f"Latest SMA 50: ${indicators['sma_50'].iloc[-1]:.2f}")
print(f"Latest MACD: {indicators['macd'].iloc[-1]:.4f}")

# Load OHLCV data
prices = storage.load_stock_data("AAPL")
print(f"Latest Close: ${prices['Close'].iloc[-1]:.2f}")
```

## Command Line Options

```bash
# Get help
python load_data.py --help

# Available options:
--exchange NSE|BSE|NASDAQ|NYSE   # Load all stocks from exchange
--top-n N                        # Limit to top N stocks
--tickers AAPL MSFT ...          # Load specific tickers
--period 1y|5y|10y|20y|max       # Time period (default: 20y)
--force-refresh                  # Force refresh existing data
--no-indicators                  # Skip technical indicators
--no-fundamentals                # Skip fundamental data
--info                           # Show cache information
--clear [--ticker AAPL]          # Clear cache
```

## Performance Notes

### Storage Requirements
- **Per stock (20 years)**: ~1 MB total
  - OHLCV: ~200 KB
  - Technical Indicators: ~750 KB
  - Fundamentals: ~300 bytes
- **100 stocks**: ~100 MB
- **1000 stocks**: ~1 GB

### Loading Times (Approximate)
- **Single stock with all features**: 2-5 seconds
- **10 stocks**: 10-20 seconds (parallel loading)
- **100 stocks**: 2-5 minutes
- **1000 stocks**: 30-60 minutes

Tips for faster loading:
- Use `--no-indicators` for 50% speed boost
- Use `--no-fundamentals` for 20% speed boost
- Reduce `--period` for faster initial loads

## What Values Are Stored?

### Fundamental Metrics (30+ fields)
- **Valuation**: P/E, P/B, P/S, PEG Ratio
- **Financial Health**: Debt to Equity, Current Ratio, Quick Ratio
- **Profitability**: Profit Margin, Operating Margin, ROE, ROA
- **Growth**: Revenue Growth, Earnings Growth
- **Dividends**: Dividend Yield, Payout Ratio
- **Risk**: Beta
- **Company Info**: Sector, Industry, Market Cap, Enterprise Value

### Technical Indicators (25+ fields per day)
- **Moving Averages**: SMA (20, 50, 100, 200), EMA (12, 26, 50, 200)
- **Momentum**: RSI, MACD (with signal & histogram), Stochastic K & D
- **Volatility**: ATR, Bollinger Bands (upper, middle, lower), 20-day volatility
- **Volume**: OBV, Volume SMA
- **Trend**: ADX, DI+, DI-
- **Returns**: Daily Return, Cumulative Return

## Maintenance

### Daily Updates
```bash
# Update your watchlist daily
python load_data.py --tickers AAPL MSFT GOOGL --period 5d --force-refresh
```

### Weekly Updates
```bash
# Refresh fundamentals weekly
python load_data.py --exchange NASDAQ --top-n 30 --force-refresh
```

### Check Database
```bash
# View database stats
python load_data.py --info

# View table information
python migrate_db.py --info
```

## Troubleshooting

### Database not running?
```bash
docker-compose up -d
```

### Migration errors?
```bash
# Check database connection
python -c "from app.database.connection import check_connection; print('OK' if check_connection() else 'Failed')"
```

### Want to start fresh?
```bash
# Clear all cached data
python load_data.py --clear
```

## Next Steps

1. **Run the migration**: `python migrate_db.py`
2. **Load your watchlist**: `python load_data.py --tickers YOUR_STOCKS`
3. **Explore the data**: Use StorageManager to query fundamentals and indicators
4. **Build features**: Use the comprehensive data for analysis and strategy backtesting

## Full Documentation

See `references/scripts/enhanced-data-storage.md` for complete documentation including:
- Detailed schema information
- API integration examples
- Performance optimization tips
- Future enhancement roadmap

---

**Need Help?** Check the logs in `logs/` directory for detailed information about data loading and any errors.

