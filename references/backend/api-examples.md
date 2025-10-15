# API Examples

Comprehensive examples for using the Stock Analyzer API.

## Table of Contents
- [Getting Started](#getting-started)
- [Technical Analysis Scans](#technical-analysis-scans)
- [Fundamental Analysis Scans](#fundamental-analysis-scans)
- [Combined Scans](#combined-scans)
- [Individual Stock Analysis](#individual-stock-analysis)
- [Utility Endpoints](#utility-endpoints)

## Getting Started

Make sure the API server is running:
```bash
python run.py
```

All examples use the base URL: `http://localhost:8000`

## Technical Analysis Scans

### 1. Find Oversold Stocks (RSI < 30)

**Purpose**: Identify potentially oversold stocks that may rebound

```json
POST /scan
{
  "exchange": "NSE",
  "technical_filters": [
    {"field": "rsi", "operator": "<", "value": 30}
  ]
}
```

### 2. Find Overbought Stocks (RSI > 70)

**Purpose**: Identify potentially overbought stocks

```json
POST /scan
{
  "exchange": "NASDAQ",
  "technical_filters": [
    {"field": "rsi", "operator": ">", "value": 70}
  ]
}
```

### 3. Golden Cross Pattern

**Purpose**: Find stocks where 50-day SMA is above 200-day SMA (bullish signal)

```json
POST /scan
{
  "exchange": "NSE",
  "tickers": ["RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS"],
  "technical_filters": [
    {"field": "sma_50", "operator": ">", "value": 0},
    {"field": "sma_200", "operator": ">", "value": 0}
  ],
  "filter_logic": "AND"
}
```

### 4. MACD Bullish Trend

**Purpose**: Find stocks with positive MACD (bullish momentum)

```json
POST /scan
{
  "exchange": "NYSE",
  "technical_filters": [
    {"field": "macd", "operator": ">", "value": 0},
    {"field": "macd_histogram", "operator": ">", "value": 0}
  ],
  "filter_logic": "AND"
}
```

### 5. Strong Momentum with Healthy RSI

**Purpose**: Find stocks with strong upward momentum but not overbought

```json
POST /scan
{
  "exchange": "NSE",
  "technical_filters": [
    {"field": "rsi", "operator": ">", "value": 50},
    {"field": "rsi", "operator": "<", "value": 70},
    {"field": "macd", "operator": ">", "value": 0}
  ],
  "filter_logic": "AND"
}
```

## Fundamental Analysis Scans

### 1. Value Stocks (Low P/E)

**Purpose**: Find undervalued stocks based on P/E ratio

```json
POST /scan
{
  "exchange": "NSE",
  "fundamental_filters": [
    {"field": "trailing_pe", "operator": "<", "value": 15},
    {"field": "trailing_pe", "operator": ">", "value": 0}
  ],
  "filter_logic": "AND"
}
```

### 2. Growth Stocks (High P/E but good metrics)

**Purpose**: Find growth stocks with reasonable fundamentals

```json
POST /scan
{
  "exchange": "NASDAQ",
  "tickers": ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA"],
  "fundamental_filters": [
    {"field": "trailing_pe", "operator": ">", "value": 20},
    {"field": "market_cap", "operator": ">", "value": 100000000000}
  ],
  "filter_logic": "AND"
}
```

### 3. Large Cap Stocks

**Purpose**: Find large-cap companies (Market Cap > $10B)

```json
POST /scan
{
  "exchange": "NYSE",
  "fundamental_filters": [
    {"field": "market_cap", "operator": ">", "value": 10000000000}
  ]
}
```

### 4. Financially Healthy Companies

**Purpose**: Find companies with good debt ratios

```json
POST /scan
{
  "exchange": "NSE",
  "fundamental_filters": [
    {"field": "debt_to_equity", "operator": "<", "value": 1},
    {"field": "current_ratio", "operator": ">", "value": 1.5}
  ],
  "filter_logic": "AND"
}
```

## Combined Scans

### 1. Oversold Value Stocks

**Purpose**: Find oversold stocks that are also undervalued

```json
POST /scan
{
  "exchange": "NSE",
  "technical_filters": [
    {"field": "rsi", "operator": "<", "value": 35}
  ],
  "fundamental_filters": [
    {"field": "trailing_pe", "operator": "<", "value": 20},
    {"field": "trailing_pe", "operator": ">", "value": 0},
    {"field": "market_cap", "operator": ">", "value": 50000000000}
  ],
  "filter_logic": "AND"
}
```

### 2. Quality Growth Stocks

**Purpose**: Find stocks with good momentum and fundamentals

```json
POST /scan
{
  "exchange": "NASDAQ",
  "technical_filters": [
    {"field": "rsi", "operator": ">", "value": 45},
    {"field": "rsi", "operator": "<", "value": 65},
    {"field": "macd", "operator": ">", "value": 0}
  ],
  "fundamental_filters": [
    {"field": "market_cap", "operator": ">", "value": 10000000000},
    {"field": "debt_to_equity", "operator": "<", "value": 2}
  ],
  "filter_logic": "AND"
}
```

### 3. Turnaround Candidates

**Purpose**: Find oversold large-cap stocks with decent fundamentals

```json
POST /scan
{
  "exchange": "NSE",
  "technical_filters": [
    {"field": "rsi", "operator": "<", "value": 40}
  ],
  "fundamental_filters": [
    {"field": "market_cap", "operator": ">", "value": 100000000000},
    {"field": "debt_to_equity", "operator": "<", "value": 1.5},
    {"field": "current_ratio", "operator": ">", "value": 1}
  ],
  "filter_logic": "AND"
}
```

### 4. Momentum + Value

**Purpose**: Find stocks with upward momentum and low P/E

```json
POST /scan
{
  "exchange": "NSE",
  "technical_filters": [
    {"field": "rsi", "operator": ">", "value": 50},
    {"field": "macd", "operator": ">", "value": 0}
  ],
  "fundamental_filters": [
    {"field": "trailing_pe", "operator": "<", "value": 18},
    {"field": "trailing_pe", "operator": ">", "value": 5}
  ],
  "filter_logic": "AND"
}
```

## Individual Stock Analysis

### Analyze a Single Stock

```bash
GET /analyze/RELIANCE.NS
```

**Response includes:**
- Current price
- All technical indicators (RSI, MACD, SMA, EMA, etc.)
- Fundamental data (P/E, P/B, Debt/Equity, Market Cap, Sector)

### Get Current Price

```bash
GET /price/RELIANCE.NS
```

## Utility Endpoints

### List Available Exchanges

```bash
GET /exchanges
```

### Get Tickers for an Exchange

```bash
GET /tickers/NSE
GET /tickers/NASDAQ?top_n=20
```

### Cache Management

```bash
# Get cache information
GET /cache/info

# Clear all cache
DELETE /cache/clear

# Clear specific ticker
DELETE /cache/clear?ticker=RELIANCE.NS
```

### Health Check

```bash
GET /health
```

## Advanced Examples

### Custom Ticker List Scan

**Purpose**: Scan only specific stocks you're interested in

```json
POST /scan
{
  "exchange": "NSE",
  "tickers": [
    "RELIANCE.NS",
    "TCS.NS",
    "INFY.NS",
    "HDFCBANK.NS",
    "ICICIBANK.NS"
  ],
  "technical_filters": [
    {"field": "rsi", "operator": "<", "value": 40}
  ],
  "fundamental_filters": [
    {"field": "trailing_pe", "operator": "<", "value": 25}
  ],
  "filter_logic": "AND",
  "force_refresh": false
}
```

### OR Logic Example

**Purpose**: Find stocks that match ANY of the criteria

```json
POST /scan
{
  "exchange": "NSE",
  "technical_filters": [
    {"field": "rsi", "operator": "<", "value": 30},
    {"field": "rsi", "operator": ">", "value": 70}
  ],
  "filter_logic": "OR"
}
```

This finds stocks that are either oversold OR overbought.

### Force Refresh

**Purpose**: Force fresh data download (ignore cache)

```json
POST /scan
{
  "exchange": "NASDAQ",
  "tickers": ["AAPL", "MSFT"],
  "technical_filters": [
    {"field": "rsi", "operator": ">", "value": 50}
  ],
  "force_refresh": true
}
```

## Tips & Best Practices

### 1. Use Specific Ticker Lists
Instead of scanning entire exchanges, use specific ticker lists for faster results:
```json
{
  "exchange": "NSE",
  "tickers": ["STOCK1.NS", "STOCK2.NS", "STOCK3.NS"],
  ...
}
```

### 2. Combine Multiple Conditions
Use multiple filters to narrow down results:
```json
{
  "technical_filters": [
    {"field": "rsi", "operator": ">", "value": 40},
    {"field": "rsi", "operator": "<", "value": 60}
  ],
  "filter_logic": "AND"
}
```

### 3. Leverage Caching
- First scan downloads data (slow)
- Subsequent scans use cache (fast)
- Cache is valid for 1 day (configurable)
- Use `force_refresh: false` for speed

### 4. Start Simple
Begin with one or two filters, then add more:
```json
{
  "exchange": "NSE",
  "technical_filters": [
    {"field": "rsi", "operator": "<", "value": 30}
  ]
}
```

### 5. Use Field Aliases
These are equivalent:
- `trailing_pe` = `pe`
- `price_to_book` = `pb`
- `debt_to_equity` = `de`

## Common Filter Combinations

| Strategy | Technical Filters | Fundamental Filters |
|----------|------------------|---------------------|
| **Value Investing** | None or RSI < 40 | P/E < 15, Debt/Equity < 1 |
| **Momentum Trading** | RSI > 60, MACD > 0 | Market Cap > 1B |
| **Contrarian** | RSI < 30 | P/E < 20, Current Ratio > 1.5 |
| **Growth** | RSI > 50, MACD > 0 | P/E > 20, Market Cap > 10B |
| **Income** | RSI 40-60 | Dividend Yield > 3%, Debt/Equity < 1 |

## Error Handling

### Handle Missing Data
Some stocks may not have all fundamental data:
```json
{
  "fundamental_filters": [
    {"field": "trailing_pe", "operator": ">", "value": 0},
    {"field": "trailing_pe", "operator": "<", "value": 50}
  ]
}
```

This excludes stocks with negative or missing P/E ratios.

## Interactive Testing

For easiest testing, use the **Swagger UI**:
1. Open http://localhost:8000/docs
2. Click on any endpoint
3. Click "Try it out"
4. Fill in the request body
5. Click "Execute"
6. View the response

---

For more information, see the [README.md](README.md) or visit http://localhost:8000/docs

