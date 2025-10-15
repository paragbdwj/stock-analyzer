"""
Data acquisition service using yfinance.
"""
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd
import yfinance as yf
from tqdm import tqdm

from app.config import config
from app.utils.logger import get_logger
from app.utils.storage import StorageManager


logger = get_logger(__name__)


class DataService:
    """
    Service for fetching stock data from Yahoo Finance.
    """
    
    def __init__(self, storage_manager: Optional[StorageManager] = None):
        """
        Initialize data service.
        
        Args:
            storage_manager: Storage manager for caching data
        """
        cache_days = config.data_storage.get("cache_days", 1)
        self.storage = storage_manager or StorageManager(cache_days=cache_days)
        self.cache_days = cache_days
        self.max_workers = config.data_fetch.get("max_workers", 10)
        self.retry_attempts = config.data_fetch.get("retry_attempts", 3)
        self.retry_delay = config.data_fetch.get("retry_delay", 2)
    
    def fetch_stock_data(
        self,
        ticker: str,
        period: str = "1y",
        interval: str = "1d",
        force_refresh: bool = False,
        include_indicators: bool = False,
        include_fundamentals: bool = False
    ) -> Optional[pd.DataFrame]:
        """
        Fetch stock OHLCV data for a single ticker with optional technical indicators and fundamentals.
        
        Args:
            ticker: Stock ticker symbol
            period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
            force_refresh: Force refresh data even if cached
            include_indicators: Calculate and store technical indicators
            include_fundamentals: Fetch and store fundamental data
        
        Returns:
            DataFrame with OHLCV data or None if failed
        """
        # Check TimescaleDB cache first
        if not force_refresh:
            cached_data = self.storage.load_stock_data(ticker, max_age_days=self.cache_days)
            if cached_data is not None:
                logger.info(f"✓ Using cached data from TimescaleDB for {ticker} ({len(cached_data)} records)")
                return cached_data
        
        # Data not in DB or force_refresh=True, fetch from Yahoo Finance
        logger.info(f"→ Fetching data from Yahoo Finance API for {ticker}")
        
        for attempt in range(self.retry_attempts):
            try:
                logger.debug(f"Fetching data for {ticker} (attempt {attempt + 1}/{self.retry_attempts})")
                
                stock = yf.Ticker(ticker)
                data = stock.history(period=period, interval=interval)
                
                if data.empty:
                    logger.warning(f"No data returned for {ticker}")
                    return None
                
                # Save to TimescaleDB
                logger.info(f"→ Saving {len(data)} records to TimescaleDB for {ticker}")
                save_success = self.storage.save_stock_data(ticker, data)
                
                # Calculate and save technical indicators if requested
                if include_indicators and interval == "1d":  # Only for daily data
                    logger.info(f"→ Calculating technical indicators for {ticker}")
                    from app.services.technical_service import TechnicalService
                    tech_service = TechnicalService()
                    indicators_df = tech_service.calculate_indicators(ticker, data)
                    if indicators_df is not None:
                        self.storage.save_technical_indicators(ticker, indicators_df)
                        logger.info(f"✓ Technical indicators saved for {ticker}")
                
                # Fetch and save fundamental data if requested
                if include_fundamentals:
                    logger.info(f"→ Fetching fundamental data for {ticker}")
                    try:
                        info = stock.info
                        if info and len(info) > 1:
                            self.storage.save_fundamental_data(ticker, info)
                            logger.info(f"✓ Fundamental data saved for {ticker}")
                    except Exception as e:
                        logger.warning(f"Could not fetch fundamental data for {ticker}: {e}")
                
                if save_success:
                    logger.info(f"✓ Data saved to TimescaleDB for {ticker}")
                    # Load back from DB to ensure consistency
                    db_data = self.storage.load_stock_data(ticker, max_age_days=self.cache_days)
                    if db_data is not None:
                        logger.info(f"✓ Verified data in TimescaleDB for {ticker}")
                        return db_data
                
                # If DB save/load failed, return the fetched data anyway
                logger.warning(f"⚠ Using fetched data directly (DB save/load failed) for {ticker}")
                return data
                
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed for {ticker}: {e}")
                if attempt < self.retry_attempts - 1:
                    time.sleep(self.retry_delay)
                else:
                    logger.error(f"Failed to fetch data for {ticker} after {self.retry_attempts} attempts")
                    return None
        
        return None
    
    def fetch_multiple_stocks(
        self,
        tickers: List[str],
        period: str = "1y",
        interval: str = "1d",
        force_refresh: bool = False,
        show_progress: bool = True,
        include_indicators: bool = False,
        include_fundamentals: bool = False
    ) -> Dict[str, pd.DataFrame]:
        """
        Fetch stock data for multiple tickers in parallel with optional indicators and fundamentals.
        
        Args:
            tickers: List of stock ticker symbols
            period: Time period
            interval: Data interval
            force_refresh: Force refresh data even if cached
            show_progress: Show progress bar
            include_indicators: Calculate and store technical indicators
            include_fundamentals: Fetch and store fundamental data
        
        Returns:
            Dictionary mapping ticker to DataFrame
        """
        results = {}
        
        # Use ThreadPoolExecutor for parallel fetching
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_ticker = {
                executor.submit(
                    self.fetch_stock_data,
                    ticker,
                    period,
                    interval,
                    force_refresh,
                    include_indicators,
                    include_fundamentals
                ): ticker
                for ticker in tickers
            }
            
            # Process completed tasks with progress bar
            iterator = as_completed(future_to_ticker)
            if show_progress:
                iterator = tqdm(iterator, total=len(tickers), desc="Fetching stock data")
            
            for future in iterator:
                ticker = future_to_ticker[future]
                try:
                    data = future.result()
                    if data is not None:
                        results[ticker] = data
                except Exception as e:
                    logger.error(f"Error processing {ticker}: {e}")
        
        logger.info(f"Successfully fetched data for {len(results)}/{len(tickers)} tickers")
        return results
    
    def get_ticker_info(self, ticker: str) -> Optional[Dict]:
        """
        Get detailed information about a ticker.
        
        Args:
            ticker: Stock ticker symbol
        
        Returns:
            Dictionary with ticker info or None if failed
        """
        try:
            stock = yf.Ticker(ticker)
            return stock.info
        except Exception as e:
            logger.error(f"Failed to get info for {ticker}: {e}")
            return None
    
    @staticmethod
    def get_nse_tickers(top_n: Optional[int] = None) -> List[str]:
        """
        Get list of NSE stock tickers.
        Note: This is a simplified version. For production, you'd want to fetch
        this from a more reliable source like NSE's official website or API.
        
        Args:
            top_n: Limit to top N stocks (by market cap)
        
        Returns:
            List of NSE ticker symbols with .NS suffix
        """
        # Common NSE stocks for demonstration
        # In production, you'd fetch this from NSE or a stocks database
        common_stocks = [
            "RELIANCE", "TCS", "HDFCBANK", "INFY", "HINDUNILVR",
            "ICICIBANK", "BHARTIARTL", "ITC", "SBIN", "BAJFINANCE",
            "KOTAKBANK", "LT", "ASIANPAINT", "AXISBANK", "MARUTI",
            "TITAN", "SUNPHARMA", "ULTRACEMCO", "NESTLEIND", "WIPRO",
            "HCLTECH", "TECHM", "POWERGRID", "NTPC", "TATAMOTORS",
            "M&M", "TATASTEEL", "ONGC", "ADANIENT", "ADANIPORTS"
        ]
        
        # Add .NS suffix for NSE
        nse_tickers = [f"{stock}.NS" for stock in common_stocks]
        
        if top_n:
            return nse_tickers[:top_n]
        
        return nse_tickers
    
    @staticmethod
    def get_nasdaq_tickers(top_n: Optional[int] = None) -> List[str]:
        """
        Get list of NASDAQ stock tickers.
        
        Args:
            top_n: Limit to top N stocks
        
        Returns:
            List of NASDAQ ticker symbols
        """
        # Common NASDAQ stocks for demonstration
        common_stocks = [
            "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA",
            "META", "TSLA", "AVGO", "COST", "NFLX",
            "AMD", "PEP", "ADBE", "CSCO", "CMCSA",
            "INTC", "QCOM", "TMUS", "AMGN", "HON",
            "TXN", "INTU", "AMAT", "SBUX", "ISRG",
            "BKNG", "GILD", "VRTX", "ADI", "MDLZ"
        ]
        
        if top_n:
            return common_stocks[:top_n]
        
        return common_stocks
    
    def get_exchange_tickers(self, exchange: str, top_n: Optional[int] = None) -> List[str]:
        """
        Get list of tickers for a given exchange.
        
        Args:
            exchange: Exchange code (NSE, BSE, NASDAQ, NYSE)
            top_n: Limit to top N stocks
        
        Returns:
            List of ticker symbols
        """
        exchange = exchange.upper()
        
        if exchange == "NSE":
            return self.get_nse_tickers(top_n)
        elif exchange == "NASDAQ":
            return self.get_nasdaq_tickers(top_n)
        elif exchange == "NYSE":
            # For demonstration, using some common NYSE stocks
            nyse_stocks = [
                "JPM", "V", "WMT", "JNJ", "PG", "MA", "XOM",
                "BAC", "CVX", "ABBV", "KO", "PFE", "MRK", "DIS"
            ]
            if top_n:
                return nyse_stocks[:top_n]
            return nyse_stocks
        elif exchange == "BSE":
            # BSE uses .BO suffix
            bse_stocks = self.get_nse_tickers(top_n)
            return [ticker.replace(".NS", ".BO") for ticker in bse_stocks]
        else:
            logger.warning(f"Unknown exchange: {exchange}. Using NSE as default.")
            return self.get_nse_tickers(top_n)
    
    def get_latest_price(self, ticker: str) -> Optional[float]:
        """
        Get the latest closing price for a ticker.
        
        Args:
            ticker: Stock ticker symbol
        
        Returns:
            Latest close price or None if not available
        """
        data = self.fetch_stock_data(ticker, period="5d", interval="1d")
        if data is not None and not data.empty:
            return float(data['Close'].iloc[-1])
        return None

