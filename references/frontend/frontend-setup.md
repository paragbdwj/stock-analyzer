# Frontend Setup Guide

## Quick Start

### 1. Start the Backend API

First, make sure the Stock Analyzer API is running:

```bash
# In the project root
python run.py
```

The API should be available at `http://localhost:8000`

### 2. Start the Frontend

In a new terminal:

```bash
cd frontend
npm run dev
```

The frontend will be available at `http://localhost:3000`

## Features Overview

### 🏠 Homepage (`http://localhost:3000`)
- Overview of all features
- Quick navigation cards
- Available indicators list

### 🔍 Stock Scanner (`http://localhost:3000/scanner`)
**Filter stocks across entire exchanges**

**Example Use Cases:**
1. **Find Oversold Value Stocks**
   - Technical Filter: RSI < 30
   - Fundamental Filter: P/E Ratio < 20
   - Logic: AND

2. **Find High Momentum Stocks**
   - Technical Filter: RSI > 60
   - Technical Filter: MACD > 0
   - Logic: AND

3. **Find Large Cap Undervalued Stocks**
   - Fundamental Filter: Market Cap > 10000000000
   - Fundamental Filter: P/E Ratio < 15
   - Logic: AND

### 📊 Stock Analyzer (`http://localhost:3000/analyzer`)
**Deep analysis of individual stocks**

**Try these tickers:**
- Indian stocks: `RELIANCE.NS`, `TCS.NS`, `INFY.NS`, `HDFCBANK.NS`
- US stocks: `AAPL`, `MSFT`, `GOOGL`, `TSLA`, `NVDA`

## UI Components Used

All components are from shadcn/ui:
- ✅ Button - Interactive actions
- ✅ Card - Content containers
- ✅ Input - Text input fields
- ✅ Label - Form labels
- ✅ Select - Dropdown selections
- ✅ Badge - Status indicators
- ✅ Tabs - Organized content views
- ✅ Table - Data display
- ✅ Skeleton - Loading states
- ✅ Alert - Error messages
- ✅ Separator - Visual dividers

## API Configuration

The frontend expects the API at `http://localhost:8000` by default.

To change the API URL:
1. Create `.env.local` in the frontend directory
2. Add: `NEXT_PUBLIC_API_URL=http://your-api-url:port`
3. Restart the dev server

## Screenshots

### Homepage
- Clean, modern landing page
- Feature cards with descriptions
- Quick access buttons

### Scanner
- Left panel: Filter configuration
  - Exchange selection
  - Custom ticker input
  - Technical filters (RSI, MACD, SMA, etc.)
  - Fundamental filters (P/E, Market Cap, etc.)
  - AND/OR logic selector
- Right panel: Scan results
  - Matched stocks count
  - Scan duration
  - Stock cards with tabbed data
  - Matched filters badges

### Analyzer
- Search bar with ticker input
- Stock header with price and key metrics
- Quick stats cards
- Detailed tabbed analysis
  - Technical indicators table
  - Fundamental metrics table

## Design Features

### Color Scheme
- Neutral base with primary accent colors
- Dark mode ready
- Gradient backgrounds

### Layout
- Responsive design (mobile, tablet, desktop)
- Clean card-based interfaces
- Intuitive navigation
- Loading states with skeletons
- Error handling with alerts

### Typography
- Inter font family
- Clear hierarchy
- Readable sizes

### Interactions
- Hover effects on cards
- Smooth transitions
- Loading states
- Form validation

## Tips for Best Results

1. **Start Backend First**: Always start the API before the frontend
2. **Use Valid Tickers**: Include exchange suffix for Indian stocks (.NS or .BO)
3. **Filter Combinations**: Start with simple filters and add more
4. **Cache Behavior**: First scan is slow, subsequent scans are fast
5. **Custom Tickers**: Use comma-separated list for specific stocks

## Troubleshooting

### "Failed to fetch" error
- ✅ Check if API is running (`http://localhost:8000/health`)
- ✅ Verify API URL in browser console
- ✅ Check CORS settings in backend

### No results in scanner
- ✅ Try broader filter criteria
- ✅ Verify exchange has tickers
- ✅ Check if filters are too restrictive

### Ticker not found
- ✅ Verify ticker symbol is correct
- ✅ Add proper suffix (.NS, .BO)
- ✅ Try force refresh option

## Architecture

```
Frontend (Next.js)          Backend (FastAPI)
     ↓                            ↓
  Browser                   localhost:8000
localhost:3000                     ↓
     ↓                       TimescaleDB
  API Client ────────────►   PostgreSQL
  (lib/api.ts)                   ↓
     ↓                      Yahoo Finance
 Components                   API Data
```

## Development

### Adding New Pages
```typescript
// app/new-page/page.tsx
export default function NewPage() {
  return <div>New Page</div>
}
```

### Adding New Components
```bash
npx shadcn@latest add [component-name]
```

### Modifying Filters
Edit the constants in `/app/scanner/page.tsx`:
- `TECHNICAL_FIELDS`
- `FUNDAMENTAL_FIELDS`
- `OPERATORS`

## Production Deployment

1. Build the application:
```bash
npm run build
```

2. Start production server:
```bash
npm start
```

3. Or deploy to Vercel:
```bash
vercel deploy
```

Remember to set environment variables in your hosting platform!

---

## Next Steps

1. ✅ Start the backend API
2. ✅ Start the frontend dev server
3. ✅ Open http://localhost:3000
4. ✅ Try the Stock Scanner
5. ✅ Try the Stock Analyzer
6. ✅ Explore different filters and combinations

Enjoy analyzing stocks! 📈

