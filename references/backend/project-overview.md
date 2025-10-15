# Stock Analyzer - Project Overview

## Architecture

The Stock Analyzer is built using a modular, service-oriented architecture with FastAPI as the web framework.

```
┌─────────────────────────────────────────────────────────┐
│                    FastAPI Application                   │
│                      (app/main.py)                       │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                    API Routes Layer                      │
│                   (app/api/routes.py)                    │
│                                                          │
│  Endpoints:                                              │
│  • POST /scan - Main scanning endpoint                  │
│  • GET /analyze/{ticker} - Single stock analysis         │
│  • GET /exchanges - List exchanges                       │
│  • GET /tickers/{exchange} - Get tickers                 │
│  • Cache management, health check, etc.                  │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                   Service Layer                          │
│                (app/services/)                           │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │  ScannerService (scanner_service.py)             │   │
│  │  - Orchestrates the entire scanning process     │   │
│  │  - Applies filters and combines results          │   │
│  └──────────┬─────────────────────┬──────────────────┘  │
│             │                     │                      │
│  ┌──────────▼──────────┐ ┌───────▼──────────────────┐   │
│  │  DataService        │ │  TechnicalService        │   │
│  │  (data_service.py)  │ │  (technical_service.py)  │   │
│  │                     │ │                          │   │
│  │  • Fetch OHLCV data │ │  • Calculate RSI         │   │
│  │  • Yahoo Finance    │ │  • Calculate MACD        │   │
│  │  • Cache management │ │  • Calculate SMA/EMA     │   │
│  │  • Parallel fetch   │ │  • Bollinger Bands       │   │
│  └─────────────────────┘ │  • ATR, ADX, Stochastic  │   │
│                          └──────────────────────────┘   │
│  ┌───────────────────────────────────────────────────┐   │
│  │  FundamentalService (fundamental_service.py)      │   │
│  │                                                   │   │
│  │  • Fetch P/E, P/B, Debt/Equity                   │   │
│  │  • Market Cap, Sector, Industry                   │   │
│  │  • Optional FMP API integration                   │   │
│  └───────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                  Utilities Layer                         │
│                  (app/utils/)                            │
│                                                          │
│  • StorageManager (storage.py) - Local data caching     │
│  • Logger (logger.py) - Logging with color output       │
└─────────────────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                  Data Storage                            │
│                  (data/stocks/)                          │
│                                                          │
│  • Parquet/CSV files for each ticker                    │
│  • Metadata tracking (last update, size, etc.)          │
└─────────────────────────────────────────────────────────┘
```

## Data Flow

### 1. Scan Request Flow

```
User Request (POST /scan)
    ↓
API Route Handler
    ↓
ScannerService.scan_stocks()
    ↓
DataService.fetch_multiple_stocks()
    ├─→ Check cache (StorageManager)
    │   ├─→ If cached & fresh: Return cached data
    │   └─→ If not cached/stale: Fetch from Yahoo Finance
    │       └─→ Save to cache
    ↓
For each stock:
    ├─→ TechnicalService.calculate_indicators()
    │   └─→ Returns DataFrame with all indicators
    ├─→ TechnicalService.get_latest_indicators()
    │   └─→ Returns TechnicalIndicators object
    └─→ FundamentalService.get_fundamental_data()
        └─→ Returns FundamentalData object
    ↓
ScannerService._check_filters()
    ├─→ Apply technical filters
    ├─→ Apply fundamental filters
    └─→ Combine with AND/OR logic
    ↓
Return matched stocks as ScanResult
```

### 2. Individual Analysis Flow

```
User Request (GET /analyze/{ticker})
    ↓
API Route Handler
    ↓
ScannerService.get_stock_analysis()
    ├─→ DataService.fetch_stock_data()
    ├─→ TechnicalService.calculate_indicators()
    ├─→ TechnicalService.get_latest_indicators()
    └─→ FundamentalService.get_fundamental_data()
    ↓
Return StockInfo object
```

## Key Components

### 1. Configuration Management (config.py)

- Loads settings from `config.json`
- Manages environment variables from `.env`
- Provides centralized access to all configuration

**Key Settings:**
- Exchange configurations
- Technical indicator parameters
- Data fetch settings (workers, retries, etc.)
- Storage settings (type, path, cache duration)

### 2. Data Models (models/schemas.py)

Pydantic models for type safety and validation:

- **StockData**: OHLCV data structure
- **TechnicalIndicators**: All technical indicators
- **FundamentalData**: Fundamental metrics
- **FilterRule**: Filter definition
- **ScanRequest**: Scan parameters
- **ScanResult**: Scan results
- **StockInfo**: Combined stock information

### 3. Services

#### DataService
- **Purpose**: Fetch and manage stock price data
- **Data Source**: Yahoo Finance (via yfinance)
- **Features**:
  - Parallel data fetching (ThreadPoolExecutor)
  - Automatic retry logic
  - Local caching for performance
  - Exchange ticker management

#### TechnicalService
- **Purpose**: Calculate technical indicators
- **Library**: pandas-ta
- **Indicators**:
  - Moving Averages (SMA, EMA)
  - Momentum (RSI)
  - Trend (MACD)
  - Volatility (Bollinger Bands, ATR)
  - Volume (OBV)
  - Strength (ADX)
  - Oscillators (Stochastic)

#### FundamentalService
- **Purpose**: Fetch fundamental data
- **Data Sources**:
  - Primary: Yahoo Finance (yfinance)
  - Optional: Financial Modeling Prep API
- **Metrics**:
  - Valuation ratios (P/E, P/B)
  - Financial health (Debt/Equity, Current Ratio)
  - Market data (Market Cap, Beta)
  - Company info (Sector, Industry)

#### ScannerService
- **Purpose**: Orchestrate scanning and filtering
- **Functions**:
  - Coordinate all services
  - Apply filter logic (AND/OR)
  - Combine technical and fundamental criteria
  - Generate scan results

### 4. Storage Manager (utils/storage.py)

- **Purpose**: Local data caching
- **Formats**: Parquet (default) or CSV
- **Features**:
  - Metadata tracking
  - Cache freshness checking
  - Cache management (clear, info)
  - Automatic cache invalidation

### 5. API Layer (api/routes.py)

RESTful endpoints built with FastAPI:

**Core Endpoints:**
- `/scan` - Main scanning endpoint
- `/analyze/{ticker}` - Single stock analysis
- `/exchanges` - List exchanges
- `/tickers/{exchange}` - Get tickers

**Utility Endpoints:**
- `/health` - Health check
- `/price/{ticker}` - Current price
- `/cache/info` - Cache statistics
- `/cache/clear` - Clear cache

## Technology Stack

### Core Framework
- **FastAPI**: Modern Python web framework
  - Automatic API documentation
  - Type validation with Pydantic
  - High performance (async support)
  - OpenAPI standard

### Data Processing
- **pandas**: DataFrame operations
- **numpy**: Numerical computations
- **pyarrow**: Parquet file format support

### Financial Data
- **yfinance**: Yahoo Finance data (free, no API key)
- **pandas-ta**: Technical analysis indicators
- **fundamentalanalysis**: FMP API wrapper (optional)

### Server
- **uvicorn**: ASGI server
- **python-dotenv**: Environment variable management

### Utilities
- **requests/aiohttp**: HTTP clients
- **tqdm**: Progress bars
- **colorlog**: Colored logging

## Performance Optimizations

### 1. Local Caching
- **Problem**: Repeated API calls are slow and may hit rate limits
- **Solution**: Cache data locally in Parquet format
- **Benefit**: 10-100x faster for cached data

### 2. Parallel Processing
- **Problem**: Sequential API calls for multiple stocks are slow
- **Solution**: ThreadPoolExecutor with configurable workers
- **Benefit**: N-times faster (where N = number of workers)

### 3. Data Format
- **Format**: Parquet instead of CSV
- **Benefit**: Faster read/write, smaller file size, preserves data types

### 4. Smart Filtering
- **Approach**: Filter during processing, not after
- **Benefit**: Reduces memory usage and processing time

## Configuration

### config.json Structure

```json
{
  "exchanges": {
    "NSE": {"suffix": ".NS", "description": "..."},
    ...
  },
  "default_exchange": "NSE",
  "data_storage": {
    "type": "parquet",
    "path": "data/stocks",
    "cache_days": 1
  },
  "technical_indicators": {
    "sma_periods": [20, 50, 100, 200],
    "ema_periods": [12, 26, 50, 200],
    "rsi_period": 14,
    ...
  },
  "data_fetch": {
    "period": "1y",
    "interval": "1d",
    "max_workers": 10,
    "retry_attempts": 3,
    "retry_delay": 2
  },
  "api": {
    "host": "0.0.0.0",
    "port": 8000,
    "reload": true
  }
}
```

## Extensibility

### Adding New Indicators

1. Add calculation in `TechnicalService.calculate_indicators()`
2. Update `TechnicalIndicators` model
3. Add field mapping in `ScannerService._get_field_value()`

### Adding New Exchanges

1. Add exchange config to `config.json`
2. Implement ticker fetching in `DataService.get_exchange_tickers()`

### Adding New Data Sources

1. Create new service class (e.g., `AlternativeDataService`)
2. Add to `ScannerService` initialization
3. Update models for new data fields
4. Update filter logic to handle new fields

## Error Handling

### Levels of Error Handling

1. **Service Level**: Try-except blocks, logging, graceful degradation
2. **API Level**: HTTPException for client errors, 500 for server errors
3. **Data Level**: Validation with Pydantic, None for missing data
4. **Network Level**: Retry logic, timeouts, fallbacks

### Example: Missing Data Handling

```python
# Technical indicators may be NaN for recent data
if value is not None and pd.notna(value):
    return float(value)
return None
```

## Testing the Application

### 1. Manual Testing
- Use Swagger UI: http://localhost:8000/docs
- Use example script: `python examples/example_usage.py`

### 2. API Testing
- cURL commands
- Postman collections
- Python requests library

### 3. Performance Testing
- Time scan operations
- Monitor cache hit rates
- Check parallel processing efficiency

## Security Considerations

### Current Implementation
- CORS: Allow all origins (development mode)
- No authentication (local use)
- API key in .env (not committed)

### Production Recommendations
1. Restrict CORS origins
2. Add authentication (JWT, API keys)
3. Rate limiting
4. HTTPS only
5. Input validation (already done with Pydantic)
6. Logging and monitoring

## Future Enhancements

### Potential Features
1. **Database Integration**: PostgreSQL/MongoDB for historical scans
2. **WebSocket Support**: Real-time price updates
3. **Backtesting**: Test strategies on historical data
4. **Alerts**: Email/SMS notifications for matches
5. **Scheduling**: Automated daily scans
6. **Charting**: Generate technical charts
7. **Portfolio Tracking**: Track selected stocks
8. **Machine Learning**: Predictive models

### Scalability Improvements
1. **Async Data Fetching**: Replace ThreadPoolExecutor with asyncio
2. **Redis Caching**: Distributed cache for multiple instances
3. **Message Queue**: For long-running scans
4. **Containerization**: Docker deployment
5. **Horizontal Scaling**: Multiple API instances

## Development Workflow

### 1. Setup
```bash
make setup  # or ./setup.sh
source venv/bin/activate
```

### 2. Development
```bash
python run.py  # Start server with auto-reload
```

### 3. Testing
- Test endpoints at http://localhost:8000/docs
- Run example script: `python examples/example_usage.py`

### 4. Deployment
- Configure production settings in `config.json`
- Update CORS and security settings
- Use production ASGI server (Gunicorn + Uvicorn)

## Troubleshooting

### Common Issues

**Slow Scans**
- Increase `max_workers` in config
- Use smaller ticker lists
- Enable caching

**Missing Data**
- Check ticker symbol format
- Verify exchange suffix
- Try `force_refresh=true`

**Rate Limiting**
- Reduce `max_workers`
- Increase `retry_delay`
- Enable caching

**Import Errors**
- Activate virtual environment
- Reinstall dependencies: `pip install -r requirements.txt`

## Contributing

### Code Style
- Follow PEP 8
- Type hints for function signatures
- Docstrings for all public functions
- Modular, single-responsibility functions

### Adding Features
1. Create feature branch
2. Implement in appropriate service
3. Update models if needed
4. Add API endpoint if needed
5. Update documentation
6. Test thoroughly

---

For detailed API examples, see [API_EXAMPLES.md](API_EXAMPLES.md)  
For quick start guide, see [QUICK_START.md](QUICK_START.md)  
For full documentation, see [README.md](README.md)

