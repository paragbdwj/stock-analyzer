'use client';

import { useState } from 'react';
import { ComposedChart, Line, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Bar } from 'recharts';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { CandlestickChart as CandleIcon, LineChart, TrendingUp } from 'lucide-react';
import { OHLCData } from '@/lib/api';
import { getCurrency } from '@/lib/utils';

interface StockChartProps {
  data: OHLCData[];
  ticker: string;
  period?: string;
}

type ChartType = 'candlestick' | 'line';

// Custom Candlestick Shape Component
const Candlestick = (props: any) => {
  const { x, y, width, height, payload } = props;
  
  if (!payload) return null;
  
  const { open, close, high, low } = payload;
  const isGreen = close > open;
  const color = isGreen ? '#22c55e' : '#ef4444';
  
  // Calculate positions
  const bodyTop = isGreen ? close : open;
  const bodyBottom = isGreen ? open : close;
  const bodyHeight = Math.abs(close - open);
  
  // Y scale calculation (inverted)
  const chartHeight = height || 0;
  const yMin = low;
  const yMax = high;
  const range = yMax - yMin || 1;
  
  const getY = (value: number) => {
    return y + chartHeight - ((value - yMin) / range) * chartHeight;
  };
  
  const wickX = x + width / 2;
  const bodyX = x + width * 0.2;
  const bodyWidth = width * 0.6;
  
  return (
    <g>
      {/* Upper wick */}
      <line
        x1={wickX}
        y1={getY(high)}
        x2={wickX}
        y2={getY(bodyTop)}
        stroke={color}
        strokeWidth={1}
      />
      {/* Lower wick */}
      <line
        x1={wickX}
        y1={getY(bodyBottom)}
        x2={wickX}
        y2={getY(low)}
        stroke={color}
        strokeWidth={1}
      />
      {/* Body */}
      <rect
        x={bodyX}
        y={getY(bodyTop)}
        width={bodyWidth}
        height={Math.max(getY(bodyBottom) - getY(bodyTop), 1)}
        fill={color}
        stroke={color}
      />
    </g>
  );
};

export function StockChart({ data, ticker, period = '1Y' }: StockChartProps) {
  const [chartType, setChartType] = useState<ChartType>('candlestick');
  const currency = getCurrency(ticker);

  // Calculate summary stats
  const periodHigh = Math.max(...data.map(d => d.high));
  const periodLow = Math.min(...data.map(d => d.low));
  const avgVolume = data.reduce((sum, d) => sum + d.volume, 0) / data.length;
  const periodChange = ((data[data.length - 1].close - data[0].open) / data[0].open) * 100;

  // Format data for the chart
  const chartData = data.map(item => ({
    ...item,
    date: new Date(item.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
  }));

  // Custom tooltip
  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-background border border-border rounded-lg p-3 shadow-lg">
          <p className="text-sm font-semibold mb-2">{data.date}</p>
          {chartType === 'candlestick' ? (
            <>
              <p className="text-xs">
                <span className="text-muted-foreground">Open:</span>{' '}
                <span className="font-medium">{currency.symbol}{data.open.toFixed(2)}</span>
              </p>
              <p className="text-xs">
                <span className="text-muted-foreground">High:</span>{' '}
                <span className="font-medium text-green-500">{currency.symbol}{data.high.toFixed(2)}</span>
              </p>
              <p className="text-xs">
                <span className="text-muted-foreground">Low:</span>{' '}
                <span className="font-medium text-red-500">{currency.symbol}{data.low.toFixed(2)}</span>
              </p>
              <p className="text-xs">
                <span className="text-muted-foreground">Close:</span>{' '}
                <span className="font-medium">{currency.symbol}{data.close.toFixed(2)}</span>
              </p>
            </>
          ) : (
            <p className="text-xs">
              <span className="text-muted-foreground">Price:</span>{' '}
              <span className="font-medium">{currency.symbol}{data.close.toFixed(2)}</span>
            </p>
          )}
          <p className="text-xs mt-1">
            <span className="text-muted-foreground">Volume:</span>{' '}
            <span className="font-medium">{(data.volume / 1000000).toFixed(2)}M</span>
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5" />
              Price Chart
              <span className="text-sm font-normal text-muted-foreground">• {period}</span>
            </CardTitle>
            <CardDescription>
              Historical price movement for {ticker}
            </CardDescription>
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant={chartType === 'candlestick' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setChartType('candlestick')}
              className="gap-2"
            >
              <CandleIcon className="h-4 w-4" />
              Candlestick
            </Button>
            <Button
              variant={chartType === 'line' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setChartType('line')}
              className="gap-2"
            >
              <LineChart className="h-4 w-4" />
              Line
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="w-full h-[500px]">
          <ResponsiveContainer width="100%" height="100%">
            {chartType === 'candlestick' ? (
              <ComposedChart
                data={chartData}
                margin={{ top: 20, right: 30, left: 20, bottom: 20 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#2a2e39" />
                <XAxis
                  dataKey="date"
                  stroke="#9ca3af"
                  style={{ fontSize: '12px' }}
                  interval={Math.floor(chartData.length / 10)}
                />
                <YAxis
                  stroke="#9ca3af"
                  style={{ fontSize: '12px' }}
                  domain={['dataMin - 10', 'dataMax + 10']}
                  tickFormatter={(value) => `${currency.symbol}${value.toFixed(0)}`}
                />
                <Tooltip content={<CustomTooltip />} />
                <Bar
                  dataKey="high"
                  shape={<Candlestick />}
                  isAnimationActive={false}
                />
              </ComposedChart>
            ) : (
              <ComposedChart
                data={chartData}
                margin={{ top: 20, right: 30, left: 20, bottom: 20 }}
              >
                <defs>
                  <linearGradient id="colorClose" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#2a2e39" />
                <XAxis
                  dataKey="date"
                  stroke="#9ca3af"
                  style={{ fontSize: '12px' }}
                  interval={Math.floor(chartData.length / 10)}
                />
                <YAxis
                  stroke="#9ca3af"
                  style={{ fontSize: '12px' }}
                  domain={['dataMin - 10', 'dataMax + 10']}
                  tickFormatter={(value) => `${currency.symbol}${value.toFixed(0)}`}
                />
                <Tooltip content={<CustomTooltip />} />
                <Area
                  type="monotone"
                  dataKey="close"
                  stroke="#3b82f6"
                  fill="url(#colorClose)"
                  strokeWidth={2}
                />
                <Line
                  type="monotone"
                  dataKey="close"
                  stroke="#3b82f6"
                  strokeWidth={2}
                  dot={false}
                />
              </ComposedChart>
            )}
          </ResponsiveContainer>
        </div>
        
        {/* Summary Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6 pt-4 border-t">
          <div className="text-center">
            <p className="text-xs text-muted-foreground mb-1">Period High</p>
            <p className="text-lg font-semibold text-green-500">
              {currency.symbol}{periodHigh.toFixed(2)}
            </p>
          </div>
          <div className="text-center">
            <p className="text-xs text-muted-foreground mb-1">Period Low</p>
            <p className="text-lg font-semibold text-red-500">
              {currency.symbol}{periodLow.toFixed(2)}
            </p>
          </div>
          <div className="text-center">
            <p className="text-xs text-muted-foreground mb-1">Avg Volume</p>
            <p className="text-lg font-semibold">
              {(avgVolume / 1000000).toFixed(2)}M
            </p>
          </div>
          <div className="text-center">
            <p className="text-xs text-muted-foreground mb-1">Period Change</p>
            <p className={`text-lg font-semibold ${
              periodChange >= 0 ? 'text-green-500' : 'text-red-500'
            }`}>
              {periodChange >= 0 ? '+' : ''}{periodChange.toFixed(2)}%
            </p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
