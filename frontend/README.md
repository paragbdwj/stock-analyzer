# Stock Analyzer Frontend

A beautiful, modern UI for analyzing stocks built with Next.js 15, TypeScript, Tailwind CSS, and shadcn/ui.

## Features

- 📊 **Stock Scanner**: Scan entire exchanges with custom technical and fundamental filters
- 🔍 **Stock Analyzer**: Deep dive analysis of individual stocks with comprehensive metrics
- 🎨 **Beautiful UI**: Modern design with shadcn/ui components
- ⚡ **Fast**: Built on Next.js 15 with optimized performance
- 📱 **Responsive**: Works seamlessly on desktop and mobile devices

## Prerequisites

- Node.js 18+ installed
- Stock Analyzer API running on `http://localhost:8000`

## Installation

1. Install dependencies:
```bash
npm install
```

2. Configure environment (optional):
```bash
# Copy .env.local and update if needed
cp .env.local .env.local.example
```

## Development

Run the development server:

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## Building for Production

```bash
npm run build
npm start
```

## Project Structure

```
frontend/
├── app/
│   ├── page.tsx              # Homepage dashboard
│   ├── scanner/
│   │   └── page.tsx          # Stock scanner page
│   ├── analyzer/
│   │   └── page.tsx          # Individual stock analyzer
│   ├── layout.tsx            # Root layout
│   └── globals.css           # Global styles
├── components/
│   └── ui/                   # shadcn/ui components
├── lib/
│   ├── api.ts                # API client & types
│   └── utils.ts              # Utility functions
└── public/                   # Static assets
```

## Available Pages

### Homepage (`/`)
- Overview of all features
- Quick navigation to Scanner and Analyzer
- List of available indicators

### Stock Scanner (`/scanner`)
- Select exchange (NSE, BSE, NASDAQ, NYSE)
- Add technical filters (RSI, MACD, SMA, EMA, etc.)
- Add fundamental filters (P/E, Market Cap, Debt-to-Equity, etc.)
- Combine filters with AND/OR logic
- View matched stocks with comprehensive data

### Stock Analyzer (`/analyzer`)
- Analyze individual stocks by ticker
- View complete technical indicators
- View fundamental metrics
- Organized in tabs for easy navigation

## API Integration

The frontend connects to the Stock Analyzer API. Make sure the backend is running:

```bash
# In the parent directory
cd ../
python run.py
```

API URL can be configured in `.env.local`:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Technologies

- **Next.js 15**: React framework with App Router
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Utility-first styling
- **shadcn/ui**: Beautiful, accessible component library
- **Lucide Icons**: Modern icon set

## Key Components

### Stock Scanner
- Dynamic filter builder for technical & fundamental metrics
- Real-time scanning with loading states
- Beautiful card-based results display
- Tabbed view for technical vs fundamental data

### Stock Analyzer
- Single stock deep-dive analysis
- Comprehensive technical indicators table
- Fundamental metrics breakdown
- Quick stats overview

## Customization

### Adding New Filters

Edit `/app/scanner/page.tsx`:

```typescript
const TECHNICAL_FIELDS = [
  { value: 'new_indicator', label: 'New Indicator' },
  // ...
];
```

### Styling

The app uses Tailwind CSS with shadcn/ui. Colors and themes can be customized in:
- `app/globals.css` - CSS variables
- `tailwind.config.ts` - Tailwind configuration

## Tips

1. **Exchange Suffixes**: 
   - NSE stocks: Add `.NS` (e.g., `RELIANCE.NS`)
   - BSE stocks: Add `.BO` (e.g., `RELIANCE.BO`)
   - US stocks: No suffix needed (e.g., `AAPL`, `MSFT`)

2. **Filter Examples**:
   - Oversold stocks: RSI < 30
   - Overbought stocks: RSI > 70
   - Value stocks: P/E Ratio < 15
   - Large cap: Market Cap > 10B

3. **Performance**: 
   - First scan downloads data (slower)
   - Subsequent scans use cache (faster)
   - Use custom ticker lists for targeted scans

## License

Same as parent project.

---

Built with ❤️ using Next.js and shadcn/ui
