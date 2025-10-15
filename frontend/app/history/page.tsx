'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Separator } from '@/components/ui/separator';
import { Skeleton } from '@/components/ui/skeleton';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { ArrowLeft, Calendar, TrendingUp, BarChart3, Activity, DollarSign, Building2, AlertCircle } from 'lucide-react';
import { api, FundamentalData, TechnicalIndicators, OHLCData } from '@/lib/api';
import { formatNumber, formatPercentage, formatPrice, formatLargeNumberWithCurrency, getRSIBadgeVariant } from '@/lib/utils';
import { TickerAutocomplete } from '@/components/TickerAutocomplete';
import { DateRangePicker } from '@/components/DateRangePicker';
import { DateRange } from 'react-day-picker';
import { format, subYears } from 'date-fns';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, CandlestickChart, Candle } from 'recharts';
import { CandlestickChart as CandlestickChartComponent } from '@/components/CandlestickChart';

export default function HistoricalAnalysisPage() {
  const [ticker, setTicker] = useState('');
  const [selectedDate, setSelectedDate] = useState<Date>(new Date());
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Data states
  const [fundamentalsHistory, setFundamentalsHistory] = useState<FundamentalData[] | null>(null);
  const [selectedFundamental, setSelectedFundamental] = useState<FundamentalData | null>(null);
  const [indicatorsHistory, setIndicatorsHistory] = useState<any[] | null>(null);
  const [selectedIndicators, setSelectedIndicators] = useState<TechnicalIndicators | null>(null);
  const [ohlcvData, setOhlcvData] = useState<OHLCData[] | null>(null);
  const [selectedOhlcv, setSelectedOhlcv] = useState<OHLCData | null>(null);

  const handleAnalyze = async () => {
    if (!ticker.trim()) {
      setError('Please enter a ticker symbol');
      return;
    }

    setLoading(true);
    setError(null);
    setFundamentalsHistory(null);
    setIndicatorsHistory(null);
    setOhlcvData(null);

    try {
      const tickerUpper = ticker.trim().toUpperCase();
      
      // Fetch fundamentals history
      try {
        const fundamentalsResult = await api.getFundamentalsHistory(tickerUpper);
        setFundamentalsHistory(fundamentalsResult.snapshots);
        if (fundamentalsResult.snapshots.length > 0) {
          setSelectedFundamental(fundamentalsResult.snapshots[0]);
        }
      } catch (err) {
        console.log('Fundamentals history not available:', err);
      }
      
      // Fetch technical indicators history
      try {
        const indicatorsResult = await api.getTechnicalIndicators(tickerUpper);
        setIndicatorsHistory(indicatorsResult.time_series);
        if (indicatorsResult.time_series.length > 0) {
          // Find indicators for selected date
          const dateStr = format(selectedDate, 'yyyy-MM-dd');
          const matching = indicatorsResult.time_series.find((ind: any) => ind.date.startsWith(dateStr));
          if (matching) {
            setSelectedIndicators(matching);
          }
        }
      } catch (err) {
        console.log('Technical indicators history not available:', err);
      }
      
      // Fetch OHLCV data
      try {
        const historyResult = await api.getHistoricalData(tickerUpper, '5y', '1d', true);
        setOhlcvData(historyResult.data);
        // Find OHLCV for selected date
        const dateStr = format(selectedDate, 'yyyy-MM-dd');
        const matching = historyResult.data.find((d: OHLCData) => d.date.startsWith(dateStr));
        if (matching) {
          setSelectedOhlcv(matching);
        }
      } catch (err) {
        console.log('OHLCV data not available:', err);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleDateChange = (date: Date) => {
    setSelectedDate(date);
    
    // Update selected data based on new date
    const dateStr = format(date, 'yyyy-MM-dd');
    
    // Find matching fundamental
    if (fundamentalsHistory) {
      const matching = fundamentalsHistory.find(f => {
        if (f.timestamp) {
          return f.timestamp.startsWith(dateStr);
        }
        return false;
      });
      if (matching) {
        setSelectedFundamental(matching);
      }
    }
    
    // Find matching indicators
    if (indicatorsHistory) {
      const matching = indicatorsHistory.find((ind: any) => ind.date.startsWith(dateStr));
      if (matching) {
        setSelectedIndicators(matching);
      }
    }
    
    // Find matching OHLCV
    if (ohlcvData) {
      const matching = ohlcvData.find(d => d.date.startsWith(dateStr));
      if (matching) {
        setSelectedOhlcv(matching);
      }
    }
  };

  const renderMetric = (label: string, value: number | string | undefined, format: 'number' | 'percentage' | 'currency' | 'ratio' | 'text' = 'number') => {
    if (value === undefined || value === null) return null;
    
    let displayValue: string;
    switch (format) {
      case 'percentage':
        displayValue = formatPercentage(Number(value));
        break;
      case 'currency':
        displayValue = formatLargeNumberWithCurrency(Number(value), ticker);
        break;
      case 'ratio':
        displayValue = formatNumber(Number(value), 2);
        break;
      case 'text':
        displayValue = String(value);
        break;
      default:
        displayValue = formatNumber(Number(value), 2);
    }

    return (
      <div className="flex justify-between items-center py-2">
        <span className="text-sm text-muted-foreground">{label}</span>
        <span className="text-sm font-semibold">{displayValue}</span>
      </div>
    );
  };

  const renderTrendChart = (data: any[], metric: string, label: string) => {
    if (!data || data.length === 0) return null;

    const chartData = data
      .map(item => ({
        date: new Date(item.date || item.timestamp).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
        value: item[metric],
      }))
      .filter(d => d.value !== null && d.value !== undefined);

    if (chartData.length === 0) return null;

    return (
      <div className="mt-4">
        <h5 className="text-xs font-semibold mb-2">{label}</h5>
        <ResponsiveContainer width="100%" height={100}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.1} />
            <XAxis dataKey="date" tick={{ fontSize: 10 }} stroke="#6b7280" />
            <YAxis tick={{ fontSize: 10 }} stroke="#6b7280" />
            <Tooltip
              contentStyle={{ backgroundColor: '#1f2937', border: 'none', borderRadius: '6px', fontSize: '12px' }}
            />
            <Line type="monotone" dataKey="value" stroke="#3b82f6" strokeWidth={2} dot={{ r: 3 }} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-neutral-50 to-neutral-100 dark:from-neutral-950 dark:to-neutral-900">
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        {/* Header */}
        <div className="mb-8">
          <Link href="/">
            <Button variant="ghost" className="mb-4">
              <ArrowLeft className="mr-2 h-4 w-4" />
              Back to Home
            </Button>
          </Link>
          <h1 className="text-4xl font-bold mb-2">Historical Analysis</h1>
          <p className="text-muted-foreground">
            View complete fundamental and technical analysis for any date in the past
          </p>
        </div>

        {/* Search and Date Selection */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Select Stock & Date</CardTitle>
            <CardDescription>
              Choose a ticker and date to view historical analysis
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex gap-2">
              <TickerAutocomplete
                value={ticker}
                onChange={setTicker}
                placeholder="Start typing ticker or company name..."
                className="flex-1"
              />
              <Button size="lg" onClick={handleAnalyze} disabled={loading}>
                <Calendar className="mr-2 h-4 w-4" />
                {loading ? 'Loading...' : 'Analyze'}
              </Button>
            </div>
            
            {fundamentalsHistory && (
              <div className="flex flex-col sm:flex-row sm:items-center gap-2">
                <span className="text-sm text-muted-foreground whitespace-nowrap">
                  Select Date:
                </span>
                <input
                  type="date"
                  value={format(selectedDate, 'yyyy-MM-dd')}
                  onChange={(e) => handleDateChange(new Date(e.target.value))}
                  className="px-3 py-2 border rounded-md bg-background"
                  max={format(new Date(), 'yyyy-MM-dd')}
                />
                <Badge variant="outline">
                  {fundamentalsHistory.length} snapshots available
                </Badge>
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
              </CardHeader>
              <CardContent>
                <Skeleton className="h-64 w-full" />
              </CardContent>
            </Card>
          </div>
        )}

        {/* Analysis Results */}
        {!loading && (selectedFundamental || selectedIndicators || selectedOhlcv) && (
          <div className="space-y-6">
            {/* Selected Date Info */}
            <Card>
              <CardHeader>
                <div className="flex justify-between items-center">
                  <div>
                    <CardTitle className="text-2xl">{ticker}</CardTitle>
                    <CardDescription className="text-base mt-2">
                      Analysis for {format(selectedDate, 'MMMM dd, yyyy')}
                    </CardDescription>
                  </div>
                  <Badge variant="secondary" className="text-lg px-4 py-2">
                    {format(selectedDate, 'MMM dd, yyyy')}
                  </Badge>
                </div>
              </CardHeader>
            </Card>

            {/* OHLCV Data */}
            {selectedOhlcv && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <BarChart3 className="h-5 w-5" />
                    OHLCV Data
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                    <div className="p-3 bg-secondary/50 rounded-lg">
                      <p className="text-xs text-muted-foreground mb-1">Open</p>
                      <p className="text-lg font-semibold">
                        {formatPrice(selectedOhlcv.open, ticker)}
                      </p>
                    </div>
                    <div className="p-3 bg-secondary/50 rounded-lg">
                      <p className="text-xs text-muted-foreground mb-1">High</p>
                      <p className="text-lg font-semibold text-green-600">
                        {formatPrice(selectedOhlcv.high, ticker)}
                      </p>
                    </div>
                    <div className="p-3 bg-secondary/50 rounded-lg">
                      <p className="text-xs text-muted-foreground mb-1">Low</p>
                      <p className="text-lg font-semibold text-red-600">
                        {formatPrice(selectedOhlcv.low, ticker)}
                      </p>
                    </div>
                    <div className="p-3 bg-secondary/50 rounded-lg">
                      <p className="text-xs text-muted-foreground mb-1">Close</p>
                      <p className="text-lg font-semibold">
                        {formatPrice(selectedOhlcv.close, ticker)}
                      </p>
                    </div>
                    <div className="p-3 bg-secondary/50 rounded-lg">
                      <p className="text-xs text-muted-foreground mb-1">Volume</p>
                      <p className="text-lg font-semibold">
                        {selectedOhlcv.volume.toLocaleString()}
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Detailed Analysis Tabs */}
            <Card>
              <CardHeader>
                <CardTitle>Complete Analysis</CardTitle>
              </CardHeader>
              <CardContent>
                <Tabs defaultValue="fundamentals" className="w-full">
                  <TabsList className="grid w-full grid-cols-2">
                    <TabsTrigger value="fundamentals">
                      <DollarSign className="mr-2 h-4 w-4" />
                      Fundamentals
                    </TabsTrigger>
                    <TabsTrigger value="technical">
                      <Activity className="mr-2 h-4 w-4" />
                      Technical Indicators
                    </TabsTrigger>
                  </TabsList>

                  {/* Fundamentals Tab */}
                  <TabsContent value="fundamentals" className="mt-6">
                    {selectedFundamental ? (
                      <div className="space-y-6">
                        {/* Valuation Metrics */}
                        <div>
                          <h3 className="font-semibold mb-3 text-primary flex items-center gap-2">
                            <DollarSign className="h-4 w-4" />
                            Valuation Metrics
                          </h3>
                          <div className="space-y-1">
                            {renderMetric('Market Cap', selectedFundamental.market_cap, 'currency')}
                            {renderMetric('Enterprise Value', selectedFundamental.enterprise_value, 'currency')}
                            {renderMetric('Trailing P/E', selectedFundamental.trailing_pe, 'ratio')}
                            {renderMetric('Forward P/E', selectedFundamental.forward_pe, 'ratio')}
                            {renderMetric('Price to Book', selectedFundamental.price_to_book, 'ratio')}
                            {renderMetric('PEG Ratio', selectedFundamental.peg_ratio, 'ratio')}
                          </div>
                          {fundamentalsHistory && renderTrendChart(fundamentalsHistory, 'trailing_pe', 'P/E Ratio Trend')}
                        </div>

                        <Separator />

                        {/* Profitability */}
                        <div>
                          <h3 className="font-semibold mb-3 text-primary flex items-center gap-2">
                            <TrendingUp className="h-4 w-4" />
                            Profitability
                          </h3>
                          <div className="space-y-1">
                            {renderMetric('Profit Margin', selectedFundamental.profit_margin, 'percentage')}
                            {renderMetric('Operating Margin', selectedFundamental.operating_margin, 'percentage')}
                            {renderMetric('Return on Assets', selectedFundamental.return_on_assets, 'percentage')}
                            {renderMetric('Return on Equity', selectedFundamental.return_on_equity, 'percentage')}
                          </div>
                          {fundamentalsHistory && renderTrendChart(fundamentalsHistory, 'profit_margin', 'Profit Margin Trend')}
                        </div>

                        <Separator />

                        {/* Growth */}
                        <div>
                          <h3 className="font-semibold mb-3 text-primary flex items-center gap-2">
                            <Activity className="h-4 w-4" />
                            Growth & Dividends
                          </h3>
                          <div className="space-y-1">
                            {renderMetric('Revenue Growth', selectedFundamental.revenue_growth, 'percentage')}
                            {renderMetric('Earnings Growth', selectedFundamental.earnings_growth, 'percentage')}
                            {renderMetric('Dividend Yield', selectedFundamental.dividend_yield, 'percentage')}
                            {renderMetric('Payout Ratio', selectedFundamental.payout_ratio, 'percentage')}
                          </div>
                          {fundamentalsHistory && renderTrendChart(fundamentalsHistory, 'revenue_growth', 'Revenue Growth Trend')}
                        </div>

                        <Separator />

                        {/* Financial Health */}
                        <div>
                          <h3 className="font-semibold mb-3 text-primary flex items-center gap-2">
                            <Building2 className="h-4 w-4" />
                            Financial Health
                          </h3>
                          <div className="space-y-1">
                            {renderMetric('Debt to Equity', selectedFundamental.debt_to_equity, 'ratio')}
                            {renderMetric('Current Ratio', selectedFundamental.current_ratio, 'ratio')}
                            {renderMetric('Quick Ratio', selectedFundamental.quick_ratio, 'ratio')}
                            {renderMetric('Beta', selectedFundamental.beta, 'ratio')}
                          </div>
                        </div>
                      </div>
                    ) : (
                      <div className="text-center py-8 text-muted-foreground">
                        No fundamental data available for this date
                      </div>
                    )}
                  </TabsContent>

                  {/* Technical Indicators Tab */}
                  <TabsContent value="technical" className="mt-6">
                    {selectedIndicators ? (
                      <div className="space-y-6">
                        {/* Momentum Indicators */}
                        <div>
                          <h3 className="font-semibold mb-3 text-primary">Momentum Indicators</h3>
                          <div className="space-y-1">
                            {renderMetric('RSI (14)', selectedIndicators.rsi, 'number')}
                            {renderMetric('MACD', selectedIndicators.macd, 'number')}
                            {renderMetric('MACD Signal', selectedIndicators.macd_signal, 'number')}
                            {renderMetric('Stochastic K', selectedIndicators.stoch_k, 'number')}
                            {renderMetric('Stochastic D', selectedIndicators.stoch_d, 'number')}
                          </div>
                        </div>

                        <Separator />

                        {/* Moving Averages */}
                        <div>
                          <h3 className="font-semibold mb-3 text-primary">Moving Averages</h3>
                          <div className="space-y-1">
                            {renderMetric('SMA 20', selectedIndicators.sma_20, 'number')}
                            {renderMetric('SMA 50', selectedIndicators.sma_50, 'number')}
                            {renderMetric('SMA 100', selectedIndicators.sma_100, 'number')}
                            {renderMetric('SMA 200', selectedIndicators.sma_200, 'number')}
                            {renderMetric('EMA 50', selectedIndicators.ema_50, 'number')}
                            {renderMetric('EMA 200', selectedIndicators.ema_200, 'number')}
                          </div>
                        </div>

                        <Separator />

                        {/* Volatility */}
                        <div>
                          <h3 className="font-semibold mb-3 text-primary">Volatility</h3>
                          <div className="space-y-1">
                            {renderMetric('ATR (14)', selectedIndicators.atr, 'number')}
                            {renderMetric('Bollinger Upper', selectedIndicators.bb_upper, 'number')}
                            {renderMetric('Bollinger Lower', selectedIndicators.bb_lower, 'number')}
                            {renderMetric('20-Day Volatility', selectedIndicators.volatility_20d, 'percentage')}
                          </div>
                        </div>

                        <Separator />

                        {/* Volume & Returns */}
                        <div>
                          <h3 className="font-semibold mb-3 text-primary">Volume & Returns</h3>
                          <div className="space-y-1">
                            {renderMetric('OBV', selectedIndicators.obv, 'number')}
                            {renderMetric('Daily Return', selectedIndicators.daily_return, 'percentage')}
                            {renderMetric('Cumulative Return', selectedIndicators.cumulative_return, 'percentage')}
                          </div>
                        </div>
                      </div>
                    ) : (
                      <div className="text-center py-8 text-muted-foreground">
                        No technical indicator data available for this date
                      </div>
                    )}
                  </TabsContent>
                </Tabs>
              </CardContent>
            </Card>

            {/* Historical Chart */}
            {ohlcvData && ohlcvData.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle>Price Chart</CardTitle>
                  <CardDescription>
                    Historical price data with selected date highlighted
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <CandlestickChartComponent data={ohlcvData} ticker={ticker} />
                </CardContent>
              </Card>
            )}
          </div>
        )}

        {/* Empty State */}
        {!loading && !selectedFundamental && !selectedIndicators && !selectedOhlcv && !error && (
          <Card>
            <CardContent className="text-center py-16">
              <Calendar className="h-16 w-16 mx-auto mb-4 text-muted-foreground opacity-50" />
              <h3 className="text-xl font-semibold mb-2">No Stock Selected</h3>
              <p className="text-muted-foreground">
                Enter a ticker symbol above to view historical analysis
              </p>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}

