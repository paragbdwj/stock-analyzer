# Stock Analyzer - Daily Stock Scanner

A powerful Python-based FastAPI application for automated daily stock scanning using technical and fundamental analysis. Scan entire stock exchanges for trading opportunities based on customizable criteria.

## 🚀 Features

### Core Capabilities
- **Data Acquisition**: Fetch daily OHLCV data for stocks from multiple exchanges (NSE, BSE, NASDAQ, NYSE)
- **Technical Analysis**: Calculate 15+ technical indicators including RSI, MACD, SMA, EMA, Bollinger Bands, ATR, ADX, Stochastic, and OBV
- **Fundamental Analysis**: Retrieve key metrics like P/E ratio, P/B ratio, Debt-to-Equity, Market Cap, and more
- **Smart Filtering**: Combine technical and fundamental criteria with AND/OR logic
- **TimescaleDB Storage**: High-performance time series database for market data
- **Parallel Processing**: Multi-threaded data fetching for optimal performance
- **RESTful API**: FastAPI-based endpoints for easy integration

### Technical Indicators
- **Moving Averages**: SMA (20, 50, 100, 200), EMA (12, 26, 50, 200)
- **Momentum**: RSI (Relative Strength Index)
- **Trend**: MACD (Moving Average Convergence Divergence)
- **Volatility**: Bollinger Bands, ATR (Average True Range)
- **Volume**: OBV (On-Balance Volume)
- **Strength**: ADX (Average Directional Index)
- **Oscillators**: Stochastic Oscillator

### Fundamental Metrics
- **Valuation**: P/E Ratio (Trailing & Forward), Price-to-Book
- **Financial Health**: Debt-to-Equity, Current Ratio
- **Market Data**: Market Cap, Beta, Dividend Yield
- **Company Info**: Sector, Industry

## 📋 Requirements

- Python 3.9+
- Virtual environment (venv)
- Internet connection for data fetching

## 🛠️ Installation

### 1. Clone or Navigate to the Project

```bash
cd /Users/paragbhardwaj/Documents/Projects/stock-market/stock-analyzer
```

### 2. Start TimescaleDB (Required)

**Option A: Using Docker (Recommended)**

```bash
# Start TimescaleDB container
docker-compose up -d

# Verify it's running
docker-compose ps
```

**Option B: Manual Installation**

See [TIMESCALEDB_SETUP.md](TIMESCALEDB_SETUP.md) for detailed instructions.

### 3. Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
# venv\Scripts\activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Initialize Database

```bash
# Set up database schema and hypertables
python init_db.py
```

### 6. Configure Environment (Optional)

For enhanced fundamental data using Financial Modeling Prep API:

```bash
# Create .env file
cp .env.example .env

# Edit .env and add your FMP API key (optional)
# Sign up at https://financialmodelingprep.com/developer/docs/
```

## 🚀 Quick Start

### Start the API Server

```bash
# Make sure virtual environment is activated
python run.py
```

The API will be available at:
- **API Base**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 📊 Data Flow (Database-First Architecture)

The system uses a **smart caching strategy** for optimal performance:

1. ✅ **Check TimescaleDB first** - Fast retrieval from database (50-100ms)
2. ✅ **Fallback to Yahoo Finance API** - If data not in DB or stale
3. ✅ **Auto-save to TimescaleDB** - All fetched data is cached automatically
4. ✅ **Verify data** - Confirms successful save before returning

**Example Flow:**
```
Request → Check DB → Found? → Return (fast ✓)
                  → Not Found → Fetch API → Save DB → Return
```

**Pre-load data for faster performance:**
```bash
# Load NSE stocks into database
python load_data.py --exchange NSE --top-n 30

# Load specific tickers
python load_data.py --tickers AAPL MSFT GOOGL RELIANCE.NS

# Check database contents
python load_data.py --info
```

**Benefits:**
- 🚀 Fast responses (DB-only after initial load)
- 💾 Automatic caching of all API calls
- 🔄 Configurable cache freshness (default: 1 day)
- 📈 Scales to thousands of stocks

See [Data Flow Documentation](references/data-flow.md) for detailed architecture.

### Using the Interactive API Documentation

1. Open http://localhost:8000/docs in your browser
2. Explore available endpoints
3. Test API calls directly from the browser

## 📚 API Endpoints

### Core Endpoints

#### 1. Scan Stocks
**POST** `/scan`

Scan stocks based on technical and fundamental filters.

**Example Request:**
```json
{
  "exchange": "NSE",
  "technical_filters": [
    {"field": "rsi", "operator": "<", "value": 30}
  ],
  "fundamental_filters": [
    {"field": "trailing_pe", "operator": "<", "value": 20}
  ],
  "filter_logic": "AND",
  "force_refresh": false
}
```

**Example Response:**
```json
{
  "timestamp": "2024-01-15T10:30:00",
  "exchange": "NSE",
  "total_scanned": 30,
  "total_matched": 5,
  "stocks": [
    {
      "ticker": "RELIANCE.NS",
      "current_price": 2450.50,
      "technical": {
        "rsi": 28.5,
        "sma_50": 2400.0,
        "sma_200": 2350.0
      },
      "fundamental": {
        "trailing_pe": 18.5,
        "market_cap": 1500000000000
      },
      "matched_filters": [
        "Technical: rsi < 30",
        "Fundamental: trailing_pe < 20"
      ]
    }
  ],
  "scan_duration_seconds": 45.5
}
```

#### 2. Analyze Single Stock
**GET** `/analyze/{ticker}`

Get detailed analysis for a specific stock.

```bash
curl http://localhost:8000/analyze/RELIANCE.NS
curl http://localhost:8000/analyze/AAPL?force_refresh=true
```

#### 3. Get Available Exchanges
**GET** `/exchanges`

List all supported exchanges.

#### 4. Get Tickers for Exchange
**GET** `/tickers/{exchange}`

Get list of tickers for a specific exchange.

```bash
curl http://localhost:8000/tickers/NSE
curl http://localhost:8000/tickers/NASDAQ?top_n=10
```

#### 5. Get Current Price
**GET** `/price/{ticker}`

Get current price for a ticker.

```bash
curl http://localhost:8000/price/RELIANCE.NS
```

#### 6. Cache Management
**GET** `/cache/info` - Get cache statistics  
**DELETE** `/cache/clear` - Clear all cached data  
**DELETE** `/cache/clear?ticker=RELIANCE.NS` - Clear specific ticker

## 🎯 Usage Examples

### Example 1: Find Oversold Stocks with Good Fundamentals

**Scan Criteria:**
- RSI < 30 (Oversold)
- P/E Ratio < 20 (Undervalued)
- Market Cap > 10 Billion

```json
{
  "exchange": "NSE",
  "technical_filters": [
    {"field": "rsi", "operator": "<", "value": 30}
  ],
  "fundamental_filters": [
    {"field": "trailing_pe", "operator": "<", "value": 20},
    {"field": "market_cap", "operator": ">", "value": 10000000000}
  ],
  "filter_logic": "AND"
}
```

### Example 2: Find Golden Cross Candidates

**Scan Criteria:**
- 50-day SMA > 200-day SMA (Golden Cross)
- RSI between 40-60 (Neutral momentum)

```json
{
  "exchange": "NASDAQ",
  "technical_filters": [
    {"field": "sma_50", "operator": ">", "value": 0},
    {"field": "rsi", "operator": ">", "value": 40},
    {"field": "rsi", "operator": "<", "value": 60}
  ],
  "filter_logic": "AND"
}
```

### Example 3: High Momentum Stocks

**Scan Criteria:**
- RSI > 70 (Overbought/Strong momentum)
- OR MACD > 0 (Bullish trend)

```json
{
  "exchange": "NYSE",
  "technical_filters": [
    {"field": "rsi", "operator": ">", "value": 70},
    {"field": "macd", "operator": ">", "value": 0}
  ],
  "filter_logic": "OR"
}
```

## 🔧 Configuration

Edit `config.json` to customize:

```json
{
  "default_exchange": "NSE",
  "database": {
    "host": "localhost",
    "port": 5432,
    "database": "stock_analyzer",
    "user": "postgres",
    "password": "postgres",
    "pool_size": 10,
    "max_overflow": 20
  },
  "data_storage": {
    "cache_days": 1,
    "compression": true
  },
  "technical_indicators": {
    "sma_periods": [20, 50, 100, 200],
    "ema_periods": [12, 26, 50, 200],
    "rsi_period": 14,
    "macd_fast": 12,
    "macd_slow": 26,
    "macd_signal": 9
  },
  "data_fetch": {
    "period": "1y",
    "interval": "1d",
    "max_workers": 10,
    "retry_attempts": 3,
    "retry_delay": 2
  }
}
```

## 📁 Project Structure

```
stock-analyzer/
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI application
│   ├── config.py                # Configuration management
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py            # API endpoints
│   ├── database/
│   │   ├── __init__.py
│   │   ├── connection.py        # TimescaleDB connection
│   │   └── models.py            # SQLAlchemy models
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py           # Pydantic models
│   ├── services/
│   │   ├── __init__.py
│   │   ├── data_service.py      # Data acquisition
│   │   ├── technical_service.py # Technical analysis
│   │   ├── fundamental_service.py # Fundamental analysis
│   │   └── scanner_service.py   # Stock scanning logic
│   └── utils/
│       ├── __init__.py
│       ├── logger.py            # Logging utilities
│       └── storage.py           # TimescaleDB storage manager
├── config.json                  # Configuration file
├── docker-compose.yml           # TimescaleDB container setup
├── init_db.py                   # Database initialization script
├── requirements.txt             # Python dependencies
├── run.py                       # Entry point script
├── README.md                    # This file
└── TIMESCALEDB_SETUP.md         # Database setup guide
```

## 🧪 Testing the API

### Using cURL

```bash
# Health check
curl http://localhost:8000/health

# List exchanges
curl http://localhost:8000/exchanges

# Get NSE tickers
curl http://localhost:8000/tickers/NSE

# Analyze a stock
curl http://localhost:8000/analyze/RELIANCE.NS

# Run a scan
curl -X POST http://localhost:8000/scan \
  -H "Content-Type: application/json" \
  -d '{
    "exchange": "NSE",
    "technical_filters": [
      {"field": "rsi", "operator": "<", "value": 30}
    ]
  }'
```

### Using Python

```python
import requests

# Scan for oversold stocks
response = requests.post('http://localhost:8000/scan', json={
    "exchange": "NSE",
    "technical_filters": [
        {"field": "rsi", "operator": "<", "value": 30}
    ],
    "fundamental_filters": [
        {"field": "trailing_pe", "operator": "<", "value": 20}
    ],
    "filter_logic": "AND"
})

result = response.json()
print(f"Found {result['total_matched']} stocks")

for stock in result['stocks']:
    print(f"{stock['ticker']}: Price={stock['current_price']}, RSI={stock['technical']['rsi']}")
```

## 📊 Available Filter Fields

### Technical Fields
- `rsi` - Relative Strength Index
- `sma_20`, `sma_50`, `sma_100`, `sma_200` - Simple Moving Averages
- `ema_12`, `ema_26`, `ema_50`, `ema_200` - Exponential Moving Averages
- `macd`, `macd_signal`, `macd_histogram` - MACD indicators
- `obv` - On-Balance Volume
- `atr` - Average True Range
- `adx` - Average Directional Index

### Fundamental Fields
- `trailing_pe` (or `pe`) - Trailing P/E Ratio
- `forward_pe` - Forward P/E Ratio
- `price_to_book` (or `pb`) - Price-to-Book Ratio
- `debt_to_equity` (or `de`) - Debt-to-Equity Ratio
- `current_ratio` - Current Ratio
- `market_cap` - Market Capitalization
- `beta` - Beta coefficient
- `dividend_yield` - Dividend Yield

### Operators
- `<` - Less than
- `>` - Greater than
- `<=` - Less than or equal to
- `>=` - Greater than or equal to
- `==` - Equal to
- `!=` - Not equal to

## 🔍 Supported Exchanges

- **NSE** (National Stock Exchange of India) - Suffix: `.NS`
- **BSE** (Bombay Stock Exchange) - Suffix: `.BO`
- **NASDAQ** - No suffix
- **NYSE** (New York Stock Exchange) - No suffix

## 🚀 Performance Tips

1. **Use TimescaleDB**: Optimized for time series data with automatic compression and indexing.
2. **Leverage Caching**: Data is cached in the database for 1 day by default.
3. **Limit Tickers**: Use the `tickers` parameter to scan specific stocks instead of entire exchanges.
4. **Parallel Processing**: The system uses multi-threading. Adjust `max_workers` in config for your system.
5. **Filter Early**: Combine filters with AND logic to reduce processing.
6. **Connection Pooling**: TimescaleDB uses connection pooling for better performance.

## 🔐 Security Notes

- In production, update CORS settings in `app/main.py`
- Add authentication/authorization as needed
- Rate limit API endpoints for public deployment
- Secure your FMP API key (don't commit to git)

## 📝 Development

### Adding New Indicators

1. Edit `app/services/technical_service.py`
2. Add calculation in `calculate_indicators()`
3. Update `TechnicalIndicators` model in `app/models/schemas.py`
4. Add field mapping in `_get_field_value()` in `scanner_service.py`

### Adding New Exchanges

1. Update `config.json` with exchange info
2. Add ticker fetching logic in `data_service.py`

## 🐛 Troubleshooting

**Issue**: "No module named 'app'"  
**Solution**: Make sure you're in the project directory and virtual environment is activated.

**Issue**: Database connection failed  
**Solution**: Make sure TimescaleDB is running: `docker-compose up -d`

**Issue**: Rate limiting from Yahoo Finance  
**Solution**: Reduce `max_workers` in config or increase delay between requests.

**Issue**: Missing data for a ticker  
**Solution**: Verify ticker symbol is correct (check exchange suffix). Try with `force_refresh=true`.

**Issue**: Slow scanning  
**Solution**: Check database connection, reduce scan scope, or increase `max_workers`.

**Issue**: Database out of memory  
**Solution**: Enable compression (automatic), add retention policy, or increase database resources.

## 📄 License

This project is provided as-is for educational and personal use.

## 🙏 Acknowledgments

- **yfinance** - Yahoo Finance data
- **pandas-ta** - Technical analysis indicators
- **FastAPI** - Modern Python web framework
- **TimescaleDB** - High-performance time series database
- **Financial Modeling Prep** - Fundamental data API

## 📧 Support

For issues and questions, please check:
1. The interactive API docs at `/docs`
2. Configuration in `config.json`
3. Logs for error messages

---

**Happy Trading! 📈**

*Disclaimer: This tool is for informational purposes only. Always do your own research before making investment decisions.*
