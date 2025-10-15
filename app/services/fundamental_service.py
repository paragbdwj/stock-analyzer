"""
Fundamental analysis service using yfinance and optionally FMP API.
"""
import os
from typing import Dict, Optional
import yfinance as yf

from app.config import config
from app.utils.logger import get_logger
from app.models.schemas import FundamentalData


logger = get_logger(__name__)

# Optional FMP support
try:
    import fundamentalanalysis as fa
    HAS_FMP = True
except ImportError:
    HAS_FMP = False
    logger.info("fundamentalanalysis library not available. Using yfinance only for fundamental data.")


class FundamentalService:
    """
    Service for fetching fundamental data.
    """
    
    def __init__(self):
        """Initialize fundamental analysis service."""
        self.fmp_api_key = config.settings.fmp_api_key
        self.use_fmp = HAS_FMP and self.fmp_api_key is not None
        
        if self.use_fmp:
            logger.info("Using Financial Modeling Prep API for enhanced fundamental data")
        else:
            logger.info("Using yfinance for fundamental data")
    
    def get_fundamental_data(self, ticker: str) -> Optional[FundamentalData]:
        """
        Get fundamental data for a ticker.
        
        Args:
            ticker: Stock ticker symbol
        
        Returns:
            FundamentalData object or None if failed
        """
        try:
            # Primary method: Use yfinance
            fundamental_data = self._get_yfinance_data(ticker)
            
            # Optionally enhance with FMP data
            if self.use_fmp and fundamental_data:
                fmp_data = self._get_fmp_data(ticker)
                if fmp_data:
                    # Merge FMP data with yfinance data
                    fundamental_data = self._merge_fundamental_data(fundamental_data, fmp_data)
            
            return fundamental_data
            
        except Exception as e:
            logger.error(f"Failed to get fundamental data for {ticker}: {e}")
            return None
    
    def _get_yfinance_data(self, ticker: str) -> Optional[FundamentalData]:
        """
        Get fundamental data using yfinance.
        
        Args:
            ticker: Stock ticker symbol
        
        Returns:
            FundamentalData object or None if failed
        """
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            if not info or len(info) <= 1:
                logger.warning(f"No fundamental data available for {ticker}")
                return None
            
            # Extract fundamental metrics
            fundamental_data = FundamentalData(
                ticker=ticker,
                trailing_pe=info.get('trailingPE'),
                forward_pe=info.get('forwardPE'),
                price_to_book=info.get('priceToBook'),
                debt_to_equity=info.get('debtToEquity'),
                current_ratio=info.get('currentRatio'),
                market_cap=info.get('marketCap'),
                sector=info.get('sector'),
                industry=info.get('industry'),
                beta=info.get('beta'),
                dividend_yield=info.get('dividendYield')
            )
            
            logger.debug(f"Retrieved fundamental data for {ticker} from yfinance")
            return fundamental_data
            
        except Exception as e:
            logger.error(f"Error getting yfinance data for {ticker}: {e}")
            return None
    
    def _get_fmp_data(self, ticker: str) -> Optional[Dict]:
        """
        Get fundamental data using Financial Modeling Prep API.
        
        Args:
            ticker: Stock ticker symbol (without exchange suffix)
        
        Returns:
            Dictionary with FMP data or None if failed
        """
        if not self.use_fmp:
            return None
        
        try:
            # Remove exchange suffix for FMP API
            clean_ticker = ticker.replace('.NS', '').replace('.BO', '')
            
            # Get key metrics
            key_metrics = fa.key_metrics(clean_ticker, self.fmp_api_key, period="annual")
            
            if key_metrics is not None and not key_metrics.empty:
                latest_metrics = key_metrics.iloc[0].to_dict()
                logger.debug(f"Retrieved FMP data for {ticker}")
                return latest_metrics
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting FMP data for {ticker}: {e}")
            return None
    
    def _merge_fundamental_data(
        self,
        yfinance_data: FundamentalData,
        fmp_data: Dict
    ) -> FundamentalData:
        """
        Merge yfinance and FMP fundamental data.
        
        Args:
            yfinance_data: FundamentalData from yfinance
            fmp_data: Dictionary with FMP data
        
        Returns:
            Merged FundamentalData object
        """
        # FMP data can be used to fill in missing values or provide additional metrics
        # For now, we prioritize yfinance data and use FMP as fallback
        
        if fmp_data:
            # Example: Fill in missing P/E ratio from FMP
            if yfinance_data.trailing_pe is None and 'peRatio' in fmp_data:
                yfinance_data.trailing_pe = fmp_data['peRatio']
            
            # Add more field mappings as needed
        
        return yfinance_data
    
    def get_metric_value(self, ticker: str, metric_name: str) -> Optional[float]:
        """
        Get a specific fundamental metric value.
        
        Args:
            ticker: Stock ticker symbol
            metric_name: Name of the metric (e.g., 'trailing_pe', 'market_cap')
        
        Returns:
            Metric value or None if not available
        """
        try:
            fundamental_data = self.get_fundamental_data(ticker)
            
            if fundamental_data is None:
                return None
            
            # Map common metric names
            metric_map = {
                'trailing_pe': fundamental_data.trailing_pe,
                'forward_pe': fundamental_data.forward_pe,
                'price_to_book': fundamental_data.price_to_book,
                'debt_to_equity': fundamental_data.debt_to_equity,
                'current_ratio': fundamental_data.current_ratio,
                'market_cap': fundamental_data.market_cap,
                'beta': fundamental_data.beta,
                'dividend_yield': fundamental_data.dividend_yield,
                # Aliases
                'pe': fundamental_data.trailing_pe,
                'pb': fundamental_data.price_to_book,
                'de': fundamental_data.debt_to_equity
            }
            
            normalized_name = metric_name.lower()
            value = metric_map.get(normalized_name)
            
            return float(value) if value is not None else None
            
        except Exception as e:
            logger.error(f"Error getting metric {metric_name} for {ticker}: {e}")
            return None
    
    def get_company_info(self, ticker: str) -> Optional[Dict]:
        """
        Get general company information.
        
        Args:
            ticker: Stock ticker symbol
        
        Returns:
            Dictionary with company info or None if failed
        """
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            company_info = {
                'name': info.get('longName'),
                'sector': info.get('sector'),
                'industry': info.get('industry'),
                'country': info.get('country'),
                'website': info.get('website'),
                'employees': info.get('fullTimeEmployees'),
                'description': info.get('longBusinessSummary')
            }
            
            return company_info
            
        except Exception as e:
            logger.error(f"Error getting company info for {ticker}: {e}")
            return None
    
    def get_financial_ratios(self, ticker: str) -> Optional[Dict[str, float]]:
        """
        Get key financial ratios.
        
        Args:
            ticker: Stock ticker symbol
        
        Returns:
            Dictionary with financial ratios or None if failed
        """
        try:
            fundamental_data = self.get_fundamental_data(ticker)
            
            if fundamental_data is None:
                return None
            
            ratios = {
                'trailing_pe': fundamental_data.trailing_pe,
                'forward_pe': fundamental_data.forward_pe,
                'price_to_book': fundamental_data.price_to_book,
                'debt_to_equity': fundamental_data.debt_to_equity,
                'current_ratio': fundamental_data.current_ratio,
                'beta': fundamental_data.beta,
                'dividend_yield': fundamental_data.dividend_yield
            }
            
            # Filter out None values
            return {k: v for k, v in ratios.items() if v is not None}
            
        except Exception as e:
            logger.error(f"Error getting financial ratios for {ticker}: {e}")
            return None

