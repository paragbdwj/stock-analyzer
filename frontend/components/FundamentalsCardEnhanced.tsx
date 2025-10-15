'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { FundamentalData } from '@/lib/api';
import { formatNumber, formatPercentage, formatLargeNumberWithCurrency } from '@/lib/utils';
import { TrendingUp, TrendingDown, DollarSign, PieChart, Activity, Building2, Calendar, BarChart2 } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';

interface FundamentalsCardEnhancedProps {
  fundamentals: FundamentalData;
  historicalData?: FundamentalData[];
  ticker?: string;
}

export function FundamentalsCardEnhanced({ fundamentals, historicalData, ticker }: FundamentalsCardEnhancedProps) {
  const [selectedSnapshot, setSelectedSnapshot] = useState<FundamentalData>(fundamentals);
  const [showTrends, setShowTrends] = useState(false);

  useEffect(() => {
    setSelectedSnapshot(fundamentals);
  }, [fundamentals]);

  const handleDateChange = (timestamp: string) => {
    const snapshot = historicalData?.find(s => s.timestamp === timestamp);
    if (snapshot) {
      setSelectedSnapshot(snapshot);
    }
  };

  const renderMetric = (label: string, value: number | string | undefined, format: 'number' | 'percentage' | 'currency' | 'ratio' | 'text' = 'number', key?: string) => {
    if (value === undefined || value === null) return null;
    
    let displayValue: string;
    switch (format) {
      case 'percentage':
        displayValue = formatPercentage(Number(value));
        break;
      case 'currency':
        displayValue = formatLargeNumberWithCurrency(Number(value), ticker || selectedSnapshot.ticker);
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
      <div key={key || label} className="flex justify-between items-center py-2">
        <span className="text-sm text-muted-foreground">{label}</span>
        <span className="text-sm font-semibold">{displayValue}</span>
      </div>
    );
  };

  const renderSection = (title: string, icon: React.ReactNode, metrics: React.ReactNode[]) => {
    const validMetrics = metrics.filter(m => m !== null);
    if (validMetrics.length === 0) return null;

    return (
      <div className="space-y-2">
        <div className="flex items-center gap-2 mb-3">
          {icon}
          <h4 className="text-sm font-semibold">{title}</h4>
        </div>
        <div className="space-y-1">{validMetrics}</div>
      </div>
    );
  };

  const renderTrendChart = (metric: keyof FundamentalData, label: string) => {
    if (!historicalData || historicalData.length < 2) return null;

    const data = [...historicalData]
      .reverse()
      .map(snapshot => ({
        date: new Date(snapshot.timestamp!).toLocaleDateString('en-US', { month: 'short', year: '2-digit' }),
        value: snapshot[metric] as number,
      }))
      .filter(d => d.value !== null && d.value !== undefined);

    if (data.length === 0) return null;

    return (
      <div key={metric as string} className="mt-4">
        <h5 className="text-xs font-semibold mb-2 flex items-center gap-1">
          <BarChart2 className="h-3 w-3" />
          {label} Trend
        </h5>
        <ResponsiveContainer width="100%" height={100}>
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.1} />
            <XAxis dataKey="date" tick={{ fontSize: 10 }} stroke="#6b7280" />
            <YAxis tick={{ fontSize: 10 }} stroke="#6b7280" />
            <Tooltip
              contentStyle={{ backgroundColor: '#1f2937', border: 'none', borderRadius: '6px', fontSize: '12px' }}
              labelStyle={{ color: '#9ca3af' }}
            />
            <Line type="monotone" dataKey="value" stroke="#3b82f6" strokeWidth={2} dot={{ r: 3 }} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    );
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex justify-between items-start">
          <CardTitle className="flex items-center gap-2">
            <Building2 className="h-5 w-5" />
            Fundamental Analysis
          </CardTitle>
          {historicalData && historicalData.length > 1 && (
            <button
              onClick={() => setShowTrends(!showTrends)}
              className="text-xs text-muted-foreground hover:text-foreground transition-colors flex items-center gap-1"
            >
              <BarChart2 className="h-3 w-3" />
              {showTrends ? 'Hide' : 'Show'} Trends
            </button>
          )}
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Date Selector */}
        {historicalData && historicalData.length > 1 && (
          <div className="flex items-center gap-2 p-3 bg-secondary/50 rounded-lg">
            <Calendar className="h-4 w-4 text-muted-foreground" />
            <span className="text-sm text-muted-foreground">View snapshot from:</span>
            <Select onValueChange={handleDateChange} value={selectedSnapshot.timestamp}>
              <SelectTrigger className="w-[200px] h-8">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {historicalData.map((snapshot, index) => (
                  <SelectItem key={snapshot.timestamp || index} value={snapshot.timestamp!}>
                    {new Date(snapshot.timestamp!).toLocaleDateString('en-US', {
                      year: 'numeric',
                      month: 'short',
                      day: 'numeric'
                    })}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Badge variant="outline" className="text-xs">
              {historicalData.length} snapshots
            </Badge>
          </div>
        )}

        {/* Company Info */}
        {(selectedSnapshot.sector || selectedSnapshot.industry) && (
          <div className="flex gap-2 flex-wrap">
            {selectedSnapshot.sector && (
              <Badge variant="secondary" className="text-xs">
                {selectedSnapshot.sector}
              </Badge>
            )}
            {selectedSnapshot.industry && (
              <Badge variant="outline" className="text-xs">
                {selectedSnapshot.industry}
              </Badge>
            )}
          </div>
        )}

        {/* Valuation Metrics */}
        {renderSection(
          'Valuation Metrics',
          <DollarSign className="h-4 w-4 text-green-600" />,
          [
            renderMetric('Market Cap', selectedSnapshot.market_cap, 'currency', 'market_cap'),
            renderMetric('Enterprise Value', selectedSnapshot.enterprise_value, 'currency', 'enterprise_value'),
            renderMetric('Trailing P/E', selectedSnapshot.trailing_pe, 'ratio', 'trailing_pe'),
            renderMetric('Forward P/E', selectedSnapshot.forward_pe, 'ratio', 'forward_pe'),
            renderMetric('Price to Book', selectedSnapshot.price_to_book, 'ratio', 'price_to_book'),
            renderMetric('Price to Sales', selectedSnapshot.price_to_sales, 'ratio', 'price_to_sales'),
            renderMetric('PEG Ratio', selectedSnapshot.peg_ratio, 'ratio', 'peg_ratio'),
          ]
        )}

        {showTrends && historicalData && historicalData.length > 1 && (
          <>
            {renderTrendChart('trailing_pe', 'P/E Ratio')}
            {renderTrendChart('price_to_book', 'P/B Ratio')}
          </>
        )}

        <Separator />

        {/* Financial Health */}
        {renderSection(
          'Financial Health',
          <Activity className="h-4 w-4 text-blue-600" />,
          [
            renderMetric('Debt to Equity', selectedSnapshot.debt_to_equity, 'ratio', 'debt_to_equity'),
            renderMetric('Current Ratio', selectedSnapshot.current_ratio, 'ratio', 'current_ratio'),
            renderMetric('Quick Ratio', selectedSnapshot.quick_ratio, 'ratio', 'quick_ratio'),
          ]
        )}

        <Separator />

        {/* Profitability */}
        {renderSection(
          'Profitability',
          <TrendingUp className="h-4 w-4 text-purple-600" />,
          [
            renderMetric('Profit Margin', selectedSnapshot.profit_margin, 'percentage', 'profit_margin'),
            renderMetric('Operating Margin', selectedSnapshot.operating_margin, 'percentage', 'operating_margin'),
            renderMetric('Return on Assets', selectedSnapshot.return_on_assets, 'percentage', 'return_on_assets'),
            renderMetric('Return on Equity', selectedSnapshot.return_on_equity, 'percentage', 'return_on_equity'),
          ]
        )}

        {showTrends && historicalData && historicalData.length > 1 && (
          <>
            {renderTrendChart('profit_margin', 'Profit Margin')}
            {renderTrendChart('return_on_equity', 'ROE')}
          </>
        )}

        <Separator />

        {/* Growth & Dividends */}
        {renderSection(
          'Growth & Dividends',
          <PieChart className="h-4 w-4 text-orange-600" />,
          [
            renderMetric('Revenue Growth', selectedSnapshot.revenue_growth, 'percentage', 'revenue_growth'),
            renderMetric('Earnings Growth', selectedSnapshot.earnings_growth, 'percentage', 'earnings_growth'),
            renderMetric('Dividend Yield', selectedSnapshot.dividend_yield, 'percentage', 'dividend_yield'),
            renderMetric('Payout Ratio', selectedSnapshot.payout_ratio, 'percentage', 'payout_ratio'),
          ]
        )}

        {showTrends && historicalData && historicalData.length > 1 && (
          renderTrendChart('revenue_growth', 'Revenue Growth')
        )}

        <Separator />

        {/* Risk Metrics */}
        {selectedSnapshot.beta !== undefined && (
          <div className="space-y-2">
            <div className="flex items-center gap-2 mb-3">
              <Activity className="h-4 w-4 text-red-600" />
              <h4 className="text-sm font-semibold">Risk</h4>
            </div>
            {renderMetric('Beta', selectedSnapshot.beta, 'ratio', 'beta')}
            {selectedSnapshot.beta !== undefined && (
              <p className="text-xs text-muted-foreground mt-2">
                {selectedSnapshot.beta > 1
                  ? 'More volatile than the market'
                  : selectedSnapshot.beta < 1
                  ? 'Less volatile than the market'
                  : 'Tracks the market'}
              </p>
            )}
          </div>
        )}

        {selectedSnapshot.timestamp && (
          <div className="text-xs text-muted-foreground text-center pt-4">
            Snapshot from: {new Date(selectedSnapshot.timestamp).toLocaleString()}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

