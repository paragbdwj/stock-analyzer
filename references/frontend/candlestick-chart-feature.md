# Candlestick Chart Feature

This document describes the candlestick price chart feature added to the Stock Analyzer UI.

## Overview

The candlestick chart displays historical OHLC (Open, High, Low, Close) price data with volume information and summary statistics. It uses **Recharts**, a popular open-source React charting library.

## Features

### 📊 Chart Components

1. **Price Chart (Area + Line)**
   - Blue area chart showing price movement trend
   - Line chart with close prices
   - Custom dots representing OHLC candlesticks
   - Tooltip showing detailed OHLC data for each date

2. **Volume Chart**
   - Bar chart showing trading volume
   - Displayed in millions (M) for readability
   - Positioned below the price chart

3. **Summary Statistics**
   - Period High (highest price in selected period)
   - Period Low (lowest price in selected period)
   - Average Volume
   - Period Change (percentage change from start to end)

### 🎨 Visual Design

- **Green** indicators for price increases (close > open)
- **Red** indicators for price decreases (close < open)
- **Blue** area fill for overall trend visualization
- Responsive layout that adapts to screen size
- Automatic X-axis label rotation for longer periods

### 📅 Date Display

The chart automatically formats dates based on the data range:
- **≤ 6 months**: Shows "MMM DD" (e.g., "Jan 15")
- **> 6 months**: Shows "MMM DD, YYYY" (e.g., "Jan 15, 2024")
- **Smart label spacing**: Shows 10-15 labels regardless of data points

## Backend API

### New Endpoint: `/history/{ticker}`

Fetches historical OHLC data for a ticker.

**Request:**
```http
GET /history/RELIANCE.NS?period=1y&interval=1d&use_cache=true
```

**Parameters:**
- `ticker` (path): Stock ticker symbol
- `period` (query): Time period - `1d`, `5d`, `1mo`, `3mo`, `6mo`, `1y`, `2y`, `5y`, `10y`, `ytd`, `max` (default: `1y`)
- `interval` (query): Data interval - `1d`, `1wk`, `1mo` (default: `1d`)
- `use_cache` (query): Use cached data if available (default: `true`)

**Response:**
```json
{
  "ticker": "RELIANCE.NS",
  "period": "1y",
  "interval": "1d",
  "total_records": 252,
  "data": [
    {
      "date": "2024-10-14T00:00:00",
      "open": 2850.50,
      "high": 2875.00,
      "low": 2840.25,
      "close": 2865.75,
      "volume": 5234567,
      "adj_close": 2865.75
    }
    // ... more records
  ]
}
```

## Frontend Implementation

### Components Created

#### 1. `CandlestickChart.tsx`
Location: `/frontend/components/CandlestickChart.tsx`

A reusable React component that renders the price chart with volume.

**Props:**
```typescript
interface CandlestickChartProps {
  data: OHLCData[];      // Historical OHLC data
  ticker: string;         // Stock ticker symbol
  period?: string;        // Display period label (e.g., "1Y")
}
```

**Features:**
- Custom tooltip with OHLC details
- Automatic price range calculation
- Volume chart integration
- Summary statistics
- Responsive design

### API Client Updates

#### New Method: `getHistoricalData()`
Location: `/frontend/lib/api.ts`

```typescript
async getHistoricalData(
  ticker: string,
  period: string = '1y',
  interval: string = '1d',
  useCache: boolean = true
): Promise<HistoricalDataResponse>
```

**New Types:**
```typescript
interface OHLCData {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  adj_close?: number;
}

interface HistoricalDataResponse {
  ticker: string;
  period: string;
  interval: string;
  data: OHLCData[];
  total_records: number;
}
```

### Analyzer Page Updates

Location: `/frontend/app/analyzer/page.tsx`

**Changes:**
1. Added state for historical data
2. Fetches both stock info and historical data in parallel
3. Displays chart between stock header and detailed analysis
4. Added loading skeleton for chart

## Usage

### Testing the Feature

1. **Start the backend:**
   ```bash
   cd /path/to/stock-analyzer
   source venv/bin/activate
   python3 run.py
   ```

2. **Start the frontend:**
   ```bash
   cd frontend
   npm run dev
   ```

3. **Access the analyzer:**
   - Navigate to http://localhost:3000/analyzer
   - Enter a ticker: `RELIANCE.NS`
   - Click **Analyze**

### Example Tickers

**Indian Stocks (NSE):**
- RELIANCE.NS
- TCS.NS
- INFY.NS
- HDFCBANK.NS
- ITC.NS

**US Stocks:**
- AAPL
- MSFT
- GOOGL
- TSLA
- AMZN

## Technical Details

### Library Used

**Recharts** - https://recharts.org/
- Open-source React charting library
- Built on D3.js
- Declarative API
- Responsive and customizable
- Version: Latest (installed via npm)

### Installation

```bash
cd frontend
npm install recharts
```

### Chart Types Used

1. **ComposedChart**: Container for combining multiple chart types
2. **Area**: Filled area showing price trend
3. **Line**: Line chart for close prices
4. **BarChart**: Volume bars
5. **CartesianGrid**: Grid lines
6. **XAxis/YAxis**: Axis components
7. **Tooltip**: Custom hover tooltips

### Data Transformation

The component transforms raw OHLC data:
```typescript
// Input: OHLCData from API
{
  date: "2024-10-14T00:00:00",
  open: 2850.50,
  high: 2875.00,
  low: 2840.25,
  close: 2865.75,
  volume: 5234567
}

// Transformed for chart
{
  date: "Oct 14",           // Formatted date
  fullDate: "2024-10-14",   // Original date
  high: 2875.00,
  low: 2840.25,
  open: 2850.50,
  close: 2865.75,
  volume: 5234567,
  isGreen: true,            // close >= open
  range: [2840.25, 2875.00] // [low, high]
}
```

## Customization

### Changing Colors

Edit `CandlestickChart.tsx`:

```typescript
// Green candles (price up)
const greenColor = '#22c55e';  // Tailwind green-500

// Red candles (price down)
const redColor = '#ef4444';    // Tailwind red-500

// Area fill color
const areaColor = '#3b82f6';   // Tailwind blue-500
```

### Changing Chart Height

```typescript
<ResponsiveContainer width="100%" height={400}>
  {/* Change 400 to desired height */}
</ResponsiveContainer>
```

### Adding More Periods

Update the `chartPeriod` state to allow user selection:

```typescript
const [chartPeriod, setChartPeriod] = useState('1y');

// Add period selector UI
<Select value={chartPeriod} onValueChange={setChartPeriod}>
  <SelectItem value="1mo">1 Month</SelectItem>
  <SelectItem value="3mo">3 Months</SelectItem>
  <SelectItem value="6mo">6 Months</SelectItem>
  <SelectItem value="1y">1 Year</SelectItem>
  <SelectItem value="2y">2 Years</SelectItem>
  <SelectItem value="5y">5 Years</SelectItem>
</Select>
```

## Performance Considerations

### Data Caching

- By default, `use_cache=true` fetches data from TimescaleDB
- Cached data is instant (no API calls to Yahoo Finance)
- Force refresh with `use_cache=false` if needed

### Chart Rendering

- Uses React `useMemo` for data transformations
- Calculates price ranges once per data change
- Label intervals adjust based on data points
- Animations are optimized for performance

### Best Practices

1. **Load data for cached tickers** (instant display)
2. **Use 1-day interval** for best chart resolution
3. **Limit to 1-year default** for good UX balance
4. **Parallel data fetching** (stock info + historical data)

## Troubleshooting

### Issue: Chart Not Displaying

**Check:**
1. Backend is running on port 8000
2. Historical data endpoint returns data
3. No console errors in browser
4. Recharts is installed: `npm list recharts`

**Test endpoint:**
```bash
curl "http://localhost:8000/history/RELIANCE.NS?period=1y"
```

### Issue: "No historical data found"

**Solutions:**
1. Load data first: `python3 load_data.py --tickers RELIANCE.NS`
2. Check ticker symbol is correct
3. Try with `use_cache=false` to fetch fresh data

### Issue: Chart Performance is Slow

**Solutions:**
1. Reduce data points (use weekly/monthly interval)
2. Shorten period (use 6mo instead of 5y)
3. Disable animations in Recharts components
4. Use production build: `npm run build && npm start`

## Future Enhancements

### Possible Improvements

1. **True Candlesticks**: Implement custom SVG rendering for traditional candlestick bars
2. **Technical Overlays**: Add MA lines, Bollinger Bands on the chart
3. **Zoom & Pan**: Add interactive zoom controls
4. **Period Selector**: UI to change time periods dynamically
5. **Interval Selector**: Switch between daily/weekly/monthly views
6. **Compare Stocks**: Overlay multiple tickers
7. **Export Chart**: Download as PNG/SVG
8. **Full-screen Mode**: Expand chart to full screen

### Alternative Libraries

If you need more advanced candlestick charts:

1. **Lightweight Charts** (TradingView)
   - https://tradingview.github.io/lightweight-charts/
   - True candlestick support
   - Better performance for large datasets

2. **ApexCharts**
   - https://apexcharts.com/
   - Built-in candlestick chart type
   - More chart types available

3. **Plotly.js**
   - https://plotly.com/javascript/
   - Interactive candlestick charts
   - 3D charts available

## Files Modified

### Backend
- `app/api/routes.py` - Added `/history/{ticker}` endpoint

### Frontend
- `frontend/lib/api.ts` - Added `getHistoricalData()` method and types
- `frontend/components/CandlestickChart.tsx` - New chart component
- `frontend/app/analyzer/page.tsx` - Integrated chart display
- `frontend/package.json` - Added recharts dependency

## Summary

✅ **Backend API** - Historical OHLC data endpoint  
✅ **Frontend Component** - Candlestick chart with volume  
✅ **Data Visualization** - Area chart showing price trends  
✅ **Interactive Tooltips** - Detailed OHLC data on hover  
✅ **Summary Stats** - Period high/low, avg volume, total change  
✅ **Responsive Design** - Works on all screen sizes  
✅ **Open Source** - Using Recharts library  
✅ **Performance** - Cached data from TimescaleDB  

---

**Created:** October 14, 2025  
**Library:** Recharts (Open Source)  
**Chart Types:** Area, Line, Bar  
**Data Source:** Yahoo Finance via yfinance  
**Storage:** TimescaleDB (cached)

