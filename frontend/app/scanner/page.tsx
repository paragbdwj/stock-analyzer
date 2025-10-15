'use client';

import { useState } from 'react';
import Link from 'next/link';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Skeleton } from '@/components/ui/skeleton';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Separator } from '@/components/ui/separator';
import { ArrowLeft, Plus, Trash2, Search, TrendingUp, TrendingDown, AlertCircle } from 'lucide-react';
import { api, Filter, ScanResult, StockInfo } from '@/lib/api';
import { formatNumber, formatLargeNumber, getRSIBadgeVariant, formatPercentage } from '@/lib/utils';

const EXCHANGES = ['NSE', 'BSE', 'NASDAQ', 'NYSE'];

const TECHNICAL_FIELDS = [
  { value: 'rsi', label: 'RSI' },
  { value: 'sma_20', label: 'SMA 20' },
  { value: 'sma_50', label: 'SMA 50' },
  { value: 'sma_100', label: 'SMA 100' },
  { value: 'sma_200', label: 'SMA 200' },
  { value: 'ema_12', label: 'EMA 12' },
  { value: 'ema_26', label: 'EMA 26' },
  { value: 'ema_50', label: 'EMA 50' },
  { value: 'ema_200', label: 'EMA 200' },
  { value: 'macd', label: 'MACD' },
  { value: 'macd_signal', label: 'MACD Signal' },
  { value: 'macd_histogram', label: 'MACD Histogram' },
  { value: 'atr', label: 'ATR' },
  { value: 'adx', label: 'ADX' },
  { value: 'obv', label: 'OBV' },
];

const FUNDAMENTAL_FIELDS = [
  { value: 'trailing_pe', label: 'P/E Ratio (Trailing)' },
  { value: 'forward_pe', label: 'P/E Ratio (Forward)' },
  { value: 'price_to_book', label: 'Price-to-Book' },
  { value: 'debt_to_equity', label: 'Debt-to-Equity' },
  { value: 'current_ratio', label: 'Current Ratio' },
  { value: 'market_cap', label: 'Market Cap' },
  { value: 'beta', label: 'Beta' },
  { value: 'dividend_yield', label: 'Dividend Yield' },
];

const OPERATORS = [
  { value: '<', label: '<' },
  { value: '>', label: '>' },
  { value: '<=', label: '<=' },
  { value: '>=', label: '>=' },
  { value: '==', label: '==' },
  { value: '!=', label: '!=' },
];

export default function ScannerPage() {
  const [exchange, setExchange] = useState('NSE');
  const [technicalFilters, setTechnicalFilters] = useState<Filter[]>([]);
  const [fundamentalFilters, setFundamentalFilters] = useState<Filter[]>([]);
  const [filterLogic, setFilterLogic] = useState<'AND' | 'OR'>('AND');
  const [customTickers, setCustomTickers] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [scanResult, setScanResult] = useState<ScanResult | null>(null);

  const addTechnicalFilter = () => {
    setTechnicalFilters([...technicalFilters, { field: 'rsi', operator: '<', value: 30 }]);
  };

  const addFundamentalFilter = () => {
    setFundamentalFilters([...fundamentalFilters, { field: 'trailing_pe', operator: '<', value: 20 }]);
  };

  const removeTechnicalFilter = (index: number) => {
    setTechnicalFilters(technicalFilters.filter((_, i) => i !== index));
  };

  const removeFundamentalFilter = (index: number) => {
    setFundamentalFilters(fundamentalFilters.filter((_, i) => i !== index));
  };

  const updateTechnicalFilter = (index: number, field: keyof Filter, value: any) => {
    const newFilters = [...technicalFilters];
    newFilters[index] = { ...newFilters[index], [field]: value };
    setTechnicalFilters(newFilters);
  };

  const updateFundamentalFilter = (index: number, field: keyof Filter, value: any) => {
    const newFilters = [...fundamentalFilters];
    newFilters[index] = { ...newFilters[index], [field]: value };
    setFundamentalFilters(newFilters);
  };

  const handleScan = async () => {
    setLoading(true);
    setError(null);
    setScanResult(null);

    try {
      const tickers = customTickers
        ? customTickers.split(',').map(t => t.trim()).filter(t => t)
        : undefined;

      const result = await api.scanStocks({
        exchange,
        tickers,
        technical_filters: technicalFilters.length > 0 ? technicalFilters : undefined,
        fundamental_filters: fundamentalFilters.length > 0 ? fundamentalFilters : undefined,
        filter_logic: filterLogic,
        force_refresh: false,
      });

      setScanResult(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-neutral-50 to-neutral-100 dark:from-neutral-950 dark:to-neutral-900">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <Link href="/">
            <Button variant="ghost" className="mb-4">
              <ArrowLeft className="mr-2 h-4 w-4" />
              Back to Home
            </Button>
          </Link>
          <h1 className="text-4xl font-bold mb-2">Stock Scanner</h1>
          <p className="text-muted-foreground">
            Scan stocks using advanced technical and fundamental filters
          </p>
        </div>

        <div className="grid lg:grid-cols-3 gap-6">
          {/* Filters Panel */}
          <div className="lg:col-span-1 space-y-6">
            {/* Basic Settings */}
            <Card>
              <CardHeader>
                <CardTitle>Scan Settings</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label>Exchange</Label>
                  <Select value={exchange} onValueChange={setExchange}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {EXCHANGES.map(ex => (
                        <SelectItem key={ex} value={ex}>{ex}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label>Custom Tickers (optional)</Label>
                  <Input
                    placeholder="e.g., RELIANCE.NS, TCS.NS"
                    value={customTickers}
                    onChange={(e) => setCustomTickers(e.target.value)}
                  />
                  <p className="text-xs text-muted-foreground mt-1">
                    Comma-separated list
                  </p>
                </div>

                <div>
                  <Label>Filter Logic</Label>
                  <Select value={filterLogic} onValueChange={(val) => setFilterLogic(val as 'AND' | 'OR')}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="AND">AND (all must match)</SelectItem>
                      <SelectItem value="OR">OR (any can match)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </CardContent>
            </Card>

            {/* Technical Filters */}
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle>Technical Filters</CardTitle>
                  <Button size="sm" variant="outline" onClick={addTechnicalFilter}>
                    <Plus className="h-4 w-4" />
                  </Button>
                </div>
                <CardDescription>
                  {technicalFilters.length} filter(s) active
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                {technicalFilters.map((filter, index) => (
                  <div key={index} className="p-3 border rounded-lg space-y-2">
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-sm font-medium">Filter {index + 1}</span>
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => removeTechnicalFilter(index)}
                      >
                        <Trash2 className="h-3 w-3" />
                      </Button>
                    </div>
                    <Select
                      value={filter.field}
                      onValueChange={(val) => updateTechnicalFilter(index, 'field', val)}
                    >
                      <SelectTrigger className="h-8 text-sm">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {TECHNICAL_FIELDS.map(f => (
                          <SelectItem key={f.value} value={f.value}>{f.label}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <div className="grid grid-cols-2 gap-2">
                      <Select
                        value={filter.operator}
                        onValueChange={(val) => updateTechnicalFilter(index, 'operator', val)}
                      >
                        <SelectTrigger className="h-8 text-sm">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          {OPERATORS.map(op => (
                            <SelectItem key={op.value} value={op.value}>{op.label}</SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                      <Input
                        type="number"
                        className="h-8 text-sm"
                        value={filter.value}
                        onChange={(e) => updateTechnicalFilter(index, 'value', parseFloat(e.target.value))}
                      />
                    </div>
                  </div>
                ))}
                {technicalFilters.length === 0 && (
                  <p className="text-sm text-muted-foreground text-center py-4">
                    No technical filters added
                  </p>
                )}
              </CardContent>
            </Card>

            {/* Fundamental Filters */}
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle>Fundamental Filters</CardTitle>
                  <Button size="sm" variant="outline" onClick={addFundamentalFilter}>
                    <Plus className="h-4 w-4" />
                  </Button>
                </div>
                <CardDescription>
                  {fundamentalFilters.length} filter(s) active
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                {fundamentalFilters.map((filter, index) => (
                  <div key={index} className="p-3 border rounded-lg space-y-2">
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-sm font-medium">Filter {index + 1}</span>
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => removeFundamentalFilter(index)}
                      >
                        <Trash2 className="h-3 w-3" />
                      </Button>
                    </div>
                    <Select
                      value={filter.field}
                      onValueChange={(val) => updateFundamentalFilter(index, 'field', val)}
                    >
                      <SelectTrigger className="h-8 text-sm">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {FUNDAMENTAL_FIELDS.map(f => (
                          <SelectItem key={f.value} value={f.value}>{f.label}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <div className="grid grid-cols-2 gap-2">
                      <Select
                        value={filter.operator}
                        onValueChange={(val) => updateFundamentalFilter(index, 'operator', val)}
                      >
                        <SelectTrigger className="h-8 text-sm">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          {OPERATORS.map(op => (
                            <SelectItem key={op.value} value={op.value}>{op.label}</SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                      <Input
                        type="number"
                        className="h-8 text-sm"
                        value={filter.value}
                        onChange={(e) => updateFundamentalFilter(index, 'value', parseFloat(e.target.value))}
                      />
                    </div>
                  </div>
                ))}
                {fundamentalFilters.length === 0 && (
                  <p className="text-sm text-muted-foreground text-center py-4">
                    No fundamental filters added
                  </p>
                )}
              </CardContent>
            </Card>

            <Button 
              className="w-full" 
              size="lg" 
              onClick={handleScan}
              disabled={loading || (technicalFilters.length === 0 && fundamentalFilters.length === 0)}
            >
              <Search className="mr-2 h-4 w-4" />
              {loading ? 'Scanning...' : 'Run Scan'}
            </Button>
          </div>

          {/* Results Panel */}
          <div className="lg:col-span-2">
            <Card>
              <CardHeader>
                <CardTitle>Scan Results</CardTitle>
                {scanResult && (
                  <CardDescription>
                    Found {scanResult.total_matched} matching stocks out of {scanResult.total_scanned} scanned
                    ({scanResult.scan_duration_seconds.toFixed(2)}s)
                  </CardDescription>
                )}
              </CardHeader>
              <CardContent>
                {error && (
                  <Alert variant="destructive">
                    <AlertCircle className="h-4 w-4" />
                    <AlertDescription>{error}</AlertDescription>
                  </Alert>
                )}

                {loading && (
                  <div className="space-y-3">
                    <Skeleton className="h-12 w-full" />
                    <Skeleton className="h-12 w-full" />
                    <Skeleton className="h-12 w-full" />
                  </div>
                )}

                {scanResult && !loading && (
                  <div className="space-y-4">
                    {scanResult.stocks.length === 0 ? (
                      <p className="text-center text-muted-foreground py-8">
                        No stocks matched your criteria
                      </p>
                    ) : (
                      <div className="space-y-4">
                        {scanResult.stocks.map((stock) => (
                          <StockCard key={stock.ticker} stock={stock} />
                        ))}
                      </div>
                    )}
                  </div>
                )}

                {!scanResult && !loading && !error && (
                  <div className="text-center py-12 text-muted-foreground">
                    <Search className="h-12 w-12 mx-auto mb-4 opacity-50" />
                    <p>Configure filters and click "Run Scan" to start</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}

function StockCard({ stock }: { stock: StockInfo }) {
  return (
    <Card className="hover:shadow-md transition-shadow">
      <CardHeader className="pb-3">
        <div className="flex justify-between items-start">
          <div>
            <CardTitle className="text-xl">{stock.ticker}</CardTitle>
            <CardDescription>
              {stock.fundamental.sector && `${stock.fundamental.sector} • `}
              {stock.fundamental.industry}
            </CardDescription>
          </div>
          <div className="text-right">
            <div className="text-2xl font-bold">${formatNumber(stock.current_price)}</div>
            {stock.technical.rsi !== undefined && (
              <Badge variant={getRSIBadgeVariant(stock.technical.rsi)} className="mt-1">
                RSI: {formatNumber(stock.technical.rsi)}
              </Badge>
            )}
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="technical" className="w-full">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="technical">Technical</TabsTrigger>
            <TabsTrigger value="fundamental">Fundamental</TabsTrigger>
          </TabsList>
          <TabsContent value="technical" className="space-y-2">
            <div className="grid grid-cols-2 gap-2 text-sm">
              {stock.technical.rsi !== undefined && (
                <div className="flex justify-between">
                  <span className="text-muted-foreground">RSI:</span>
                  <span className="font-medium">{formatNumber(stock.technical.rsi)}</span>
                </div>
              )}
              {stock.technical.macd !== undefined && (
                <div className="flex justify-between">
                  <span className="text-muted-foreground">MACD:</span>
                  <span className="font-medium">{formatNumber(stock.technical.macd)}</span>
                </div>
              )}
              {stock.technical.sma_50 !== undefined && (
                <div className="flex justify-between">
                  <span className="text-muted-foreground">SMA 50:</span>
                  <span className="font-medium">${formatNumber(stock.technical.sma_50)}</span>
                </div>
              )}
              {stock.technical.sma_200 !== undefined && (
                <div className="flex justify-between">
                  <span className="text-muted-foreground">SMA 200:</span>
                  <span className="font-medium">${formatNumber(stock.technical.sma_200)}</span>
                </div>
              )}
              {stock.technical.adx !== undefined && (
                <div className="flex justify-between">
                  <span className="text-muted-foreground">ADX:</span>
                  <span className="font-medium">{formatNumber(stock.technical.adx)}</span>
                </div>
              )}
            </div>
          </TabsContent>
          <TabsContent value="fundamental" className="space-y-2">
            <div className="grid grid-cols-2 gap-2 text-sm">
              {stock.fundamental.trailing_pe !== undefined && (
                <div className="flex justify-between">
                  <span className="text-muted-foreground">P/E Ratio:</span>
                  <span className="font-medium">{formatNumber(stock.fundamental.trailing_pe)}</span>
                </div>
              )}
              {stock.fundamental.market_cap !== undefined && (
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Market Cap:</span>
                  <span className="font-medium">{formatLargeNumber(stock.fundamental.market_cap)}</span>
                </div>
              )}
              {stock.fundamental.debt_to_equity !== undefined && (
                <div className="flex justify-between">
                  <span className="text-muted-foreground">D/E Ratio:</span>
                  <span className="font-medium">{formatNumber(stock.fundamental.debt_to_equity)}</span>
                </div>
              )}
              {stock.fundamental.dividend_yield !== undefined && (
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Div Yield:</span>
                  <span className="font-medium">{formatPercentage(stock.fundamental.dividend_yield)}</span>
                </div>
              )}
              {stock.fundamental.beta !== undefined && (
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Beta:</span>
                  <span className="font-medium">{formatNumber(stock.fundamental.beta)}</span>
                </div>
              )}
            </div>
          </TabsContent>
        </Tabs>

        {stock.matched_filters && stock.matched_filters.length > 0 && (
          <>
            <Separator className="my-3" />
            <div>
              <p className="text-xs font-semibold text-muted-foreground mb-2">Matched Filters:</p>
              <div className="flex flex-wrap gap-1">
                {stock.matched_filters.map((filter, idx) => (
                  <Badge key={idx} variant="secondary" className="text-xs">
                    {filter}
                  </Badge>
                ))}
              </div>
            </div>
          </>
        )}
      </CardContent>
    </Card>
  );
}

