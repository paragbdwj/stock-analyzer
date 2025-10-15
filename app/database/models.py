"""
SQLAlchemy models for TimescaleDB.
"""
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, DateTime, Index, BigInteger, Boolean
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class StockPrice(Base):
    """
    Stock price data model for time series storage.
    This will be converted to a TimescaleDB hypertable.
    """
    __tablename__ = "stock_prices"
    
    # Composite primary key: ticker + timestamp
    ticker = Column(String(20), primary_key=True, nullable=False)
    timestamp = Column(DateTime, primary_key=True, nullable=False)
    
    # OHLCV data
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(BigInteger, nullable=False)
    adj_close = Column(Float, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<StockPrice(ticker='{self.ticker}', timestamp='{self.timestamp}', close={self.close})>"
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            "ticker": self.ticker,
            "timestamp": self.timestamp,
            "open": self.open,
            "high": self.high,
            "low": self.low,
            "close": self.close,
            "volume": self.volume,
            "adj_close": self.adj_close
        }


class StockMetadata(Base):
    """
    Metadata about cached stocks (when data was last updated, etc.).
    """
    __tablename__ = "stock_metadata"
    
    ticker = Column(String(20), primary_key=True, nullable=False)
    last_updated = Column(DateTime, nullable=False, default=datetime.utcnow)
    total_records = Column(Integer, nullable=False, default=0)
    first_date = Column(DateTime, nullable=True)
    last_date = Column(DateTime, nullable=True)
    exchange = Column(String(20), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Additional info
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<StockMetadata(ticker='{self.ticker}', last_updated='{self.last_updated}')>"
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            "ticker": self.ticker,
            "last_updated": self.last_updated,
            "total_records": self.total_records,
            "first_date": self.first_date,
            "last_date": self.last_date,
            "exchange": self.exchange,
            "is_active": self.is_active
        }


class StockFundamentals(Base):
    """
    Fundamental data for stocks (updated periodically).
    Stores company fundamentals like P/E ratio, market cap, etc.
    """
    __tablename__ = "stock_fundamentals"
    
    ticker = Column(String(20), primary_key=True, nullable=False)
    timestamp = Column(DateTime, primary_key=True, nullable=False, default=datetime.utcnow)
    
    # Valuation metrics
    trailing_pe = Column(Float, nullable=True)
    forward_pe = Column(Float, nullable=True)
    price_to_book = Column(Float, nullable=True)
    price_to_sales = Column(Float, nullable=True)
    peg_ratio = Column(Float, nullable=True)
    
    # Financial health metrics
    market_cap = Column(BigInteger, nullable=True)
    enterprise_value = Column(BigInteger, nullable=True)
    debt_to_equity = Column(Float, nullable=True)
    current_ratio = Column(Float, nullable=True)
    quick_ratio = Column(Float, nullable=True)
    
    # Profitability metrics
    profit_margin = Column(Float, nullable=True)
    operating_margin = Column(Float, nullable=True)
    return_on_assets = Column(Float, nullable=True)
    return_on_equity = Column(Float, nullable=True)
    
    # Growth & dividend metrics
    revenue_growth = Column(Float, nullable=True)
    earnings_growth = Column(Float, nullable=True)
    dividend_yield = Column(Float, nullable=True)
    payout_ratio = Column(Float, nullable=True)
    
    # Risk metrics
    beta = Column(Float, nullable=True)
    
    # Company info
    sector = Column(String(100), nullable=True)
    industry = Column(String(100), nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<StockFundamentals(ticker='{self.ticker}', timestamp='{self.timestamp}')>"
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            "ticker": self.ticker,
            "timestamp": self.timestamp,
            "trailing_pe": self.trailing_pe,
            "forward_pe": self.forward_pe,
            "price_to_book": self.price_to_book,
            "price_to_sales": self.price_to_sales,
            "peg_ratio": self.peg_ratio,
            "market_cap": self.market_cap,
            "enterprise_value": self.enterprise_value,
            "debt_to_equity": self.debt_to_equity,
            "current_ratio": self.current_ratio,
            "quick_ratio": self.quick_ratio,
            "profit_margin": self.profit_margin,
            "operating_margin": self.operating_margin,
            "return_on_assets": self.return_on_assets,
            "return_on_equity": self.return_on_equity,
            "revenue_growth": self.revenue_growth,
            "earnings_growth": self.earnings_growth,
            "dividend_yield": self.dividend_yield,
            "payout_ratio": self.payout_ratio,
            "beta": self.beta,
            "sector": self.sector,
            "industry": self.industry
        }


class StockTechnicalIndicators(Base):
    """
    Technical indicators calculated from OHLCV data.
    This will be converted to a TimescaleDB hypertable.
    """
    __tablename__ = "stock_technical_indicators"
    
    # Composite primary key: ticker + timestamp
    ticker = Column(String(20), primary_key=True, nullable=False)
    timestamp = Column(DateTime, primary_key=True, nullable=False)
    
    # Moving Averages
    sma_20 = Column(Float, nullable=True)
    sma_50 = Column(Float, nullable=True)
    sma_100 = Column(Float, nullable=True)
    sma_200 = Column(Float, nullable=True)
    
    # Exponential Moving Averages
    ema_12 = Column(Float, nullable=True)
    ema_26 = Column(Float, nullable=True)
    ema_50 = Column(Float, nullable=True)
    ema_200 = Column(Float, nullable=True)
    
    # Momentum Indicators
    rsi = Column(Float, nullable=True)
    macd = Column(Float, nullable=True)
    macd_signal = Column(Float, nullable=True)
    macd_histogram = Column(Float, nullable=True)
    
    # Volatility Indicators
    atr = Column(Float, nullable=True)
    bb_upper = Column(Float, nullable=True)
    bb_middle = Column(Float, nullable=True)
    bb_lower = Column(Float, nullable=True)
    
    # Volume Indicators
    obv = Column(BigInteger, nullable=True)
    volume_sma_20 = Column(BigInteger, nullable=True)
    
    # Trend Indicators
    adx = Column(Float, nullable=True)
    di_plus = Column(Float, nullable=True)
    di_minus = Column(Float, nullable=True)
    
    # Stochastic
    stoch_k = Column(Float, nullable=True)
    stoch_d = Column(Float, nullable=True)
    
    # Derived Metrics
    daily_return = Column(Float, nullable=True)
    cumulative_return = Column(Float, nullable=True)
    volatility_20d = Column(Float, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<StockTechnicalIndicators(ticker='{self.ticker}', timestamp='{self.timestamp}')>"
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            "ticker": self.ticker,
            "timestamp": self.timestamp,
            "sma_20": self.sma_20,
            "sma_50": self.sma_50,
            "sma_100": self.sma_100,
            "sma_200": self.sma_200,
            "ema_12": self.ema_12,
            "ema_26": self.ema_26,
            "ema_50": self.ema_50,
            "ema_200": self.ema_200,
            "rsi": self.rsi,
            "macd": self.macd,
            "macd_signal": self.macd_signal,
            "macd_histogram": self.macd_histogram,
            "atr": self.atr,
            "bb_upper": self.bb_upper,
            "bb_middle": self.bb_middle,
            "bb_lower": self.bb_lower,
            "obv": self.obv,
            "volume_sma_20": self.volume_sma_20,
            "adx": self.adx,
            "di_plus": self.di_plus,
            "di_minus": self.di_minus,
            "stoch_k": self.stoch_k,
            "stoch_d": self.stoch_d,
            "daily_return": self.daily_return,
            "cumulative_return": self.cumulative_return,
            "volatility_20d": self.volatility_20d
        }


# Create indexes
Index('idx_stock_metadata_updated', StockMetadata.last_updated)
Index('idx_stock_metadata_exchange', StockMetadata.exchange)
Index('idx_stock_fundamentals_ticker', StockFundamentals.ticker)
Index('idx_stock_technical_ticker_time', StockTechnicalIndicators.ticker, StockTechnicalIndicators.timestamp)

