'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { TechnicalIndicators } from '@/lib/api';
import { formatNumber, formatPercentage, getRSIBadgeVariant } from '@/lib/utils';
import { TrendingUp, TrendingDown, Activity, BarChart3, Waves } from 'lucide-react';

interface TechnicalIndicatorsCardProps {
  indicators: TechnicalIndicators;
}

export function TechnicalIndicatorsCard({ indicators }: TechnicalIndicatorsCardProps) {
  const renderMetric = (label: string, value: number | undefined, decimals: number = 2, key?: string) => {
    if (value === undefined || value === null) return null;
    
    return (
      <div key={key || label} className="flex justify-between items-center py-2">
        <span className="text-sm text-muted-foreground">{label}</span>
        <span className="text-sm font-semibold">{formatNumber(value, decimals)}</span>
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

  const getRSISignal = (rsi?: number) => {
    if (!rsi) return null;
    if (rsi < 30) return { text: 'Oversold', color: 'text-green-600' };
    if (rsi > 70) return { text: 'Overbought', color: 'text-red-600' };
    return { text: 'Neutral', color: 'text-gray-600' };
  };

  const getMACDSignal = (macd?: number, signal?: number) => {
    if (!macd || !signal) return null;
    if (macd > signal) return { text: 'Bullish', color: 'text-green-600' };
    return { text: 'Bearish', color: 'text-red-600' };
  };

  const getADXSignal = (adx?: number) => {
    if (!adx) return null;
    if (adx > 25) return { text: 'Strong Trend', color: 'text-blue-600' };
    if (adx > 20) return { text: 'Moderate Trend', color: 'text-yellow-600' };
    return { text: 'Weak Trend', color: 'text-gray-600' };
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Activity className="h-5 w-5" />
          Technical Indicators
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Momentum Indicators */}
        {renderSection(
          'Momentum',
          <TrendingUp className="h-4 w-4 text-blue-600" />,
          [
            indicators.rsi !== undefined && (
              <div key="rsi" className="flex justify-between items-center py-2">
                <span className="text-sm text-muted-foreground">RSI (14)</span>
                <div className="flex items-center gap-2">
                  <span className="text-sm font-semibold">{formatNumber(indicators.rsi, 2)}</span>
                  {getRSISignal(indicators.rsi) && (
                    <Badge variant={getRSIBadgeVariant(indicators.rsi)} className="text-xs">
                      {getRSISignal(indicators.rsi)?.text}
                    </Badge>
                  )}
                </div>
              </div>
            ),
            renderMetric('MACD', indicators.macd, 4),
            renderMetric('MACD Signal', indicators.macd_signal, 4),
            renderMetric('MACD Histogram', indicators.macd_histogram, 4),
            indicators.macd !== undefined && indicators.macd_signal !== undefined && (
              <div key="macd-signal" className="flex justify-end">
                <Badge 
                  variant={getMACDSignal(indicators.macd, indicators.macd_signal)?.text === 'Bullish' ? 'default' : 'destructive'}
                  className="text-xs"
                >
                  {getMACDSignal(indicators.macd, indicators.macd_signal)?.text}
                </Badge>
              </div>
            ),
            renderMetric('Stochastic K', indicators.stoch_k, 2),
            renderMetric('Stochastic D', indicators.stoch_d, 2),
          ]
        )}

        <Separator />

        {/* Moving Averages */}
        {renderSection(
          'Moving Averages',
          <Waves className="h-4 w-4 text-purple-600" />,
          [
            renderMetric('SMA 20', indicators.sma_20, 2),
            renderMetric('SMA 50', indicators.sma_50, 2),
            renderMetric('SMA 100', indicators.sma_100, 2),
            renderMetric('SMA 200', indicators.sma_200, 2),
            renderMetric('EMA 12', indicators.ema_12, 2),
            renderMetric('EMA 26', indicators.ema_26, 2),
            renderMetric('EMA 50', indicators.ema_50, 2),
            renderMetric('EMA 200', indicators.ema_200, 2),
          ]
        )}

        <Separator />

        {/* Volatility */}
        {renderSection(
          'Volatility',
          <BarChart3 className="h-4 w-4 text-orange-600" />,
          [
            renderMetric('ATR (14)', indicators.atr, 2),
            renderMetric('Bollinger Upper', indicators.bb_upper, 2),
            renderMetric('Bollinger Middle', indicators.bb_middle, 2),
            renderMetric('Bollinger Lower', indicators.bb_lower, 2),
            indicators.volatility_20d !== undefined && (
              <div key="volatility" className="flex justify-between items-center py-2">
                <span className="text-sm text-muted-foreground">20-Day Volatility</span>
                <span className="text-sm font-semibold">{formatPercentage(indicators.volatility_20d)}</span>
              </div>
            ),
          ]
        )}

        <Separator />

        {/* Trend Indicators */}
        {renderSection(
          'Trend Strength',
          <Activity className="h-4 w-4 text-green-600" />,
          [
            indicators.adx !== undefined && (
              <div key="adx" className="flex justify-between items-center py-2">
                <span className="text-sm text-muted-foreground">ADX (14)</span>
                <div className="flex items-center gap-2">
                  <span className="text-sm font-semibold">{formatNumber(indicators.adx, 2)}</span>
                  {getADXSignal(indicators.adx) && (
                    <Badge variant="outline" className="text-xs">
                      {getADXSignal(indicators.adx)?.text}
                    </Badge>
                  )}
                </div>
              </div>
            ),
            renderMetric('DI+', indicators.di_plus, 2),
            renderMetric('DI-', indicators.di_minus, 2),
          ]
        )}

        <Separator />

        {/* Volume */}
        {renderSection(
          'Volume',
          <BarChart3 className="h-4 w-4 text-cyan-600" />,
          [
            indicators.obv !== undefined && (
              <div key="obv" className="flex justify-between items-center py-2">
                <span className="text-sm text-muted-foreground">OBV</span>
                <span className="text-sm font-semibold">{indicators.obv.toLocaleString()}</span>
              </div>
            ),
            indicators.volume_sma_20 !== undefined && (
              <div key="vol-sma" className="flex justify-between items-center py-2">
                <span className="text-sm text-muted-foreground">Volume SMA 20</span>
                <span className="text-sm font-semibold">{indicators.volume_sma_20.toLocaleString()}</span>
              </div>
            ),
          ]
        )}

        <Separator />

        {/* Returns */}
        {renderSection(
          'Returns',
          indicators.daily_return !== undefined && indicators.daily_return >= 0 ? 
            <TrendingUp className="h-4 w-4 text-green-600" /> : 
            <TrendingDown className="h-4 w-4 text-red-600" />,
          [
            indicators.daily_return !== undefined && (
              <div key="daily-return" className="flex justify-between items-center py-2">
                <span className="text-sm text-muted-foreground">Daily Return</span>
                <span className={`text-sm font-semibold ${indicators.daily_return >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {formatPercentage(indicators.daily_return)}
                </span>
              </div>
            ),
            indicators.cumulative_return !== undefined && (
              <div key="cum-return" className="flex justify-between items-center py-2">
                <span className="text-sm text-muted-foreground">Cumulative Return</span>
                <span className={`text-sm font-semibold ${indicators.cumulative_return >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {formatPercentage(indicators.cumulative_return)}
                </span>
              </div>
            ),
          ]
        )}
      </CardContent>
    </Card>
  );
}

