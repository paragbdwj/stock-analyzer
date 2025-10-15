'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { FundamentalData } from '@/lib/api';
import { formatNumber, formatPercentage, formatLargeNumberWithCurrency } from '@/lib/utils';
import { TrendingUp, TrendingDown, DollarSign, PieChart, Activity, Building2 } from 'lucide-react';

interface FundamentalsCardProps {
  fundamentals: FundamentalData;
  ticker?: string;
}

export function FundamentalsCard({ fundamentals, ticker }: FundamentalsCardProps) {
  const renderMetric = (label: string, value: number | string | undefined, format: 'number' | 'percentage' | 'currency' | 'ratio' | 'text' = 'number', key?: string) => {
    if (value === undefined || value === null) return null;
    
    let displayValue: string;
    switch (format) {
      case 'percentage':
        displayValue = formatPercentage(Number(value));
        break;
      case 'currency':
        displayValue = formatLargeNumberWithCurrency(Number(value), ticker || fundamentals.ticker);
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

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Building2 className="h-5 w-5" />
          Fundamental Analysis
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Company Info */}
        {(fundamentals.sector || fundamentals.industry) && (
          <div className="flex gap-2 flex-wrap">
            {fundamentals.sector && (
              <Badge variant="secondary" className="text-xs">
                {fundamentals.sector}
              </Badge>
            )}
            {fundamentals.industry && (
              <Badge variant="outline" className="text-xs">
                {fundamentals.industry}
              </Badge>
            )}
          </div>
        )}

        {/* Valuation Metrics */}
        {renderSection(
          'Valuation Metrics',
          <DollarSign className="h-4 w-4 text-green-600" />,
          [
            renderMetric('Market Cap', fundamentals.market_cap, 'currency'),
            renderMetric('Enterprise Value', fundamentals.enterprise_value, 'currency'),
            renderMetric('Trailing P/E', fundamentals.trailing_pe, 'ratio'),
            renderMetric('Forward P/E', fundamentals.forward_pe, 'ratio'),
            renderMetric('Price to Book', fundamentals.price_to_book, 'ratio'),
            renderMetric('Price to Sales', fundamentals.price_to_sales, 'ratio'),
            renderMetric('PEG Ratio', fundamentals.peg_ratio, 'ratio'),
          ]
        )}

        <Separator />

        {/* Financial Health */}
        {renderSection(
          'Financial Health',
          <Activity className="h-4 w-4 text-blue-600" />,
          [
            renderMetric('Debt to Equity', fundamentals.debt_to_equity, 'ratio'),
            renderMetric('Current Ratio', fundamentals.current_ratio, 'ratio'),
            renderMetric('Quick Ratio', fundamentals.quick_ratio, 'ratio'),
          ]
        )}

        <Separator />

        {/* Profitability */}
        {renderSection(
          'Profitability',
          <TrendingUp className="h-4 w-4 text-purple-600" />,
          [
            renderMetric('Profit Margin', fundamentals.profit_margin, 'percentage'),
            renderMetric('Operating Margin', fundamentals.operating_margin, 'percentage'),
            renderMetric('Return on Assets', fundamentals.return_on_assets, 'percentage'),
            renderMetric('Return on Equity', fundamentals.return_on_equity, 'percentage'),
          ]
        )}

        <Separator />

        {/* Growth & Dividends */}
        {renderSection(
          'Growth & Dividends',
          <PieChart className="h-4 w-4 text-orange-600" />,
          [
            renderMetric('Revenue Growth', fundamentals.revenue_growth, 'percentage'),
            renderMetric('Earnings Growth', fundamentals.earnings_growth, 'percentage'),
            renderMetric('Dividend Yield', fundamentals.dividend_yield, 'percentage'),
            renderMetric('Payout Ratio', fundamentals.payout_ratio, 'percentage'),
          ]
        )}

        <Separator />

        {/* Risk Metrics */}
        {fundamentals.beta !== undefined && (
          <div className="space-y-2">
            <div className="flex items-center gap-2 mb-3">
              <Activity className="h-4 w-4 text-red-600" />
              <h4 className="text-sm font-semibold">Risk</h4>
            </div>
            {renderMetric('Beta', fundamentals.beta, 'ratio')}
            {fundamentals.beta !== undefined && (
              <p className="text-xs text-muted-foreground mt-2">
                {fundamentals.beta > 1
                  ? 'More volatile than the market'
                  : fundamentals.beta < 1
                  ? 'Less volatile than the market'
                  : 'Tracks the market'}
              </p>
            )}
          </div>
        )}

        {fundamentals.timestamp && (
          <div className="text-xs text-muted-foreground text-center pt-4">
            Data as of: {new Date(fundamentals.timestamp).toLocaleDateString()}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

