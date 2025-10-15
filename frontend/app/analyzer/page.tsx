'use client';

import { useState } from 'react';
import Link from 'next/link';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Skeleton } from '@/components/ui/skeleton';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Separator } from '@/components/ui/separator';
import { ArrowLeft, Search, TrendingUp, TrendingDown, AlertCircle, DollarSign, Activity } from 'lucide-react';
import { api, StockInfo, OHLCData, FundamentalData, TechnicalIndicators } from '@/lib/api';
import { formatNumber, formatLargeNumber, getRSIBadgeVariant, formatPercentage, formatPrice, formatLargeNumberWithCurrency, getCurrency } from '@/lib/utils';
import { StockChart } from '@/components/StockChart';
import { TickerAutocomplete } from '@/components/TickerAutocomplete';
import { DateRangePicker } from '@/components/DateRangePicker';
import { FundamentalsCard } from '@/components/FundamentalsCard';
import { FundamentalsCardEnhanced } from '@/components/FundamentalsCardEnhanced';
import { TechnicalIndicatorsCard } from '@/components/TechnicalIndicatorsCard';
import { DateRange } from 'react-day-picker';
import { format, subYears } from 'date-fns';

export default function AnalyzerPage() {
  const [ticker, setTicker] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [stockInfo, setStockInfo] = useState<StockInfo | null>(null);
  const [historicalData, setHistoricalData] = useState<OHLCData[] | null>(null);
  const [fundamentals, setFundamentals] = useState<FundamentalData | null>(null);
  const [fundamentalsHistory, setFundamentalsHistory] = useState<FundamentalData[] | null>(null);
  const [indicators, setIndicators] = useState<TechnicalIndicators | null>(null);
  const [chartPeriod, setChartPeriod] = useState('1y');
  const [dateRange, setDateRange] = useState<DateRange | undefined>({
    from: subYears(new Date(), 1),
    to: new Date(),
  });

  const fetchHistoricalData = async (tickerSymbol: string) => {
    try {
      const historyResult = await api.getHistoricalData(tickerSymbol, chartPeriod, '1d', true);
      
      // Filter data based on date range if specified
      let filteredData = historyResult.data;
      if (dateRange?.from && dateRange?.to) {
        const fromTime = dateRange.from.getTime();
        const toTime = dateRange.to.getTime();
        filteredData = historyResult.data.filter(item => {
          const itemTime = new Date(item.date).getTime();
          return itemTime >= fromTime && itemTime <= toTime;
        });
      }
      
      setHistoricalData(filteredData);
    } catch (err) {
      console.error('Failed to fetch historical data:', err);
    }
  };

  const handleAnalyze = async () => {
    if (!ticker.trim()) {
      setError('Please enter a ticker symbol');
      return;
    }

    setLoading(true);
    setError(null);
    setStockInfo(null);
    setHistoricalData(null);
    setFundamentals(null);
    setIndicators(null);

    try {
      const tickerUpper = ticker.trim().toUpperCase();
      
      // Fetch stock info
      const stockResult = await api.analyzeStock(tickerUpper, false);
      setStockInfo(stockResult);
      
      // Fetch historical data
      await fetchHistoricalData(tickerUpper);
      
      // Fetch fundamentals
      try {
        const fundamentalsResult = await api.getFundamentals(tickerUpper);
        setFundamentals(fundamentalsResult.data);
      } catch (err) {
        console.log('Fundamentals not available:', err);
      }
      
      // Fetch historical fundamentals
      try {
        const historyResult = await api.getFundamentalsHistory(tickerUpper);
        setFundamentalsHistory(historyResult.snapshots);
      } catch (err) {
        console.log('Historical fundamentals not available:', err);
      }
      
      // Fetch technical indicators
      try {
        const indicatorsResult = await api.getTechnicalIndicators(tickerUpper);
        setIndicators(indicatorsResult.latest);
      } catch (err) {
        console.log('Technical indicators not available:', err);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  // Refresh chart when date range changes
  const handleDateRangeChange = (range: DateRange | undefined) => {
    setDateRange(range);
    if (stockInfo && range?.from && range?.to) {
      fetchHistoricalData(stockInfo.ticker);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleAnalyze();
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-neutral-50 to-neutral-100 dark:from-neutral-950 dark:to-neutral-900">
      <div className="container mx-auto px-4 py-8 max-w-5xl">
        {/* Header */}
        <div className="mb-8">
          <Link href="/">
            <Button variant="ghost" className="mb-4">
              <ArrowLeft className="mr-2 h-4 w-4" />
              Back to Home
            </Button>
          </Link>
          <h1 className="text-4xl font-bold mb-2">Stock Analyzer</h1>
          <p className="text-muted-foreground">
            Get comprehensive technical and fundamental analysis for any stock
          </p>
        </div>

        {/* Search Bar */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Search Stock</CardTitle>
            <CardDescription>
              Search and select from NSE, BSE, or NASDAQ stocks
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex gap-2">
              <TickerAutocomplete
                value={ticker}
                onChange={setTicker}
                onKeyPress={handleKeyPress}
                placeholder="Start typing ticker or company name..."
              />
              <Button size="lg" onClick={handleAnalyze} disabled={loading}>
                <Search className="mr-2 h-4 w-4" />
                {loading ? 'Analyzing...' : 'Analyze'}
              </Button>
            </div>
            
            {/* Date Range Picker */}
            {stockInfo && (
              <div className="flex flex-col sm:flex-row sm:items-center gap-2">
                <span className="text-sm text-muted-foreground whitespace-nowrap">
                  Chart Period:
                </span>
                <div className="w-full sm:w-auto">
                  <DateRangePicker
                    dateRange={dateRange}
                    onDateRangeChange={handleDateRangeChange}
                  />
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Error Alert */}
        {error && (
          <Alert variant="destructive" className="mb-6">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* Loading State */}
        {loading && (
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <Skeleton className="h-8 w-48" />
                <Skeleton className="h-4 w-32 mt-2" />
              </CardHeader>
              <CardContent className="space-y-4">
                <Skeleton className="h-32 w-full" />
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <Skeleton className="h-6 w-32" />
                <Skeleton className="h-4 w-48 mt-2" />
              </CardHeader>
              <CardContent>
                <Skeleton className="h-[400px] w-full" />
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <Skeleton className="h-6 w-40" />
              </CardHeader>
              <CardContent>
                <Skeleton className="h-64 w-full" />
              </CardContent>
            </Card>
          </div>
        )}

        {/* Stock Analysis Results */}
        {stockInfo && !loading && (
          <div className="space-y-6">
            {/* Stock Header */}
            <Card>
              <CardHeader>
                <div className="flex justify-between items-start">
                  <div>
                    <CardTitle className="text-3xl">{stockInfo.ticker}</CardTitle>
                    <CardDescription className="text-base mt-2">
                      {stockInfo.fundamental.sector && (
                        <span className="font-medium">{stockInfo.fundamental.sector}</span>
                      )}
                      {stockInfo.fundamental.sector && stockInfo.fundamental.industry && ' • '}
                      {stockInfo.fundamental.industry}
                    </CardDescription>
                  </div>
                  <div className="text-right">
                    <div className="text-4xl font-bold text-primary">
                      {formatPrice(stockInfo.current_price, stockInfo.ticker)}
                    </div>
                    {stockInfo.technical?.rsi !== undefined && (
                      <Badge variant={getRSIBadgeVariant(stockInfo.technical.rsi)} className="mt-2">
                        RSI: {formatNumber(stockInfo.technical.rsi)}
                      </Badge>
                    )}
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  {stockInfo.fundamental.market_cap !== undefined && (
                    <div className="p-3 bg-secondary/50 rounded-lg">
                      <p className="text-xs text-muted-foreground mb-1">Market Cap</p>
                      <p className="text-lg font-semibold">
                        {formatLargeNumberWithCurrency(stockInfo.fundamental.market_cap, stockInfo.ticker)}
                      </p>
                    </div>
                  )}
                  {stockInfo.fundamental.trailing_pe !== undefined && (
                    <div className="p-3 bg-secondary/50 rounded-lg">
                      <p className="text-xs text-muted-foreground mb-1">P/E Ratio</p>
                      <p className="text-lg font-semibold">
                        {formatNumber(stockInfo.fundamental.trailing_pe)}
                      </p>
                    </div>
                  )}
                  {stockInfo.fundamental.beta !== undefined && (
                    <div className="p-3 bg-secondary/50 rounded-lg">
                      <p className="text-xs text-muted-foreground mb-1">Beta</p>
                      <p className="text-lg font-semibold">
                        {formatNumber(stockInfo.fundamental.beta)}
                      </p>
                    </div>
                  )}
                  {stockInfo.fundamental.dividend_yield !== undefined && (
                    <div className="p-3 bg-secondary/50 rounded-lg">
                      <p className="text-xs text-muted-foreground mb-1">Dividend Yield</p>
                      <p className="text-lg font-semibold">
                        {formatPercentage(stockInfo.fundamental.dividend_yield)}
                      </p>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Stock Chart */}
            {historicalData && historicalData.length > 0 && (
              <StockChart 
                data={historicalData} 
                ticker={stockInfo.ticker}
                period={chartPeriod.toUpperCase()}
              />
            )}

            {/* Enhanced Data Cards */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Technical Indicators Card */}
              {indicators && <TechnicalIndicatorsCard indicators={indicators} />}
              {!indicators && stockInfo.technical && <TechnicalIndicatorsCard indicators={stockInfo.technical} />}
              
              {/* Fundamentals Card - Enhanced with Historical Data */}
              {fundamentals && (
                <FundamentalsCardEnhanced 
                  fundamentals={fundamentals} 
                  historicalData={fundamentalsHistory || undefined}
                  ticker={stockInfo.ticker} 
                />
              )}
              {!fundamentals && stockInfo.fundamental && (
                <FundamentalsCard fundamentals={stockInfo.fundamental} ticker={stockInfo.ticker} />
              )}
            </div>

            {/* Detailed Analysis */}
            <Card>
              <CardHeader>
                <CardTitle>Detailed Analysis</CardTitle>
              </CardHeader>
              <CardContent>
                <Tabs defaultValue="technical" className="w-full">
                  <TabsList className="grid w-full grid-cols-2">
                    <TabsTrigger value="technical">
                      <Activity className="mr-2 h-4 w-4" />
                      Technical Indicators
                    </TabsTrigger>
                    <TabsTrigger value="fundamental">
                      <DollarSign className="mr-2 h-4 w-4" />
                      Fundamental Data
                    </TabsTrigger>
                  </TabsList>

                  {/* Technical Indicators Tab */}
                  <TabsContent value="technical" className="mt-6">
                    <div className="space-y-6">
                      {/* Momentum Indicators */}
                      <div>
                        <h3 className="font-semibold mb-3 text-primary">Momentum Indicators</h3>
                        <Table>
                          <TableHeader>
                            <TableRow>
                              <TableHead>Indicator</TableHead>
                              <TableHead className="text-right">Value</TableHead>
                            </TableRow>
                          </TableHeader>
                          <TableBody>
                            {stockInfo.technical?.rsi !== undefined && (
                              <TableRow>
                                <TableCell className="font-medium">RSI (14)</TableCell>
                                <TableCell className="text-right">
                                  <Badge variant={getRSIBadgeVariant(stockInfo.technical.rsi)}>
                                    {formatNumber(stockInfo.technical.rsi)}
                                  </Badge>
                                </TableCell>
                              </TableRow>
                            )}
                            {stockInfo.technical?.macd !== undefined && (
                              <TableRow>
                                <TableCell className="font-medium">MACD</TableCell>
                                <TableCell className="text-right">{formatNumber(stockInfo.technical.macd)}</TableCell>
                              </TableRow>
                            )}
                            {stockInfo.technical?.macd_signal !== undefined && (
                              <TableRow>
                                <TableCell className="font-medium">MACD Signal</TableCell>
                                <TableCell className="text-right">{formatNumber(stockInfo.technical.macd_signal)}</TableCell>
                              </TableRow>
                            )}
                            {stockInfo.technical?.macd_histogram !== undefined && (
                              <TableRow>
                                <TableCell className="font-medium">MACD Histogram</TableCell>
                                <TableCell className="text-right">{formatNumber(stockInfo.technical.macd_histogram)}</TableCell>
                              </TableRow>
                            )}
                            {stockInfo.technical?.stoch_k !== undefined && (
                              <TableRow>
                                <TableCell className="font-medium">Stochastic %K</TableCell>
                                <TableCell className="text-right">{formatNumber(stockInfo.technical.stoch_k)}</TableCell>
                              </TableRow>
                            )}
                            {stockInfo.technical?.stoch_d !== undefined && (
                              <TableRow>
                                <TableCell className="font-medium">Stochastic %D</TableCell>
                                <TableCell className="text-right">{formatNumber(stockInfo.technical.stoch_d)}</TableCell>
                              </TableRow>
                            )}
                          </TableBody>
                        </Table>
                      </div>

                      {/* Moving Averages */}
                      <div>
                        <h3 className="font-semibold mb-3 text-primary">Moving Averages</h3>
                        <Table>
                          <TableHeader>
                            <TableRow>
                              <TableHead>Period</TableHead>
                              <TableHead className="text-right">SMA</TableHead>
                              <TableHead className="text-right">EMA</TableHead>
                            </TableRow>
                          </TableHeader>
                          <TableBody>
                            <TableRow>
                              <TableCell className="font-medium">20-day</TableCell>
                              <TableCell className="text-right">
                                {stockInfo.technical?.sma_20 ? formatPrice(stockInfo.technical.sma_20, stockInfo.ticker) : 'N/A'}
                              </TableCell>
                              <TableCell className="text-right">N/A</TableCell>
                            </TableRow>
                            <TableRow>
                              <TableCell className="font-medium">50-day</TableCell>
                              <TableCell className="text-right">
                                {stockInfo.technical?.sma_50 ? formatPrice(stockInfo.technical.sma_50, stockInfo.ticker) : 'N/A'}
                              </TableCell>
                              <TableCell className="text-right">
                                {stockInfo.technical?.ema_50 ? formatPrice(stockInfo.technical.ema_50, stockInfo.ticker) : 'N/A'}
                              </TableCell>
                            </TableRow>
                            <TableRow>
                              <TableCell className="font-medium">100-day</TableCell>
                              <TableCell className="text-right">
                                {stockInfo.technical?.sma_100 ? formatPrice(stockInfo.technical.sma_100, stockInfo.ticker) : 'N/A'}
                              </TableCell>
                              <TableCell className="text-right">N/A</TableCell>
                            </TableRow>
                            <TableRow>
                              <TableCell className="font-medium">200-day</TableCell>
                              <TableCell className="text-right">
                                {stockInfo.technical?.sma_200 ? formatPrice(stockInfo.technical.sma_200, stockInfo.ticker) : 'N/A'}
                              </TableCell>
                              <TableCell className="text-right">
                                {stockInfo.technical?.ema_200 ? formatPrice(stockInfo.technical.ema_200, stockInfo.ticker) : 'N/A'}
                              </TableCell>
                            </TableRow>
                          </TableBody>
                        </Table>
                      </div>

                      {/* Volatility & Volume */}
                      <div>
                        <h3 className="font-semibold mb-3 text-primary">Volatility & Volume</h3>
                        <Table>
                          <TableHeader>
                            <TableRow>
                              <TableHead>Indicator</TableHead>
                              <TableHead className="text-right">Value</TableHead>
                            </TableRow>
                          </TableHeader>
                          <TableBody>
                            {stockInfo.technical?.atr !== undefined && (
                              <TableRow>
                                <TableCell className="font-medium">ATR (Average True Range)</TableCell>
                                <TableCell className="text-right">{formatNumber(stockInfo.technical.atr)}</TableCell>
                              </TableRow>
                            )}
                            {stockInfo.technical?.adx !== undefined && (
                              <TableRow>
                                <TableCell className="font-medium">ADX (Trend Strength)</TableCell>
                                <TableCell className="text-right">{formatNumber(stockInfo.technical.adx)}</TableCell>
                              </TableRow>
                            )}
                            {stockInfo.technical?.obv !== undefined && (
                              <TableRow>
                                <TableCell className="font-medium">OBV (On-Balance Volume)</TableCell>
                                <TableCell className="text-right">{formatLargeNumber(stockInfo.technical.obv)}</TableCell>
                              </TableRow>
                            )}
                            {stockInfo.technical?.bb_upper !== undefined && (
                              <TableRow>
                                <TableCell className="font-medium">Bollinger Upper</TableCell>
                                <TableCell className="text-right">{formatPrice(stockInfo.technical.bb_upper, stockInfo.ticker)}</TableCell>
                              </TableRow>
                            )}
                            {stockInfo.technical?.bb_middle !== undefined && (
                              <TableRow>
                                <TableCell className="font-medium">Bollinger Middle</TableCell>
                                <TableCell className="text-right">{formatPrice(stockInfo.technical.bb_middle, stockInfo.ticker)}</TableCell>
                              </TableRow>
                            )}
                            {stockInfo.technical?.bb_lower !== undefined && (
                              <TableRow>
                                <TableCell className="font-medium">Bollinger Lower</TableCell>
                                <TableCell className="text-right">{formatPrice(stockInfo.technical.bb_lower, stockInfo.ticker)}</TableCell>
                              </TableRow>
                            )}
                          </TableBody>
                        </Table>
                      </div>
                    </div>
                  </TabsContent>

                  {/* Fundamental Data Tab */}
                  <TabsContent value="fundamental" className="mt-6">
                    <div className="space-y-6">
                      {/* Valuation Metrics */}
                      <div>
                        <h3 className="font-semibold mb-3 text-primary">Valuation Metrics</h3>
                        <Table>
                          <TableHeader>
                            <TableRow>
                              <TableHead>Metric</TableHead>
                              <TableHead className="text-right">Value</TableHead>
                            </TableRow>
                          </TableHeader>
                          <TableBody>
                            {stockInfo.fundamental.trailing_pe !== undefined && (
                              <TableRow>
                                <TableCell className="font-medium">P/E Ratio (Trailing)</TableCell>
                                <TableCell className="text-right">{formatNumber(stockInfo.fundamental.trailing_pe)}</TableCell>
                              </TableRow>
                            )}
                            {stockInfo.fundamental.forward_pe !== undefined && (
                              <TableRow>
                                <TableCell className="font-medium">P/E Ratio (Forward)</TableCell>
                                <TableCell className="text-right">{formatNumber(stockInfo.fundamental.forward_pe)}</TableCell>
                              </TableRow>
                            )}
                            {stockInfo.fundamental.price_to_book !== undefined && (
                              <TableRow>
                                <TableCell className="font-medium">Price-to-Book</TableCell>
                                <TableCell className="text-right">{formatNumber(stockInfo.fundamental.price_to_book)}</TableCell>
                              </TableRow>
                            )}
                            {stockInfo.fundamental.market_cap !== undefined && (
                              <TableRow>
                                <TableCell className="font-medium">Market Capitalization</TableCell>
                                <TableCell className="text-right">{formatLargeNumberWithCurrency(stockInfo.fundamental.market_cap, stockInfo.ticker)}</TableCell>
                              </TableRow>
                            )}
                          </TableBody>
                        </Table>
                      </div>

                      {/* Financial Health */}
                      <div>
                        <h3 className="font-semibold mb-3 text-primary">Financial Health</h3>
                        <Table>
                          <TableHeader>
                            <TableRow>
                              <TableHead>Metric</TableHead>
                              <TableHead className="text-right">Value</TableHead>
                            </TableRow>
                          </TableHeader>
                          <TableBody>
                            {stockInfo.fundamental.debt_to_equity !== undefined && (
                              <TableRow>
                                <TableCell className="font-medium">Debt-to-Equity</TableCell>
                                <TableCell className="text-right">{formatNumber(stockInfo.fundamental.debt_to_equity)}</TableCell>
                              </TableRow>
                            )}
                            {stockInfo.fundamental.current_ratio !== undefined && (
                              <TableRow>
                                <TableCell className="font-medium">Current Ratio</TableCell>
                                <TableCell className="text-right">{formatNumber(stockInfo.fundamental.current_ratio)}</TableCell>
                              </TableRow>
                            )}
                          </TableBody>
                        </Table>
                      </div>

                      {/* Market & Returns */}
                      <div>
                        <h3 className="font-semibold mb-3 text-primary">Market & Returns</h3>
                        <Table>
                          <TableHeader>
                            <TableRow>
                              <TableHead>Metric</TableHead>
                              <TableHead className="text-right">Value</TableHead>
                            </TableRow>
                          </TableHeader>
                          <TableBody>
                            {stockInfo.fundamental.beta !== undefined && (
                              <TableRow>
                                <TableCell className="font-medium">Beta</TableCell>
                                <TableCell className="text-right">{formatNumber(stockInfo.fundamental.beta)}</TableCell>
                              </TableRow>
                            )}
                            {stockInfo.fundamental.dividend_yield !== undefined && (
                              <TableRow>
                                <TableCell className="font-medium">Dividend Yield</TableCell>
                                <TableCell className="text-right">{formatPercentage(stockInfo.fundamental.dividend_yield)}</TableCell>
                              </TableRow>
                            )}
                          </TableBody>
                        </Table>
                      </div>

                      {/* Company Info */}
                      {(stockInfo.fundamental.sector || stockInfo.fundamental.industry) && (
                        <div>
                          <h3 className="font-semibold mb-3 text-primary">Company Information</h3>
                          <Table>
                            <TableBody>
                              {stockInfo.fundamental.sector && (
                                <TableRow>
                                  <TableCell className="font-medium">Sector</TableCell>
                                  <TableCell className="text-right">{stockInfo.fundamental.sector}</TableCell>
                                </TableRow>
                              )}
                              {stockInfo.fundamental.industry && (
                                <TableRow>
                                  <TableCell className="font-medium">Industry</TableCell>
                                  <TableCell className="text-right">{stockInfo.fundamental.industry}</TableCell>
                                </TableRow>
                              )}
                            </TableBody>
                          </Table>
                        </div>
                      )}
                    </div>
                  </TabsContent>
                </Tabs>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Empty State */}
        {!stockInfo && !loading && !error && (
          <Card>
            <CardContent className="text-center py-16">
              <Search className="h-16 w-16 mx-auto mb-4 text-muted-foreground opacity-50" />
              <h3 className="text-xl font-semibold mb-2">No Stock Selected</h3>
              <p className="text-muted-foreground">
                Enter a ticker symbol above to view detailed analysis
              </p>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}

