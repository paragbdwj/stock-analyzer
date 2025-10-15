# Historical Fundamentals - Complete Guide

## 🎉 Feature Overview

Your stock analyzer now tracks fundamental data over time! Every time you fetch fundamental data, it saves a snapshot with a timestamp. Over time, you'll build a rich historical dataset to analyze trends.

## ✅ What's Implemented

### Backend
- ✅ Historical storage with timestamps
- ✅ Query by date range
- ✅ API endpoints for history
- ✅ Tracking script for automated snapshots

### Frontend  
- ✅ Enhanced Fundamentals Card with date selector
- ✅ Trend charts for key metrics (P/E, Margins, ROE, etc.)
- ✅ Show/Hide trends toggle
- ✅ Snapshot count badge
- ✅ Automatic historical data fetching

## 📊 How It Works

### Data Collection

**Every time you load data**, a fundamental snapshot is saved:
```bash
# This saves a snapshot for today
python load_data.py --tickers AAPL

# Multiple tickers = multiple snapshots
python load_data.py --tickers AAPL MSFT GOOGL
```

**Track fundamentals manually**:
```bash
# Single ticker
python track_fundamentals.py --ticker AAPL

# Multiple tickers
python track_fundamentals.py --tickers AAPL MSFT GOOGL
```

### Building History

**Option 1: Daily Tracking** (Most detailed)
```bash
# Run this command daily (or set up cron job)
python track_fundamentals.py --tickers AAPL MSFT GOOGL

# After 30 days = 30 snapshots
# After 90 days = 90 snapshots
# After 1 year = 365 snapshots!
```

**Option 2: Weekly Tracking** (Good balance)
```bash
# Run every Monday
python track_fundamentals.py --tickers AAPL

# After 12 weeks = 12 snapshots
# After 1 year = 52 snapshots
```

**Option 3: Monthly Tracking** (Minimal)
```bash
# Run first day of month
python track_fundamentals.py --tickers AAPL

# After 1 year = 12 snapshots
```

## 🔧 Setup Automated Tracking

### Option A: Cron Job (Linux/Mac)

```bash
# Edit crontab
crontab -e

# Add one of these:

# Daily at 6 PM
0 18 * * * cd /path/to/stock-analyzer && source venv/bin/activate && python track_fundamentals.py --tickers AAPL MSFT GOOGL

# Every Monday at 9 AM
0 9 * * 1 cd /path/to/stock-analyzer && source venv/bin/activate && python track_fundamentals.py --tickers AAPL MSFT GOOGL

# First day of month at 9 AM
0 9 1 * * cd /path/to/stock-analyzer && source venv/bin/activate && python track_fundamentals.py --tickers AAPL MSFT GOOGL
```

### Option B: Systemd Timer (Linux)

Create `/etc/systemd/system/track-fundamentals.service`:
```ini
[Unit]
Description=Track Stock Fundamentals
After=network.target

[Service]
Type=oneshot
User=your-username
WorkingDirectory=/path/to/stock-analyzer
ExecStart=/path/to/stock-analyzer/venv/bin/python track_fundamentals.py --tickers AAPL MSFT GOOGL

[Install]
WantedBy=multi-user.target
```

Create `/etc/systemd/system/track-fundamentals.timer`:
```ini
[Unit]
Description=Track Stock Fundamentals Daily
Requires=track-fundamentals.service

[Timer]
OnCalendar=daily
Persistent=true

[Install]
WantedBy=timers.target
```

Enable:
```bash
sudo systemctl daemon-reload
sudo systemctl enable track-fundamentals.timer
sudo systemctl start track-fundamentals.timer
```

### Option C: Task Scheduler (Windows)

1. Open Task Scheduler
2. Create New Task
3. Trigger: Daily at 6 PM
4. Action: Start a Program
   - Program: `C:\path\to\venv\Scripts\python.exe`
   - Arguments: `track_fundamentals.py --tickers AAPL MSFT GOOGL`
   - Start in: `C:\path\to\stock-analyzer`

## 💻 Using the Feature

### 1. Command Line

**View historical snapshots**:
```bash
python track_fundamentals.py --ticker AAPL --view-history
```

Output:
```
Fundamental history for AAPL
============================================================
Found 30 snapshots

1. Snapshot from 2025-10-15 18:00:00
----------------------------------------
   P/E Ratio: 37.60
   Market Cap: $3,677,003,448,320
   Profit Margin: 24.30%
   ROE: 149.81%
   Revenue Growth: 9.60%

2. Snapshot from 2025-10-14 18:00:00
----------------------------------------
   P/E Ratio: 37.52
   Market Cap: $3,665,234,567,890
   ...
```

**Setup instructions**:
```bash
python track_fundamentals.py --tickers AAPL --setup-schedule
```

### 2. Web UI

#### Step 1: Start Services
```bash
# Terminal 1 - Backend
cd /path/to/stock-analyzer
source venv/bin/activate
python run.py

# Terminal 2 - Frontend
cd frontend
npm run dev
```

#### Step 2: Analyze Stock
1. Go to http://localhost:3000/analyzer
2. Search for "AAPL"
3. Click "Analyze"

#### Step 3: View Historical Data

You'll see the **Enhanced Fundamentals Card** with:

**Date Selector**:
```
View snapshot from: [Oct 15, 2024 ▼]  2 snapshots
```

**Toggle Trends**:
```
[Show Trends] button in top-right
```

**When trends are shown**, you'll see:
- 📈 P/E Ratio Trend (line chart)
- 📈 P/B Ratio Trend
- 📈 Profit Margin Trend
- 📈 ROE Trend
- 📈 Revenue Growth Trend

#### Step 4: Compare Snapshots

Click the date dropdown to switch between different time periods:
```
📅 Oct 15, 2024 - P/E: 37.60, Margin: 24.30%
📅 Oct 8, 2024  - P/E: 37.52, Margin: 24.25%
📅 Oct 1, 2024  - P/E: 36.98, Margin: 24.10%
📅 Sep 24, 2024 - P/E: 36.45, Margin: 23.95%
```

### 3. API

**Get latest fundamentals**:
```bash
curl http://localhost:8000/fundamentals/AAPL
```

**Get historical fundamentals**:
```bash
# All history
curl http://localhost:8000/fundamentals/AAPL/history

# Date range
curl "http://localhost:8000/fundamentals/AAPL/history?start_date=2024-01-01&end_date=2024-10-15"
```

Response:
```json
{
  "ticker": "AAPL",
  "snapshots": [
    {
      "ticker": "AAPL",
      "timestamp": "2025-10-15T18:00:00",
      "trailing_pe": 37.60,
      "market_cap": 3677003448320,
      "profit_margin": 0.2430,
      "return_on_equity": 1.4981,
      "revenue_growth": 0.096,
      ...
    },
    {
      "ticker": "AAPL",
      "timestamp": "2025-10-14T18:00:00",
      ...
    }
  ],
  "total_snapshots": 30
}
```

## 📈 Analysis Possibilities

### 1. Trend Analysis
Track how metrics change over time:
- Is P/E ratio increasing or decreasing?
- Are profit margins improving?
- Is ROE growing?

### 2. Seasonal Patterns
Identify quarterly patterns:
- Q4 might have higher margins (holiday season)
- Q1 might show revenue growth after product launches

### 3. Deterioration Detection
Spot problems early:
- Declining margins
- Increasing debt-to-equity
- Slowing revenue growth

### 4. Valuation Timing
Find good entry points:
- P/E ratio at historical lows
- P/B ratio below average
- High ROE with low P/E

### 5. Comparison with Technicals
Compare fundamental trends with price trends:
- Stock price up but margins down = warning
- Price down but fundamentals improving = opportunity

## 🎯 Best Practices

### 1. Consistency
Track at the same time each period:
- Daily: After market close (5 PM EST)
- Weekly: Same day (Monday mornings)
- Monthly: First business day

### 2. Frequency
Choose based on needs:
- **Day traders**: Daily tracking
- **Swing traders**: Weekly tracking
- **Long-term investors**: Monthly tracking

### 3. Watchlist
Focus on key stocks:
```bash
# Your main holdings
python track_fundamentals.py --tickers AAPL MSFT GOOGL AMZN

# Add new stocks as you research
python track_fundamentals.py --ticker TSLA
```

### 4. Storage
Historical fundamentals use minimal space:
- 1 snapshot ≈ 300 bytes
- 365 snapshots ≈ 110 KB per stock
- 100 stocks × 365 days ≈ 11 MB

### 5. Analysis
Review trends regularly:
- Weekly: Check your holdings
- Monthly: Deep dive into watchlist
- Quarterly: Compare with earnings reports

## 🔍 Example Workflow

### Day 1: Setup
```bash
# Load initial data
python load_data.py --tickers AAPL MSFT GOOGL

# Setup daily tracking
crontab -e
# Add: 0 18 * * * cd /path && python track_fundamentals.py --tickers AAPL MSFT GOOGL
```

### Week 1: Building History
- Day 1: 1 snapshot
- Day 7: 7 snapshots
- Can already see daily trends!

### Month 1: Meaningful Trends
- 30 snapshots collected
- View monthly trends in UI
- Compare current vs 30 days ago

### Quarter 1: Quarterly Analysis
- 90 snapshots collected
- Analyze quarter-over-quarter
- Compare with earnings data

### Year 1: Full Historical View
- 365 snapshots collected
- Full year of trends
- Seasonal pattern analysis
- Year-over-year comparisons

## 💡 Tips

### Tip 1: Start Small
```bash
# Start with 3-5 stocks you know well
python track_fundamentals.py --tickers AAPL MSFT GOOGL
```

### Tip 2: Be Patient
- Week 1: Limited data
- Week 4: Useful trends emerging
- Week 12: Solid historical view
- Week 52: Complete annual picture

### Tip 3: Combine with Technical
```bash
# Load everything together
python load_data.py --tickers AAPL --period 20y
# This gives you:
# - 20 years of OHLCV
# - All technical indicators
# - Current fundamental snapshot
```

### Tip 4: Document Changes
When you see big changes, check why:
- Earnings release?
- Stock split?
- Major news?
- Market correction?

### Tip 5: Export Data
```python
# In Python
from app.utils.storage import StorageManager
storage = StorageManager()
history = storage.load_fundamental_data_history("AAPL")

# Export to CSV
import pandas as pd
df = pd.DataFrame(history)
df.to_csv("aapl_fundamentals_history.csv")
```

## 🎨 UI Features

### Enhanced Fundamentals Card

**Features**:
- 📅 Date selector dropdown
- 🔢 Snapshot count badge
- 📊 Toggle trend charts
- 🎨 Color-coded charts
- 📈 5 trend charts (when enabled)
- 🔍 Metric comparison across time

**Trend Charts Include**:
1. P/E Ratio over time
2. P/B Ratio over time
3. Profit Margin over time
4. ROE over time
5. Revenue Growth over time

**Responsive**:
- Desktop: Side-by-side with indicators
- Mobile: Stacked layout
- Trends: Scrollable if many snapshots

## 📚 Related

- **Load Script**: `load_data.py` - Loads OHLCV, indicators, and fundamentals
- **Track Script**: `track_fundamentals.py` - Tracks fundamentals over time
- **View History**: API endpoint `/fundamentals/{ticker}/history`
- **UI Component**: `FundamentalsCardEnhanced.tsx`

## 🚀 Next Steps

1. **Start tracking**: `python track_fundamentals.py --tickers AAPL`
2. **Setup schedule**: `python track_fundamentals.py --setup-schedule`
3. **View in UI**: Open analyzer and search for your stock
4. **Monitor trends**: Check weekly for changes

## 🎉 Summary

You now have a complete system for tracking fundamental data over time! Every snapshot you capture builds your historical dataset, enabling powerful trend analysis and better investment decisions.

**Start today** and in a month you'll have 30 data points. In a year, you'll have a complete picture of how your stocks' fundamentals evolved!

