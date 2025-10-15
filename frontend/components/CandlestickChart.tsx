'use client';

import { useMemo, useState } from 'react';
import {
  ComposedChart,
  Line,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
} from 'recharts';
import { OHLCData } from '@/lib/api';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import { getCurrency } from '@/lib/utils';

interface CandlestickChartProps {
  data: OHLCData[];
  ticker: string;
  period?: string;
}

export function CandlestickChart({ data, ticker, period = '1Y' }: CandlestickChartProps) {
  const currency = getCurrency(ticker);
  
  // Scrolling state - show 60 data points at a time
  const pointsToShow = 60;
  const [endIndex, setEndIndex] = useState(data.length);
  const startIndex = Math.max(0, endIndex - pointsToShow);
  
  // Transform data for chart representation
  const chartData = useMemo(() => {
    return data.map((item) => {
      const isGreen = item.close >= item.open;
      
      return {
        date: new Date(item.date).toLocaleDateString('en-US', { 
          month: 'short', 
          day: 'numeric',
          year: data.length > 180 ? 'numeric' : undefined 
        }),
        fullDate: item.date,
        high: item.high,
        low: item.low,
        open: item.open,
        close: item.close,
        volume: item.volume,
        isGreen,
        // For area chart representation
        range: [item.low, item.high],
      };
    });
  }, [data]);
  
  // Get visible data
  const visibleData = useMemo(() => {
    return chartData.slice(startIndex, endIndex);
  }, [chartData, startIndex, endIndex]);
  
  // Navigation handlers
  const canScrollLeft = startIndex > 0;
  const canScrollRight = endIndex < data.length;
  
  const scrollLeft = () => {
    if (canScrollLeft) {
      const newEnd = Math.max(pointsToShow, endIndex - Math.floor(pointsToShow / 2));
      setEndIndex(newEnd);
    }
  };
  
  const scrollRight = () => {
    if (canScrollRight) {
      const newEnd = Math.min(data.length, endIndex + Math.floor(pointsToShow / 2));
      setEndIndex(newEnd);
    }
  };
  
  const resetView = () => {
    setEndIndex(data.length);
  };

  // Calculate price range for better Y-axis scaling (use visible data)
  const priceRange = useMemo(() => {
    const visiblePrices = visibleData.flatMap((d) => [d.high, d.low]);
    if (visiblePrices.length === 0) return { min: 0, max: 100 };
    
    const min = Math.min(...visiblePrices);
    const max = Math.max(...visiblePrices);
    const padding = (max - min) * 0.1;
    return {
      min: Math.floor(min - padding),
      max: Math.ceil(max + padding),
    };
  }, [visibleData]);

  // Custom tooltip
  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length > 0) {
      const data = payload[0].payload;
      const isGreen = data.close >= data.open;
      const change = data.close - data.open;
      const changePercent = (change / data.open) * 100;
      
      return (
        <div className="bg-background border rounded-lg shadow-lg p-3 text-sm">
          <p className="font-semibold mb-2">{data.date}</p>
          <div className="space-y-1">
            <p className="flex justify-between gap-4">
              <span className="text-muted-foreground">Open:</span>
              <span className="font-medium">{currency.symbol}{data.open.toFixed(2)}</span>
            </p>
            <p className="flex justify-between gap-4">
              <span className="text-muted-foreground">High:</span>
              <span className="font-medium text-green-500">{currency.symbol}{data.high.toFixed(2)}</span>
            </p>
            <p className="flex justify-between gap-4">
              <span className="text-muted-foreground">Low:</span>
              <span className="font-medium text-red-500">{currency.symbol}{data.low.toFixed(2)}</span>
            </p>
            <p className="flex justify-between gap-4">
              <span className="text-muted-foreground">Close:</span>
              <span className={`font-medium ${isGreen ? 'text-green-500' : 'text-red-500'}`}>
                {currency.symbol}{data.close.toFixed(2)}
              </span>
            </p>
            <p className="flex justify-between gap-4 pt-1 border-t">
              <span className="text-muted-foreground">Volume:</span>
              <span className="font-medium text-xs">
                {(data.volume / 1000000).toFixed(2)}M
              </span>
            </p>
            <p className="flex justify-between gap-4">
              <span className="text-muted-foreground">Change:</span>
              <span className={`font-medium ${isGreen ? 'text-green-500' : 'text-red-500'}`}>
                {isGreen ? '+' : ''}{currency.symbol}{Math.abs(change).toFixed(2)} ({isGreen ? '+' : ''}{changePercent.toFixed(2)}%)
              </span>
            </p>
          </div>
        </div>
      );
    }
    return null;
  };

  // Calculate data point interval for X-axis labels (based on visible data)
  const labelInterval = useMemo(() => {
    const len = visibleData.length;
    if (len <= 30) return 0; // Show all labels
    if (len <= 60) return Math.floor(len / 10); // ~10 labels
    return Math.floor(len / 8); // ~8 labels for longer periods
  }, [visibleData.length]);

  // Custom dot for candlesticks (simplified - just show dots)
  const customDot = false; // Disable custom dots, use simple line instead

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span>Price Chart</span>
          <div className="flex items-center gap-2">
            <span className="text-sm font-normal text-muted-foreground">
              {period} • Showing {visibleData.length} of {data.length} points
            </span>
          </div>
        </CardTitle>
        <CardDescription className="flex items-center justify-between">
          <span>Historical price movement for {ticker}</span>
          <div className="flex items-center gap-1">
            <Button
              variant="outline"
              size="sm"
              onClick={scrollLeft}
              disabled={!canScrollLeft}
              className="h-7 px-2"
            >
              <ChevronLeft className="h-4 w-4" />
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={resetView}
              disabled={endIndex === data.length && startIndex === Math.max(0, data.length - pointsToShow)}
              className="h-7 px-2 text-xs"
            >
              Reset
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={scrollRight}
              disabled={!canScrollRight}
              className="h-7 px-2"
            >
              <ChevronRight className="h-4 w-4" />
            </Button>
          </div>
        </CardDescription>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={400}>
          <ComposedChart
            data={visibleData}
            margin={{ top: 10, right: 10, left: 0, bottom: 0 }}
          >
            <defs>
              <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
                <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
            <XAxis 
              dataKey="date" 
              tick={{ fontSize: 11 }}
              interval={labelInterval}
              angle={0}
              textAnchor="middle"
              height={30}
            />
            <YAxis 
              domain={[priceRange.min, priceRange.max]}
              tick={{ fontSize: 11 }}
              tickFormatter={(value) => `${currency.symbol}${value}`}
            />
            <Tooltip content={<CustomTooltip />} />
            
            {/* Area for visual appeal */}
            <Area
              type="monotone"
              dataKey="close"
              stroke="#3b82f6"
              strokeWidth={2}
              fill="url(#colorPrice)"
              dot={false}
            />
            
            {/* Close price line */}
            <Line
              type="monotone"
              dataKey="close"
              stroke="#3b82f6"
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 6 }}
            />
          </ComposedChart>
        </ResponsiveContainer>
        
        {/* Volume Chart */}
        <div className="mt-6">
          <p className="text-sm font-medium mb-2">Volume</p>
          <ResponsiveContainer width="100%" height={100}>
            <BarChart data={visibleData} margin={{ top: 0, right: 10, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
              <XAxis dataKey="date" hide />
              <YAxis 
                tick={{ fontSize: 10 }}
                tickFormatter={(value) => `${(value / 1000000).toFixed(0)}M`}
              />
              <Tooltip
                formatter={(value: number) => [`${(value / 1000000).toFixed(2)}M`, 'Volume']}
                labelFormatter={(label) => `Date: ${label}`}
              />
              <Bar 
                dataKey="volume" 
                fill="#8884d8"
                radius={[2, 2, 0, 0]}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
        
        {/* Summary Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6 pt-4 border-t">
          <div className="text-center">
            <p className="text-xs text-muted-foreground mb-1">Visible High</p>
            <p className="text-lg font-semibold text-green-500">
              {currency.symbol}{Math.max(...visibleData.map(d => d.high)).toFixed(2)}
            </p>
          </div>
          <div className="text-center">
            <p className="text-xs text-muted-foreground mb-1">Visible Low</p>
            <p className="text-lg font-semibold text-red-500">
              {currency.symbol}{Math.min(...visibleData.map(d => d.low)).toFixed(2)}
            </p>
          </div>
          <div className="text-center">
            <p className="text-xs text-muted-foreground mb-1">Avg Volume</p>
            <p className="text-lg font-semibold">
              {(visibleData.reduce((sum, d) => sum + d.volume, 0) / visibleData.length / 1000000).toFixed(2)}M
            </p>
          </div>
          <div className="text-center">
            <p className="text-xs text-muted-foreground mb-1">Visible Change</p>
            <p className={`text-lg font-semibold ${
              visibleData[visibleData.length - 1].close >= visibleData[0].open ? 'text-green-500' : 'text-red-500'
            }`}>
              {((visibleData[visibleData.length - 1].close - visibleData[0].open) / visibleData[0].open * 100).toFixed(2)}%
            </p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
