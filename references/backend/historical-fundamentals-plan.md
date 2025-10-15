# Historical Fundamentals - Implementation Plan

## Current State

### ✅ Already In Place
- Database schema supports multiple timestamps per ticker (composite primary key)
- `StockFundamentals` table with timestamp field
- Storage methods in `StorageManager`

### ❌ What's Missing
- Only one snapshot is stored per ticker (latest)
- No quarterly/annual historical fundamental fetching
- API only returns latest snapshot
- No UI to select date range for fundamentals

## 🎯 Implementation Plan

### Phase 1: Backend - Historical Storage

#### 1. Update Storage to Keep Multiple Snapshots

**File**: `app/utils/storage.py`

```python
def save_fundamental_data(self, ticker: str, fundamental_data: Dict[str, Any], timestamp: Optional[datetime] = None) -> bool:
    """
    Save fundamental data to database.
    
    Args:
        ticker: Stock ticker symbol
        fundamental_data: Dictionary with fundamental metrics
        timestamp: Specific timestamp for this snapshot (default: now)
    
    Returns:
        True if successful, False otherwise
    """
    if not fundamental_data:
        logger.warning(f"No fundamental data to save for {ticker}")
        return False
    
    try:
        from app.database.connection import get_session
        with get_session() as session:
            # Use provided timestamp or current time
            snapshot_time = timestamp or datetime.utcnow()
            
            # Create fundamental record (don't use merge, allow multiple snapshots)
            fundamental = StockFundamentals(
                ticker=ticker,
                timestamp=snapshot_time,
                trailing_pe=fundamental_data.get('trailingPE'),
                # ... other fields
            )
            
            # Add (don't merge) to allow multiple snapshots
            session.add(fundamental)
            session.commit()
            
            logger.debug(f"Saved fundamental data for {ticker} at {snapshot_time}")
            return True
            
    except Exception as e:
        logger.error(f"Failed to save fundamental data for {ticker}: {e}")
        return False
```

#### 2. Add Historical Fetching from yfinance

**File**: `app/services/fundamental_service.py`

```python
def get_quarterly_fundamentals(self, ticker: str, periods: int = 8) -> List[Dict]:
    """
    Get quarterly fundamental data (last N quarters).
    
    Args:
        ticker: Stock ticker symbol
        periods: Number of quarters to fetch
    
    Returns:
        List of dictionaries with quarterly fundamentals
    """
    try:
        stock = yf.Ticker(ticker)
        
        # Get quarterly financials
        quarterly_financials = stock.quarterly_financials
        quarterly_balance = stock.quarterly_balance_sheet
        quarterly_cashflow = stock.quarterly_cashflow
        
        snapshots = []
        
        # Process each quarter
        for date in quarterly_financials.columns[:periods]:
            snapshot = {
                'timestamp': date,
                'ticker': ticker,
                # Extract metrics from each quarter
                # ... calculate ratios from financial statements
            }
            snapshots.append(snapshot)
        
        return snapshots
        
    except Exception as e:
        logger.error(f"Failed to get quarterly fundamentals for {ticker}: {e}")
        return []

def get_annual_fundamentals(self, ticker: str, years: int = 5) -> List[Dict]:
    """
    Get annual fundamental data (last N years).
    """
    # Similar to quarterly but using annual data
    pass
```

#### 3. Update API Endpoints

**File**: `app/api/routes.py`

```python
@router.get("/fundamentals/{ticker}/history")
async def get_fundamentals_history(
    ticker: str,
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    frequency: str = Query("all", description="Filter by frequency: all, quarterly, annual")
):
    """
    Get historical fundamental data for a ticker.
    
    Returns time-series of fundamental snapshots.
    
    Example:
        GET /fundamentals/AAPL/history?start_date=2020-01-01&end_date=2024-01-01
    """
    try:
        from app.database.connection import get_session
        
        with get_session() as session:
            query = session.query(StockFundamentals).filter(
                StockFundamentals.ticker == ticker
            )
            
            # Apply date filters
            if start_date:
                query = query.filter(StockFundamentals.timestamp >= start_date)
            if end_date:
                query = query.filter(StockFundamentals.timestamp <= end_date)
            
            # Order by date
            snapshots = query.order_by(StockFundamentals.timestamp.desc()).all()
            
            if not snapshots:
                raise HTTPException(
                    status_code=404,
                    detail=f"No historical fundamental data found for {ticker}"
                )
            
            # Convert to list of dicts
            history = [snapshot.to_dict() for snapshot in snapshots]
            
            return {
                "ticker": ticker,
                "snapshots": history,
                "total_snapshots": len(history)
            }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting fundamental history for {ticker}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

### Phase 2: Data Loading Script

**File**: `load_historical_fundamentals.py`

```python
#!/usr/bin/env python3
"""
Load historical fundamental data (quarterly/annual).
"""

def load_historical_fundamentals(
    ticker: str,
    periods: int = 8,
    frequency: str = "quarterly"
):
    """
    Load historical fundamental data.
    
    Args:
        ticker: Stock ticker symbol
        periods: Number of periods to load
        frequency: 'quarterly' or 'annual'
    """
    logger.info(f"Loading {frequency} fundamentals for {ticker} ({periods} periods)")
    
    fundamental_service = FundamentalService()
    storage = StorageManager()
    
    if frequency == "quarterly":
        snapshots = fundamental_service.get_quarterly_fundamentals(ticker, periods)
    else:
        snapshots = fundamental_service.get_annual_fundamentals(ticker, periods)
    
    # Save each snapshot
    for snapshot in snapshots:
        storage.save_fundamental_data(
            ticker=ticker,
            fundamental_data=snapshot,
            timestamp=snapshot['timestamp']
        )
    
    logger.info(f"✓ Loaded {len(snapshots)} fundamental snapshots for {ticker}")

# Usage
if __name__ == "__main__":
    # Load last 8 quarters of AAPL fundamentals
    load_historical_fundamentals("AAPL", periods=8, frequency="quarterly")
    
    # Load last 5 years of annual fundamentals
    load_historical_fundamentals("AAPL", periods=5, frequency="annual")
```

### Phase 3: Frontend Updates

#### 1. Add Date Selector to Fundamentals Card

```typescript
// frontend/components/FundamentalsCard.tsx

interface FundamentalsCardProps {
  fundamentals: FundamentalData;
  ticker?: string;
  historicalData?: FundamentalData[];  // ← NEW
  onDateChange?: (date: string) => void;  // ← NEW
}

export function FundamentalsCard({ 
  fundamentals, 
  ticker,
  historicalData,
  onDateChange 
}: FundamentalsCardProps) {
  // Add date selector if historical data available
  {historicalData && historicalData.length > 1 && (
    <Select onValueChange={onDateChange}>
      <SelectTrigger>
        <SelectValue placeholder="Select date" />
      </SelectTrigger>
      <SelectContent>
        {historicalData.map((snapshot) => (
          <SelectItem key={snapshot.timestamp} value={snapshot.timestamp}>
            {new Date(snapshot.timestamp).toLocaleDateString()} - Q{getQuarter(snapshot.timestamp)}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  )}
  
  // ... rest of component
}
```

#### 2. Add Historical Trend Charts

```typescript
// components/FundamentalTrendChart.tsx

export function FundamentalTrendChart({ 
  historicalData, 
  metric 
}: { 
  historicalData: FundamentalData[], 
  metric: keyof FundamentalData 
}) {
  // Plot trend of a specific metric over time
  // e.g., P/E ratio over last 8 quarters
  
  return (
    <ResponsiveContainer width="100%" height={200}>
      <LineChart data={historicalData}>
        <XAxis dataKey="timestamp" />
        <YAxis />
        <Tooltip />
        <Line type="monotone" dataKey={metric} stroke="#8884d8" />
      </LineChart>
    </ResponsiveContainer>
  );
}
```

#### 3. Update API Client

```typescript
// frontend/lib/api.ts

async getFundamentalsHistory(
  ticker: string,
  startDate?: string,
  endDate?: string
): Promise<{ ticker: string; snapshots: FundamentalData[]; total_snapshots: number }> {
  const params = new URLSearchParams();
  if (startDate) params.append('start_date', startDate);
  if (endDate) params.append('end_date', endDate);
  const query = params.toString() ? `?${params.toString()}` : '';
  return this.request(`/fundamentals/${ticker}/history${query}`);
}
```

## 📊 Example Usage

### Loading Historical Data

```bash
# Load quarterly fundamentals for last 2 years (8 quarters)
python load_historical_fundamentals.py --ticker AAPL --periods 8 --frequency quarterly

# Load annual fundamentals for last 10 years
python load_historical_fundamentals.py --ticker AAPL --periods 10 --frequency annual

# Bulk load for multiple tickers
python load_historical_fundamentals.py --tickers AAPL MSFT GOOGL --periods 8
```

### API Calls

```bash
# Get all fundamental snapshots for AAPL
GET /fundamentals/AAPL/history

# Get fundamentals for specific date range
GET /fundamentals/AAPL/history?start_date=2020-01-01&end_date=2024-01-01

# Get only quarterly snapshots
GET /fundamentals/AAPL/history?frequency=quarterly
```

### Frontend Display

```
┌─────────────────────────────────────────┐
│ Fundamental Analysis                    │
│                                         │
│ 📅 Date: Q3 2024 ▼                     │
│    (shows dropdown with quarters)       │
│                                         │
│ Valuation Metrics                       │
│ Market Cap: $2.8T                       │
│ P/E Ratio: 28.5                         │
│                                         │
│ 📈 P/E Trend (Last 8 Quarters)         │
│ [Line chart showing P/E over time]     │
│                                         │
│ 📈 Profit Margin Trend                 │
│ [Line chart showing margin over time]  │
└─────────────────────────────────────────┘
```

## 🎯 Benefits

### For Analysis
- **Track trends**: See how P/E ratio changed over time
- **Identify patterns**: Spot deteriorating margins or improving ROE
- **Compare periods**: Q3 2023 vs Q3 2024
- **Seasonal analysis**: Identify quarterly patterns

### Use Cases
1. **Valuation Analysis**: How has P/E changed over time?
2. **Growth Tracking**: Is revenue growth accelerating?
3. **Margin Analysis**: Are profit margins improving?
4. **Debt Management**: Is debt-to-equity decreasing?
5. **Dividend Policy**: Is payout ratio stable?

## 📝 Data Availability

### From Yahoo Finance
- **Quarterly**: Last ~8-12 quarters typically available
- **Annual**: Last ~5-10 years available
- **Metrics Available**:
  - Income Statement: Revenue, Net Income, Margins
  - Balance Sheet: Assets, Liabilities, Equity
  - Cash Flow: Operating CF, Free CF
  - Calculated Ratios: P/E, P/B, ROE, etc.

### Limitations
- Historical data quality varies by stock
- Some older data may be incomplete
- Quarterly data for some markets may be limited
- Need to calculate some ratios from financial statements

## 🚀 Implementation Priority

### Phase 1 (Core) - 2-3 hours
1. ✅ Database already supports it (composite key)
2. ⚠️ Update storage to not overwrite (remove merge, use add)
3. ⚠️ Add API endpoint for historical data
4. ⚠️ Create loading script

### Phase 2 (Enhanced) - 3-4 hours
5. ⚠️ Implement quarterly data fetching from yfinance
6. ⚠️ Add frontend date selector
7. ⚠️ Display historical data in UI

### Phase 3 (Advanced) - 4-5 hours
8. ⚠️ Add trend charts for key metrics
9. ⚠️ Add comparison between quarters/years
10. ⚠️ Add alerts for significant changes

## 🎨 Visualization Ideas

### 1. Timeline View
Show fundamentals at different points in time with a slider

### 2. Metric Trends
Line charts for:
- P/E Ratio over time
- Revenue growth rate
- Profit margins
- ROE trends

### 3. Comparison Table
```
Metric        | Q3 2024 | Q2 2024 | Q1 2024 | Change
------------- | ------- | ------- | ------- | ------
P/E Ratio     | 28.5    | 27.2    | 29.1    | +4.8%
Profit Margin | 25.3%   | 24.8%   | 25.1%   | +2.0%
ROE           | 147%    | 145%    | 142%    | +3.5%
```

### 4. Heatmap
Show multiple metrics across quarters in a color-coded grid

## 🔮 Future Enhancements

1. **Automatic Updates**: Fetch quarterly data automatically after earnings
2. **Peer Comparison**: Compare historical fundamentals with competitors
3. **Alerts**: Notify when key metrics change significantly
4. **Forecasting**: Use historical data to project future values
5. **Export**: Download historical fundamental data as CSV/Excel

## 📚 Resources

- **yfinance Documentation**: Quarterly/Annual data methods
- **Financial Statement Analysis**: Understanding quarterly variations
- **TimescaleDB**: Time-series queries and continuous aggregates

---

**Status**: Ready to implement
**Complexity**: Medium
**Value**: High (for serious investors and analysts)

