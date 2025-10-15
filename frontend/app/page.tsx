import Link from 'next/link';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { TrendingUp, Search, BarChart3, Activity, Database, Calendar } from 'lucide-react';

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-neutral-50 to-neutral-100 dark:from-neutral-950 dark:to-neutral-900">
      <div className="container mx-auto px-4 py-16">
        {/* Header */}
        <div className="text-center mb-16">
          <div className="flex items-center justify-center mb-6">
            <TrendingUp className="h-16 w-16 text-primary" />
          </div>
          <h1 className="text-5xl font-bold mb-4 bg-gradient-to-r from-primary to-primary/60 bg-clip-text text-transparent">
            Stock Analyzer
          </h1>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Powerful stock scanning and analysis using advanced technical and fundamental indicators
          </p>
        </div>

        {/* Feature Cards */}
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
          {/* Stock Scanner */}
          <Card className="hover:shadow-lg transition-shadow border-2 hover:border-primary/50">
            <CardHeader>
              <div className="flex items-center gap-2 mb-2">
                <Search className="h-6 w-6 text-primary" />
                <CardTitle>Stock Scanner</CardTitle>
              </div>
              <CardDescription>
                Scan entire exchanges with custom filters
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 text-sm text-muted-foreground mb-4">
                <li>• Multiple exchanges</li>
                <li>• 15+ technical indicators</li>
                <li>• Fundamental metrics</li>
                <li>• AND/OR logic</li>
              </ul>
              <Link href="/scanner">
                <Button className="w-full">
                  Open Scanner
                </Button>
              </Link>
            </CardContent>
          </Card>

          {/* Stock Analyzer */}
          <Card className="hover:shadow-lg transition-shadow border-2 hover:border-primary/50">
            <CardHeader>
              <div className="flex items-center gap-2 mb-2">
                <BarChart3 className="h-6 w-6 text-primary" />
                <CardTitle>Stock Analyzer</CardTitle>
              </div>
              <CardDescription>
                Deep dive analysis with trends
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 text-sm text-muted-foreground mb-4">
                <li>• Technical analysis</li>
                <li>• Fundamental data</li>
                <li>• Historical trends</li>
                <li>• Real-time data</li>
              </ul>
              <Link href="/analyzer">
                <Button className="w-full">
                  Analyze Stock
                </Button>
              </Link>
            </CardContent>
          </Card>

          {/* Historical Analysis - NEW! */}
          <Card className="hover:shadow-lg transition-shadow border-2 hover:border-primary/50 border-primary/30">
            <CardHeader>
              <div className="flex items-center gap-2 mb-2">
                <Calendar className="h-6 w-6 text-primary" />
                <CardTitle>Historical Analysis</CardTitle>
                <Badge variant="secondary" className="ml-auto text-xs">NEW</Badge>
              </div>
              <CardDescription>
                View complete analysis for any date
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 text-sm text-muted-foreground mb-4">
                <li>• Date-based analysis</li>
                <li>• Historical fundamentals</li>
                <li>• Past indicators</li>
                <li>• OHLCV at any date</li>
              </ul>
              <Link href="/history">
                <Button className="w-full">
                  View History
                </Button>
              </Link>
            </CardContent>
          </Card>

          {/* Quick Price Check */}
          <Card className="hover:shadow-lg transition-shadow border-2 hover:border-primary/50">
            <CardHeader>
              <div className="flex items-center gap-2 mb-2">
                <Activity className="h-6 w-6 text-primary" />
                <CardTitle>Price Monitor</CardTitle>
              </div>
              <CardDescription>
                Quick price lookup
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 text-sm text-muted-foreground mb-4">
                <li>• Instant queries</li>
                <li>• Multiple exchanges</li>
                <li>• Real-time data</li>
                <li>• Fast lookup</li>
              </ul>
              <Link href="/analyzer">
                <Button className="w-full" variant="outline">
                  Check Prices
                </Button>
              </Link>
            </CardContent>
          </Card>
        </div>

        {/* Technical Indicators Info */}
        <Card className="mb-12">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Database className="h-6 w-6" />
              Available Indicators & Metrics
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-2 gap-8">
              <div>
                <h3 className="font-semibold mb-3 text-primary">Technical Indicators</h3>
                <ul className="grid grid-cols-2 gap-2 text-sm text-muted-foreground">
                  <li>• RSI (Relative Strength Index)</li>
                  <li>• MACD & Signal</li>
                  <li>• SMA (20, 50, 100, 200)</li>
                  <li>• EMA (12, 26, 50, 200)</li>
                  <li>• Bollinger Bands</li>
                  <li>• ATR (Average True Range)</li>
                  <li>• ADX (Directional Index)</li>
                  <li>• Stochastic Oscillator</li>
                  <li>• OBV (On-Balance Volume)</li>
                </ul>
              </div>
              <div>
                <h3 className="font-semibold mb-3 text-primary">Fundamental Metrics</h3>
                <ul className="grid grid-cols-2 gap-2 text-sm text-muted-foreground">
                  <li>• P/E Ratio (Trailing & Forward)</li>
                  <li>• Price-to-Book Ratio</li>
                  <li>• Debt-to-Equity</li>
                  <li>• Current Ratio</li>
                  <li>• Market Capitalization</li>
                  <li>• Beta Coefficient</li>
                  <li>• Dividend Yield</li>
                  <li>• Sector & Industry</li>
                </ul>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Footer */}
        <div className="text-center text-sm text-muted-foreground">
          <p className="mb-2">Powered by FastAPI, TimescaleDB, and Yahoo Finance</p>
          <p className="text-xs">⚠️ For informational purposes only. Not investment advice.</p>
        </div>
      </div>
    </div>
  );
}
