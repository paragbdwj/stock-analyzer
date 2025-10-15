"""
Stock scanner service - orchestrates data fetching, analysis, and filtering.
"""
import time
from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd

from app.config import config
from app.utils.logger import get_logger
from app.models.schemas import (
    ScanRequest, ScanResult, StockInfo, FilterRule,
    TechnicalIndicators, FundamentalData
)
from app.services.data_service import DataService
from app.services.technical_service import TechnicalService
from app.services.fundamental_service import FundamentalService


logger = get_logger(__name__)


class ScannerService:
    """
    Main scanner service that orchestrates stock scanning.
    """
    
    def __init__(self):
        """Initialize scanner service with required sub-services."""
        self.data_service = DataService()
        self.technical_service = TechnicalService()
        self.fundamental_service = FundamentalService()
    
    def scan_stocks(self, request: ScanRequest) -> ScanResult:
        """
        Scan stocks based on the provided criteria.
        
        Args:
            request: ScanRequest with filtering criteria
        
        Returns:
            ScanResult with matched stocks
        """
        start_time = time.time()
        
        logger.info(f"Starting stock scan for exchange: {request.exchange}")
        
        # Get list of tickers to scan
        if request.tickers:
            tickers = request.tickers
        else:
            tickers = self.data_service.get_exchange_tickers(request.exchange)
        
        logger.info(f"Scanning {len(tickers)} tickers")
        
        # Fetch data for all tickers
        period = config.data_fetch.get("period", "1y")
        interval = config.data_fetch.get("interval", "1d")
        
        stock_data = self.data_service.fetch_multiple_stocks(
            tickers=tickers,
            period=period,
            interval=interval,
            force_refresh=request.force_refresh
        )
        
        logger.info(f"Fetched data for {len(stock_data)} stocks")
        
        # Analyze and filter stocks
        matched_stocks = []
        
        for ticker, data in stock_data.items():
            try:
                stock_info = self._analyze_stock(ticker, data, request)
                
                if stock_info:
                    matched_stocks.append(stock_info)
                    
            except Exception as e:
                logger.error(f"Error analyzing {ticker}: {e}")
                continue
        
        # Calculate scan duration
        duration = time.time() - start_time
        
        # Create result
        result = ScanResult(
            timestamp=datetime.now(),
            exchange=request.exchange,
            total_scanned=len(stock_data),
            total_matched=len(matched_stocks),
            stocks=matched_stocks,
            scan_duration_seconds=round(duration, 2)
        )
        
        logger.info(
            f"Scan complete: {result.total_matched}/{result.total_scanned} stocks matched "
            f"in {result.scan_duration_seconds}s"
        )
        
        return result
    
    def _analyze_stock(
        self,
        ticker: str,
        data: pd.DataFrame,
        request: ScanRequest
    ) -> Optional[StockInfo]:
        """
        Analyze a single stock and check if it matches the filter criteria.
        
        Args:
            ticker: Stock ticker symbol
            data: OHLCV DataFrame
            request: ScanRequest with filter criteria
        
        Returns:
            StockInfo if stock matches criteria, None otherwise
        """
        # Calculate technical indicators
        data_with_indicators = self.technical_service.calculate_indicators(ticker, data)
        
        if data_with_indicators is None:
            return None
        
        # Get latest technical indicators
        technical_indicators = self.technical_service.get_latest_indicators(
            ticker,
            data_with_indicators
        )
        
        # Get fundamental data if needed
        fundamental_data = None
        if request.fundamental_filters:
            fundamental_data = self.fundamental_service.get_fundamental_data(ticker)
        
        # Get current price
        current_price = None
        if not data.empty:
            current_price = float(data['Close'].iloc[-1])
        
        # Check if stock matches filters
        matches, matched_filter_names = self._check_filters(
            data_with_indicators,
            technical_indicators,
            fundamental_data,
            request
        )
        
        if matches:
            # Create StockInfo object
            stock_info = StockInfo(
                ticker=ticker,
                technical=technical_indicators,
                fundamental=fundamental_data,
                current_price=current_price,
                matched_filters=matched_filter_names
            )
            
            return stock_info
        
        return None
    
    def _check_filters(
        self,
        data: pd.DataFrame,
        technical: Optional[TechnicalIndicators],
        fundamental: Optional[FundamentalData],
        request: ScanRequest
    ) -> tuple[bool, List[str]]:
        """
        Check if a stock matches the filter criteria.
        
        Args:
            data: DataFrame with indicators
            technical: TechnicalIndicators object
            fundamental: FundamentalData object
            request: ScanRequest with filters
        
        Returns:
            Tuple of (matches: bool, matched_filter_names: List[str])
        """
        matched_filters = []
        
        # Check technical filters
        technical_matches = []
        if request.technical_filters:
            for filter_rule in request.technical_filters:
                matches = self._apply_filter(filter_rule, data, technical, None)
                technical_matches.append(matches)
                if matches:
                    matched_filters.append(f"Technical: {filter_rule.field} {filter_rule.operator} {filter_rule.value}")
        
        # Check fundamental filters
        fundamental_matches = []
        if request.fundamental_filters:
            for filter_rule in request.fundamental_filters:
                matches = self._apply_filter(filter_rule, data, None, fundamental)
                fundamental_matches.append(matches)
                if matches:
                    matched_filters.append(f"Fundamental: {filter_rule.field} {filter_rule.operator} {filter_rule.value}")
        
        # Combine filter results based on logic
        all_matches = technical_matches + fundamental_matches
        
        if not all_matches:
            # No filters specified
            return True, []
        
        if request.filter_logic == "AND":
            # All filters must match
            overall_match = all(all_matches)
        else:  # OR
            # At least one filter must match
            overall_match = any(all_matches)
        
        return overall_match, matched_filters
    
    def _apply_filter(
        self,
        filter_rule: FilterRule,
        data: pd.DataFrame,
        technical: Optional[TechnicalIndicators],
        fundamental: Optional[FundamentalData]
    ) -> bool:
        """
        Apply a single filter rule.
        
        Args:
            filter_rule: FilterRule to apply
            data: DataFrame with indicators
            technical: TechnicalIndicators object
            fundamental: FundamentalData object
        
        Returns:
            True if filter matches, False otherwise
        """
        try:
            # Get the value to compare
            value = self._get_field_value(filter_rule.field, data, technical, fundamental)
            
            if value is None:
                return False
            
            # Apply comparison operator
            if filter_rule.operator == '<':
                return value < filter_rule.value
            elif filter_rule.operator == '>':
                return value > filter_rule.value
            elif filter_rule.operator == '<=':
                return value <= filter_rule.value
            elif filter_rule.operator == '>=':
                return value >= filter_rule.value
            elif filter_rule.operator == '==':
                return value == filter_rule.value
            elif filter_rule.operator == '!=':
                return value != filter_rule.value
            else:
                logger.warning(f"Unknown operator: {filter_rule.operator}")
                return False
                
        except Exception as e:
            logger.error(f"Error applying filter {filter_rule.field}: {e}")
            return False
    
    def _get_field_value(
        self,
        field_name: str,
        data: pd.DataFrame,
        technical: Optional[TechnicalIndicators],
        fundamental: Optional[FundamentalData]
    ) -> Optional[float]:
        """
        Get the value of a field from technical or fundamental data.
        
        Args:
            field_name: Name of the field
            data: DataFrame with indicators
            technical: TechnicalIndicators object
            fundamental: FundamentalData object
        
        Returns:
            Field value or None if not found
        """
        field_lower = field_name.lower()
        
        # Try to get from technical indicators first
        if technical:
            technical_fields = {
                'rsi': technical.rsi,
                'sma_20': technical.sma_20,
                'sma_50': technical.sma_50,
                'sma_100': technical.sma_100,
                'sma_200': technical.sma_200,
                'ema_12': technical.ema_12,
                'ema_26': technical.ema_26,
                'ema_50': technical.ema_50,
                'ema_200': technical.ema_200,
                'macd': technical.macd,
                'macd_signal': technical.macd_signal,
                'macd_histogram': technical.macd_histogram,
                'obv': technical.obv
            }
            
            if field_lower in technical_fields:
                return technical_fields[field_lower]
        
        # Try to get from fundamental data
        if fundamental:
            fundamental_fields = {
                'trailing_pe': fundamental.trailing_pe,
                'forward_pe': fundamental.forward_pe,
                'price_to_book': fundamental.price_to_book,
                'debt_to_equity': fundamental.debt_to_equity,
                'current_ratio': fundamental.current_ratio,
                'market_cap': fundamental.market_cap,
                'beta': fundamental.beta,
                'dividend_yield': fundamental.dividend_yield,
                # Aliases
                'pe': fundamental.trailing_pe,
                'pb': fundamental.price_to_book,
                'de': fundamental.debt_to_equity
            }
            
            if field_lower in fundamental_fields:
                return fundamental_fields[field_lower]
        
        # Try to get from DataFrame
        if data is not None and not data.empty:
            value = self.technical_service.get_indicator_value(data, field_name)
            if value is not None:
                return value
        
        logger.warning(f"Field '{field_name}' not found in technical or fundamental data")
        return None
    
    def get_stock_analysis(self, ticker: str, force_refresh: bool = False) -> Optional[StockInfo]:
        """
        Get detailed analysis for a single stock.
        
        Args:
            ticker: Stock ticker symbol
            force_refresh: Force refresh data from API even if cached in DB
        
        Returns:
            StockInfo with complete analysis or None if failed
        """
        try:
            # Fetch stock data (checks DB first, then falls back to yfinance)
            data = self.data_service.fetch_stock_data(ticker, force_refresh=force_refresh)
            
            if data is None:
                return None
            
            # Calculate technical indicators
            data_with_indicators = self.technical_service.calculate_indicators(ticker, data)
            
            # Get technical indicators
            technical_indicators = self.technical_service.get_latest_indicators(
                ticker,
                data_with_indicators
            )
            
            # Get fundamental data
            fundamental_data = self.fundamental_service.get_fundamental_data(ticker)
            
            # Get current price
            current_price = float(data['Close'].iloc[-1])
            
            # Create StockInfo
            stock_info = StockInfo(
                ticker=ticker,
                technical=technical_indicators,
                fundamental=fundamental_data,
                current_price=current_price,
                matched_filters=[]
            )
            
            return stock_info
            
        except Exception as e:
            logger.error(f"Failed to get analysis for {ticker}: {e}")
            return None

