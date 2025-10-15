"""
Storage manager using TimescaleDB for time series data.
"""
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
import pandas as pd
from sqlalchemy import text, func, and_

from app.database.models import StockPrice, StockMetadata, StockFundamentals, StockTechnicalIndicators
from app.utils.logger import get_logger


logger = get_logger(__name__)


class StorageManager:
    """
    Manages storage of stock data in TimescaleDB.
    Provides similar interface to the old file-based storage for backward compatibility.
    """
    
    def __init__(self, cache_days: int = 1):
        """
        Initialize storage manager.
        
        Args:
            cache_days: Number of days data is considered fresh
        """
        self.cache_days = cache_days
        logger.info(f"StorageManager initialized with TimescaleDB (cache_days={cache_days})")
    
    def save_stock_data(self, ticker: str, data: pd.DataFrame, exchange: Optional[str] = None) -> bool:
        """
        Save stock OHLCV data to TimescaleDB.
        
        Args:
            ticker: Stock ticker symbol
            data: DataFrame with OHLCV data (index should be datetime)
            exchange: Exchange code (optional)
        
        Returns:
            True if successful, False otherwise
        """
        if data is None or data.empty:
            logger.warning(f"No data to save for {ticker}")
            return False
        
        try:
            from app.database.connection import get_session
            with get_session() as session:
                # Delete existing data for this ticker to avoid duplicates
                # (alternatively, we could use upsert/merge)
                session.query(StockPrice).filter(StockPrice.ticker == ticker).delete()
                
                # Prepare records for bulk insert
                records = []
                for timestamp, row in data.iterrows():
                    # Ensure timestamp is datetime
                    if isinstance(timestamp, pd.Timestamp):
                        timestamp = timestamp.to_pydatetime()
                    
                    records.append(StockPrice(
                        ticker=ticker,
                        timestamp=timestamp,
                        open=float(row['Open']),
                        high=float(row['High']),
                        low=float(row['Low']),
                        close=float(row['Close']),
                        volume=int(row['Volume']),
                        adj_close=float(row.get('Adj Close', row['Close'])) if 'Adj Close' in row else None,
                        created_at=datetime.utcnow()
                    ))
                
                # Bulk insert
                session.bulk_save_objects(records)
                
                # Update or create metadata
                metadata = session.query(StockMetadata).filter(
                    StockMetadata.ticker == ticker
                ).first()
                
                if metadata is None:
                    metadata = StockMetadata(
                        ticker=ticker,
                        exchange=exchange
                    )
                    session.add(metadata)
                
                metadata.last_updated = datetime.utcnow()
                metadata.total_records = len(records)
                metadata.first_date = data.index.min().to_pydatetime() if hasattr(data.index.min(), 'to_pydatetime') else data.index.min()
                metadata.last_date = data.index.max().to_pydatetime() if hasattr(data.index.max(), 'to_pydatetime') else data.index.max()
                metadata.updated_at = datetime.utcnow()
                
                session.commit()
                
                date_range = f"{metadata.first_date.date()} to {metadata.last_date.date()}"
                logger.debug(f"Saved {len(records)} records for {ticker} to TimescaleDB ({date_range})")
                return True
                
        except Exception as e:
            logger.error(f"Failed to save data for {ticker}: {e}")
            return False
    
    def load_stock_data(self, ticker: str, max_age_days: Optional[int] = None) -> Optional[pd.DataFrame]:
        """
        Load stock data from TimescaleDB.
        
        Args:
            ticker: Stock ticker symbol
            max_age_days: Maximum age of cached data in days (None = use default)
        
        Returns:
            DataFrame with stock data or None if not found/expired
        """
        if max_age_days is None:
            max_age_days = self.cache_days
        
        try:
            from app.database.connection import get_session
            with get_session() as session:
                # Check metadata first
                metadata = session.query(StockMetadata).filter(
                    StockMetadata.ticker == ticker
                ).first()
                
                if metadata is None:
                    logger.debug(f"No cached data found in TimescaleDB for {ticker}")
                    return None
                
                # Check age
                age = datetime.utcnow() - metadata.last_updated
                if age > timedelta(days=max_age_days):
                    logger.info(f"Cached data for {ticker} is stale ({age.days} days old, max: {max_age_days} days)")
                    return None
                
                logger.debug(f"Found fresh data in TimescaleDB for {ticker} (age: {age.days} days)")
                
                # Load data
                prices = session.query(StockPrice).filter(
                    StockPrice.ticker == ticker
                ).order_by(StockPrice.timestamp).all()
                
                if not prices:
                    logger.debug(f"No price data found for {ticker}")
                    return None
                
                # Convert to DataFrame
                data = pd.DataFrame([
                    {
                        'Open': p.open,
                        'High': p.high,
                        'Low': p.low,
                        'Close': p.close,
                        'Volume': p.volume,
                        'Adj Close': p.adj_close if p.adj_close else p.close
                    }
                    for p in prices
                ])
                
                # Set index to timestamp
                data.index = pd.DatetimeIndex([p.timestamp for p in prices])
                data.index.name = 'Date'
                
                date_range = f"{data.index.min().date()} to {data.index.max().date()}"
                logger.debug(f"Loaded {len(data)} records for {ticker} from TimescaleDB ({date_range})")
                return data
                
        except Exception as e:
            logger.error(f"Failed to load data for {ticker}: {e}")
            return None
    
    def is_data_fresh(self, ticker: str, max_age_days: Optional[int] = None) -> bool:
        """
        Check if cached data is fresh enough.
        
        Args:
            ticker: Stock ticker symbol
            max_age_days: Maximum age in days (None = use default)
        
        Returns:
            True if data is fresh, False otherwise
        """
        if max_age_days is None:
            max_age_days = self.cache_days
        
        try:
            from app.database.connection import get_session
            with get_session() as session:
                metadata = session.query(StockMetadata).filter(
                    StockMetadata.ticker == ticker
                ).first()
                
                if metadata is None:
                    return False
                
                age = datetime.utcnow() - metadata.last_updated
                return age <= timedelta(days=max_age_days)
                
        except Exception as e:
            logger.error(f"Error checking data freshness for {ticker}: {e}")
            return False
    
    def clear_cache(self, ticker: Optional[str] = None) -> None:
        """
        Clear cached data from TimescaleDB.
        
        Args:
            ticker: Specific ticker to clear (None = clear all)
        """
        try:
            from app.database.connection import get_session
            with get_session() as session:
                if ticker:
                    # Clear specific ticker
                    session.query(StockPrice).filter(StockPrice.ticker == ticker).delete()
                    session.query(StockMetadata).filter(StockMetadata.ticker == ticker).delete()
                    logger.info(f"Cleared cache for {ticker}")
                else:
                    # Clear all
                    session.query(StockPrice).delete()
                    session.query(StockMetadata).delete()
                    logger.info("Cleared all cached data")
                
                session.commit()
                
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
    
    def get_cached_tickers(self) -> List[str]:
        """
        Get list of all cached tickers.
        
        Returns:
            List of ticker symbols
        """
        try:
            from app.database.connection import get_session
            with get_session() as session:
                tickers = session.query(StockMetadata.ticker).filter(
                    StockMetadata.is_active == True
                ).all()
                return [t[0] for t in tickers]
                
        except Exception as e:
            logger.error(f"Failed to get cached tickers: {e}")
            return []
    
    def get_cache_info(self) -> Dict[str, Any]:
        """
        Get information about cached data in TimescaleDB.
        
        Returns:
            Dictionary with cache statistics
        """
        try:
            from app.database.connection import get_session
            with get_session() as session:
                # Get metadata count
                ticker_count = session.query(func.count(StockMetadata.ticker)).scalar()
                
                # Get total records
                total_records = session.query(func.count(StockPrice.ticker)).scalar()
                
                # Get database size (approximate)
                result = session.execute(text(
                    """
                    SELECT 
                        pg_size_pretty(pg_total_relation_size('stock_prices')) as prices_size,
                        pg_size_pretty(pg_total_relation_size('stock_metadata')) as metadata_size
                    """
                ))
                sizes = result.fetchone()
                
                # Get date range
                date_range = session.query(
                    func.min(StockPrice.timestamp),
                    func.max(StockPrice.timestamp)
                ).first()
                
                # Get tickers list
                tickers = session.query(StockMetadata.ticker).all()
                ticker_list = [t[0] for t in tickers]
                
                return {
                    "storage_type": "TimescaleDB",
                    "total_tickers": ticker_count or 0,
                    "total_records": total_records or 0,
                    "tickers": ticker_list,
                    "date_range": {
                        "earliest": date_range[0].isoformat() if date_range[0] else None,
                        "latest": date_range[1].isoformat() if date_range[1] else None
                    },
                    "database_size": {
                        "prices_table": sizes[0] if sizes else "N/A",
                        "metadata_table": sizes[1] if sizes else "N/A"
                    }
                }
                
        except Exception as e:
            logger.error(f"Failed to get cache info: {e}")
            return {
                "storage_type": "TimescaleDB",
                "total_tickers": 0,
                "total_records": 0,
                "tickers": [],
                "error": str(e)
            }
    
    def get_ticker_info(self, ticker: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific ticker.
        
        Args:
            ticker: Stock ticker symbol
        
        Returns:
            Dictionary with ticker information or None
        """
        try:
            from app.database.connection import get_session
            with get_session() as session:
                metadata = session.query(StockMetadata).filter(
                    StockMetadata.ticker == ticker
                ).first()
                
                if metadata is None:
                    return None
                
                return metadata.to_dict()
                
        except Exception as e:
            logger.error(f"Failed to get ticker info for {ticker}: {e}")
            return None
    
    def cleanup_old_data(self, days_to_keep: int = 365) -> int:
        """
        Remove data older than specified days.
        
        Args:
            days_to_keep: Number of days of data to keep
        
        Returns:
            Number of records deleted
        """
        try:
            from app.database.connection import get_session
            with get_session() as session:
                cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
                
                deleted = session.query(StockPrice).filter(
                    StockPrice.timestamp < cutoff_date
                ).delete()
                
                session.commit()
                
                logger.info(f"Cleaned up {deleted} records older than {days_to_keep} days")
                return deleted
                
        except Exception as e:
            logger.error(f"Failed to cleanup old data: {e}")
            return 0
    
    def save_fundamental_data(self, ticker: str, fundamental_data: Dict[str, Any], timestamp: Optional[datetime] = None) -> bool:
        """
        Save fundamental data to database (supports historical snapshots).
        
        Args:
            ticker: Stock ticker symbol
            fundamental_data: Dictionary with fundamental metrics
            timestamp: Specific timestamp for this snapshot (default: now)
        
        Returns:
            True if successful, False otherwise
        """
        if not fundamental_data:
            logger.warning(f"No fundamental data to save for {ticker}")
            return False
        
        try:
            from app.database.connection import get_session
            with get_session() as session:
                # Use provided timestamp or current time
                snapshot_time = timestamp or datetime.utcnow()
                
                # Create fundamental record
                fundamental = StockFundamentals(
                    ticker=ticker,
                    timestamp=snapshot_time,
                    trailing_pe=fundamental_data.get('trailingPE'),
                    forward_pe=fundamental_data.get('forwardPE'),
                    price_to_book=fundamental_data.get('priceToBook'),
                    price_to_sales=fundamental_data.get('priceToSalesTrailing12Months'),
                    peg_ratio=fundamental_data.get('pegRatio'),
                    market_cap=fundamental_data.get('marketCap'),
                    enterprise_value=fundamental_data.get('enterpriseValue'),
                    debt_to_equity=fundamental_data.get('debtToEquity'),
                    current_ratio=fundamental_data.get('currentRatio'),
                    quick_ratio=fundamental_data.get('quickRatio'),
                    profit_margin=fundamental_data.get('profitMargins'),
                    operating_margin=fundamental_data.get('operatingMargins'),
                    return_on_assets=fundamental_data.get('returnOnAssets'),
                    return_on_equity=fundamental_data.get('returnOnEquity'),
                    revenue_growth=fundamental_data.get('revenueGrowth'),
                    earnings_growth=fundamental_data.get('earningsGrowth'),
                    dividend_yield=fundamental_data.get('dividendYield'),
                    payout_ratio=fundamental_data.get('payoutRatio'),
                    beta=fundamental_data.get('beta'),
                    sector=fundamental_data.get('sector'),
                    industry=fundamental_data.get('industry')
                )
                
                # Use merge to allow updating specific timestamp, or add for new snapshot
                session.merge(fundamental)
                session.commit()
                
                logger.debug(f"Saved fundamental data for {ticker} at {snapshot_time}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to save fundamental data for {ticker}: {e}")
            return False
    
    def load_fundamental_data_history(self, ticker: str, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """
        Load historical fundamental data from database.
        
        Args:
            ticker: Stock ticker symbol
            start_date: Optional start date for filtering
            end_date: Optional end date for filtering
        
        Returns:
            List of dictionaries with historical fundamental data
        """
        try:
            from app.database.connection import get_session
            with get_session() as session:
                query = session.query(StockFundamentals).filter(
                    StockFundamentals.ticker == ticker
                )
                
                # Apply date filters
                if start_date:
                    query = query.filter(StockFundamentals.timestamp >= start_date)
                if end_date:
                    query = query.filter(StockFundamentals.timestamp <= end_date)
                
                # Order by timestamp descending (newest first)
                fundamentals = query.order_by(StockFundamentals.timestamp.desc()).all()
                
                if not fundamentals:
                    logger.debug(f"No historical fundamental data found for {ticker}")
                    return []
                
                return [f.to_dict() for f in fundamentals]
                
        except Exception as e:
            logger.error(f"Failed to load fundamental history for {ticker}: {e}")
            return []
    
    def load_fundamental_data(self, ticker: str, max_age_days: Optional[int] = 30) -> Optional[Dict[str, Any]]:
        """
        Load latest fundamental data from database.
        
        Args:
            ticker: Stock ticker symbol
            max_age_days: Maximum age of data in days (default: 30)
        
        Returns:
            Dictionary with fundamental data or None if not found/expired
        """
        try:
            from app.database.connection import get_session
            with get_session() as session:
                # Get latest fundamental data
                fundamental = session.query(StockFundamentals).filter(
                    StockFundamentals.ticker == ticker
                ).order_by(StockFundamentals.timestamp.desc()).first()
                
                if fundamental is None:
                    logger.debug(f"No fundamental data found for {ticker}")
                    return None
                
                # Check age
                if max_age_days:
                    age = datetime.utcnow() - fundamental.timestamp
                    if age > timedelta(days=max_age_days):
                        logger.info(f"Fundamental data for {ticker} is stale ({age.days} days old)")
                        return None
                
                return fundamental.to_dict()
                
        except Exception as e:
            logger.error(f"Failed to load fundamental data for {ticker}: {e}")
            return None
    
    def save_technical_indicators(self, ticker: str, indicators_df: pd.DataFrame) -> bool:
        """
        Save technical indicators to database.
        
        Args:
            ticker: Stock ticker symbol
            indicators_df: DataFrame with technical indicators (index should be datetime)
        
        Returns:
            True if successful, False otherwise
        """
        if indicators_df is None or indicators_df.empty:
            logger.warning(f"No technical indicators to save for {ticker}")
            return False
        
        try:
            from app.database.connection import get_session
            with get_session() as session:
                # Delete existing indicators for this ticker to avoid duplicates
                session.query(StockTechnicalIndicators).filter(
                    StockTechnicalIndicators.ticker == ticker
                ).delete()
                
                # Prepare records for bulk insert
                records = []
                for timestamp, row in indicators_df.iterrows():
                    # Ensure timestamp is datetime
                    if isinstance(timestamp, pd.Timestamp):
                        timestamp = timestamp.to_pydatetime()
                    
                    # Helper function to safely get float values
                    def safe_float(value):
                        if pd.isna(value):
                            return None
                        return float(value)
                    
                    def safe_int(value):
                        if pd.isna(value):
                            return None
                        return int(value)
                    
                    records.append(StockTechnicalIndicators(
                        ticker=ticker,
                        timestamp=timestamp,
                        sma_20=safe_float(row.get('SMA_20')),
                        sma_50=safe_float(row.get('SMA_50')),
                        sma_100=safe_float(row.get('SMA_100')),
                        sma_200=safe_float(row.get('SMA_200')),
                        ema_12=safe_float(row.get('EMA_12')),
                        ema_26=safe_float(row.get('EMA_26')),
                        ema_50=safe_float(row.get('EMA_50')),
                        ema_200=safe_float(row.get('EMA_200')),
                        rsi=safe_float(row.get('RSI')),
                        macd=safe_float(row.get('MACD')),
                        macd_signal=safe_float(row.get('MACD_signal')),
                        macd_histogram=safe_float(row.get('MACD_histogram')),
                        atr=safe_float(row.get('ATR')),
                        bb_upper=safe_float(row.get('BB_upper')),
                        bb_middle=safe_float(row.get('BB_middle')),
                        bb_lower=safe_float(row.get('BB_lower')),
                        obv=safe_int(row.get('OBV')),
                        volume_sma_20=safe_int(row.get('Volume_SMA_20')),
                        adx=safe_float(row.get('ADX')),
                        di_plus=safe_float(row.get('DI_plus')),
                        di_minus=safe_float(row.get('DI_minus')),
                        stoch_k=safe_float(row.get('STOCH_k')),
                        stoch_d=safe_float(row.get('STOCH_d')),
                        daily_return=safe_float(row.get('Daily_Return')),
                        cumulative_return=safe_float(row.get('Cumulative_Return')),
                        volatility_20d=safe_float(row.get('Volatility_20d')),
                        created_at=datetime.utcnow()
                    ))
                
                # Bulk insert
                session.bulk_save_objects(records)
                session.commit()
                
                logger.debug(f"Saved {len(records)} technical indicator records for {ticker}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to save technical indicators for {ticker}: {e}")
            return False
    
    def load_technical_indicators(self, ticker: str, max_age_days: Optional[int] = None) -> Optional[pd.DataFrame]:
        """
        Load technical indicators from database.
        
        Args:
            ticker: Stock ticker symbol
            max_age_days: Maximum age of data in days (None = use default)
        
        Returns:
            DataFrame with technical indicators or None if not found/expired
        """
        if max_age_days is None:
            max_age_days = self.cache_days
        
        try:
            from app.database.connection import get_session
            with get_session() as session:
                # Check if data exists and is fresh
                metadata = session.query(StockMetadata).filter(
                    StockMetadata.ticker == ticker
                ).first()
                
                if metadata is None:
                    return None
                
                # Check age
                age = datetime.utcnow() - metadata.last_updated
                if age > timedelta(days=max_age_days):
                    return None
                
                # Load technical indicators
                indicators = session.query(StockTechnicalIndicators).filter(
                    StockTechnicalIndicators.ticker == ticker
                ).order_by(StockTechnicalIndicators.timestamp).all()
                
                if not indicators:
                    return None
                
                # Convert to DataFrame
                data = pd.DataFrame([ind.to_dict() for ind in indicators])
                data.set_index('timestamp', inplace=True)
                data.index.name = 'Date'
                
                logger.debug(f"Loaded {len(data)} technical indicator records for {ticker}")
                return data
                
        except Exception as e:
            logger.error(f"Failed to load technical indicators for {ticker}: {e}")
            return None
