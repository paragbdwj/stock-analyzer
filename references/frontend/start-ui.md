# 🚀 Quick Start - Stock Analyzer UI

## Step 1: Start Backend (Terminal 1)

```bash
cd /Users/paragbhardwaj/Documents/Projects/stock-market/stock-analyzer
python run.py
```

✅ Wait for: `Application startup complete` or `Uvicorn running on http://0.0.0.0:8000`

---

## Step 2: Start Frontend (Terminal 2)

```bash
cd /Users/paragbhardwaj/Documents/Projects/stock-market/stock-analyzer/frontend
npm run dev
```

✅ Wait for: `Local: http://localhost:3000`

---

## Step 3: Open Browser

Navigate to: **http://localhost:3000**

---

## 🎯 Try These Examples

### Example 1: Scan for Oversold Stocks
1. Click **"Open Scanner"** on homepage
2. Select Exchange: **NSE**
3. Click **"+"** under Technical Filters
4. Set: **RSI** **<** **30**
5. Click **"Run Scan"**

### Example 2: Analyze AAPL
1. Click **"Analyze Stock"** on homepage
2. Type: **AAPL**
3. Press **Enter** or click **"Analyze"**
4. Explore Technical and Fundamental tabs

### Example 3: Find Value Stocks
1. Go to **Scanner**
2. Add Technical Filter: **RSI** **<** **40**
3. Add Fundamental Filter: **trailing_pe** **<** **20**
4. Set Filter Logic: **AND**
5. Click **"Run Scan"**

---

## 📱 URLs

- **Homepage**: http://localhost:3000
- **Scanner**: http://localhost:3000/scanner
- **Analyzer**: http://localhost:3000/analyzer
- **API Docs**: http://localhost:8000/docs

---

## 🎨 Features

### Scanner Page
- Filter by 15+ technical indicators
- Filter by 8+ fundamental metrics
- Combine with AND/OR logic
- Beautiful card-based results
- Tabbed data view

### Analyzer Page
- Deep dive into any stock
- 30+ data points
- Organized in tables
- Quick stats overview
- Professional layout

---

## 💡 Ticker Examples

### Indian Stocks (NSE)
```
RELIANCE.NS
TCS.NS
INFY.NS
HDFCBANK.NS
ICICIBANK.NS
```

### US Stocks
```
AAPL
MSFT
GOOGL
TSLA
NVDA
META
AMZN
```

---

## 🎯 Common Filter Combinations

### Oversold Value Stocks
- RSI < 30
- P/E Ratio < 20
- Market Cap > 10B
- Logic: AND

### High Momentum
- RSI > 60
- MACD > 0
- Logic: AND

### Large Cap Undervalued
- Market Cap > 10,000,000,000
- P/E Ratio < 15
- Debt-to-Equity < 1
- Logic: AND

---

## ❓ Troubleshooting

### Frontend won't start
```bash
cd frontend
npm install
npm run dev
```

### Backend won't start
```bash
# Check if TimescaleDB is running
docker-compose ps

# Start it if needed
docker-compose up -d

# Then start backend
python run.py
```

### Can't connect to API
- Check backend is running: http://localhost:8000/health
- Check frontend .env.local has correct URL
- Restart both servers

---

## 📚 More Info

- Full documentation: See `UI_SUMMARY.md`
- Setup guide: See `FRONTEND_SETUP.md`
- Frontend README: See `frontend/README.md`

---

**That's it! Enjoy your stock analyzer! 🎉📈**

