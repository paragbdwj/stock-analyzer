'use client';

import { useState, useEffect, useRef, useMemo } from 'react';
import { Search } from 'lucide-react';
import { Input } from '@/components/ui/input';
import Fuse from 'fuse.js';

// Hardcoded list of popular tickers
const POPULAR_TICKERS = [
    // Indian Stocks - NSE (Expanded List)
    'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 'ICICIBANK.NS',
    'HINDUNILVR.NS', 'ITC.NS', 'SBIN.NS', 'BHARTIARTL.NS', 'KOTAKBANK.NS',
    'LT.NS', 'AXISBANK.NS', 'ASIANPAINT.NS', 'MARUTI.NS', 'TITAN.NS',
    'SUNPHARMA.NS', 'ULTRACEMCO.NS', 'BAJFINANCE.NS', 'NESTLEIND.NS', 'WIPRO.NS',
    'HCLTECH.NS', 'ONGC.NS', 'NTPC.NS', 'POWERGRID.NS', 'TATAMOTORS.NS',
    'TATASTEEL.NS', 'INDUSINDBK.NS', 'TECHM.NS', 'M&M.NS', 'ADANIPORTS.NS',
    'BAJAJFINSV.NS', 'DRREDDY.NS', 'JSWSTEEL.NS', 'CIPLA.NS', 'DIVISLAB.NS',
    'GRASIM.NS', 'BPCL.NS', 'EICHERMOT.NS', 'HEROMOTOCO.NS', 'BRITANNIA.NS',
    'APOLLOHOSP.NS', 'SHREECEM.NS', 'UPL.NS', 'ADANIENT.NS', 'HINDALCO.NS',
    'COALINDIA.NS', 'TATACONSUM.NS', 'BAJAJ-AUTO.NS', 'SBILIFE.NS', 'HDFCLIFE.NS',
    'TATASTLLP.NS', 'IOC.NS', 'HAVELLS.NS', 'PIDILITIND.NS', 'GAIL.NS',
    'ICICIPRULI.NS', 'SIEMENS.NS', 'DLF.NS', 'LTIM.NS', 'SBICARD.NS',
    'AMBUJACEM.NS', 'HDFCAMC.NS', 'INDIGO.NS', 'MARICO.NS', 'BERGEPAINT.NS',
    'BOSCHLTD.NS', 'HINDPETRO.NS', 'PNB.NS', 'GLAND.NS', 'COLPAL.NS',
    'PEL.NS', 'BANKBARODA.NS', 'ZOMATO.NS', 'NYKAA.NS', 'PAYTM.NS',
    'POLICYBZR.NS', 'IRCTC.NS', 'VEDL.NS', 'IDFCFIRSTB.NS', 'YESBANK.NS',
    // ... and many more
  
    // Indian Stocks - BSE (Expanded List)
    'RELIANCE.BO', 'TCS.BO', 'HDFCBANK.BO', 'INFY.BO', 'ICICIBANK.BO',
    'ITC.BO', 'SBIN.BO', 'BHARTIARTL.BO', 'KOTAKBANK.BO', 'LT.BO',
    'AXISBANK.BO', 'ASIANPAINT.BO', 'MARUTI.BO', 'TITAN.BO', 'SUNPHARMA.BO',
    'ULTRACEMCO.BO', 'BAJFINANCE.BO', 'NESTLEIND.BO', 'WIPRO.BO', 'HCLTECH.BO',
    'TATAMOTORS.BO', 'TATASTEEL.BO', 'M&M.BO', 'BAJAJFINSV.BO', 'INDUSINDBK.BO',
    'TECHM.BO', 'DRREDDY.BO', 'POWERGRID.BO', 'NTPC.BO', 'ONGC.BO',
    'BAJAJ-AUTO.BO', 'BHARTIARTL.BO', 'CIPLA.BO', 'GRASIM.BO', 'HDFCLIFE.BO',
    'HEROMOTOCO.BO', 'HINDALCO.BO', 'HINDUNILVR.BO', 'IOC.BO', 'JSWSTEEL.BO',
    'SBILIFE.BO', 'SHREECEM.BO', 'TATACONSUM.BO', 'UPL.BO', 'WIPRO.BO',
    'ADANIENT.BO', 'ADANIPORTS.BO', 'APOLLOHOSP.BO', 'BPCL.BO', 'BRITANNIA.BO',
    'COALINDIA.BO', 'DIVISLAB.BO', 'EICHERMOT.BO', 'ICICIPRULI.BO', 'LTIM.BO',
    // ... and many more
    
    // US Stocks - NASDAQ & NYSE (Expanded List)
    // Tech & Growth (NASDAQ focus)
    'AAPL', 'MSFT', 'GOOGL', 'GOOG', 'AMZN', 'NVDA', 'META', 'TSLA', 'AVGO', 'COST',
    'NFLX', 'AMD', 'PEP', 'CSCO', 'ADBE', 'CMCSA', 'TMUS', 'INTC', 'QCOM', 'TXN',
    'AMGN', 'INTU', 'AMAT', 'HON', 'BKNG', 'SBUX', 'ISRG', 'GILD', 'VRTX', 'ADP',
    'REGN', 'PANW', 'LRCX', 'MU', 'ADI', 'MDLZ', 'KLAC', 'SNPS', 'CDNS', 'MELI',
    'PYPL', 'ABNB', 'MAR', 'NXPI', 'ORLY', 'CRWD', 'MRVL', 'FTNT', 'WDAY', 'DASH',
    'ZM', 'DOCU', 'DDOG', 'TEAM', 'OKTA', 'ZS', 'MDB', 'ROKU', 'EXC', 'AEP',
    'EA', 'ATVI', 'CTSH', 'CSX', 'FISV', 'EXPE', 'KDP', 'KHC', 'LULU', 'MNST',
    
    // Blue Chip & Value (NYSE focus)
    'BRK.B', 'JPM', 'V', 'JNJ', 'WMT', 'XOM', 'UNH', 'MA', 'PG', 'HD',
    'CVX', 'ABBV', 'MRK', 'KO', 'BAC', 'PFE', 'LLY', 'ORCL', 'TMO',
    'ACN', 'MCD', 'ABT', 'DIS', 'VZ', 'NKE', 'CRM', 'WFC', 'DHR', 'PM',
    'BMY', 'NEE', 'UPS', 'RTX', 'SPGI', 'LOW', 'T', 'IBM', 'GS', 'BA',
    'CAT', 'DE', 'AXP', 'MMM', 'HON', 'CVS', 'ANTM', 'CI', 'DUK', 'SO',
    'LMT', 'GE', 'F', 'GM', 'TGT', 'C', 'BLK', 'SCHW', 'FDX', 'USB',
    'PNC', 'MO', 'COP', 'CL', 'EMR', 'MET', 'AIG', 'DD', 'DOW', 'ITW',
  
    // Other popular tickers
    'UBER', 'LYFT', 'SPOT', 'SHOP', 'SQ', 'SNOW', 'PLTR', 'BABA', 'NIO', 'PTON',
    'RIVN', 'LCID', 'COIN', 'HOOD', 'SFIX', 'W', 'ETSY', 'PINS', 'TWTR', 'SNAP'
    // ... and thousands more across both exchanges
].sort();

interface TickerAutocompleteProps {
  value: string;
  onChange: (value: string) => void;
  onKeyPress?: (e: React.KeyboardEvent) => void;
  placeholder?: string;
}

export function TickerAutocomplete({
  value,
  onChange,
  onKeyPress,
  placeholder = 'Enter ticker symbol...'
}: TickerAutocompleteProps) {
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(-1);
  const wrapperRef = useRef<HTMLDivElement>(null);

  // Initialize Fuse.js for fuzzy searching
  const fuse = useMemo(() => {
    return new Fuse(POPULAR_TICKERS, {
      threshold: 0.3,
      distance: 100,
      includeScore: true,
      minMatchCharLength: 1,
    });
  }, []);

  // Handle clicks outside to close suggestions
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (wrapperRef.current && !wrapperRef.current.contains(event.target as Node)) {
        setShowSuggestions(false);
      }
    }

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Update suggestions based on input
  useEffect(() => {
    if (!value.trim()) {
      setSuggestions([]);
      setShowSuggestions(false);
      return;
    }

    // Fuzzy search
    const results = fuse.search(value.trim());
    const matches = results.slice(0, 10).map(result => result.item);
    
    setSuggestions(matches);
    setShowSuggestions(matches.length > 0);
    setSelectedIndex(-1);
  }, [value, fuse]);

  const handleSelect = (ticker: string) => {
    onChange(ticker);
    setShowSuggestions(false);
    setSelectedIndex(-1);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (!showSuggestions) {
      if (onKeyPress) onKeyPress(e);
      return;
    }

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setSelectedIndex(prev => 
          prev < suggestions.length - 1 ? prev + 1 : prev
        );
        break;
      case 'ArrowUp':
        e.preventDefault();
        setSelectedIndex(prev => prev > 0 ? prev - 1 : -1);
        break;
      case 'Enter':
        e.preventDefault();
        if (selectedIndex >= 0 && selectedIndex < suggestions.length) {
          handleSelect(suggestions[selectedIndex]);
        } else if (onKeyPress) {
          onKeyPress(e);
        }
        break;
      case 'Escape':
        setShowSuggestions(false);
        setSelectedIndex(-1);
        break;
      default:
        if (onKeyPress) onKeyPress(e);
    }
  };

  return (
    <div ref={wrapperRef} className="relative flex-1">
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <Input
          placeholder={placeholder}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onKeyDown={handleKeyDown}
          onFocus={() => {
            if (suggestions.length > 0) {
              setShowSuggestions(true);
            }
          }}
          className="pl-10 text-lg"
        />
      </div>

      {/* Suggestions Dropdown */}
      {showSuggestions && suggestions.length > 0 && (
        <div className="absolute z-50 w-full mt-1 bg-background border rounded-lg shadow-lg max-h-60 overflow-auto">
          {suggestions.map((ticker, index) => (
            <button
              key={ticker}
              onClick={() => handleSelect(ticker)}
              className={`w-full text-left px-4 py-2 hover:bg-accent transition-colors ${
                index === selectedIndex ? 'bg-accent' : ''
              }`}
            >
              <div className="flex items-center justify-between">
                <span className="font-medium">{ticker}</span>
                <span className="text-xs text-muted-foreground">
                  {ticker.endsWith('.NS') ? 'NSE' : 
                   ticker.endsWith('.BO') ? 'BSE' : 
                   ticker.includes('.') ? ticker.split('.')[1] : 'US'}
                </span>
              </div>
            </button>
          ))}
        </div>
      )}

      {/* Helper text */}
      <p className="text-xs text-muted-foreground mt-1">
        {POPULAR_TICKERS.length} popular tickers • Start typing to search
      </p>
    </div>
  );
}

