"""
Technical analysis service using pandas-ta.
"""
from typing import Dict, List, Optional
import pandas as pd
import pandas_ta as ta

from app.config import config
from app.utils.logger import get_logger
from app.models.schemas import TechnicalIndicators


logger = get_logger(__name__)


class TechnicalService:
    """
    Service for calculating technical indicators.
    """
    
    def __init__(self):
        """Initialize technical analysis service."""
        self.indicators_config = config.technical_indicators
    
    def calculate_indicators(self, ticker: str, data: pd.DataFrame) -> Optional[pd.DataFrame]:
        """
        Calculate all technical indicators for a stock's OHLCV data.
        
        Args:
            ticker: Stock ticker symbol
            data: DataFrame with OHLCV data (must have Open, High, Low, Close, Volume)
        
        Returns:
            DataFrame with technical indicators or None if failed
        """
        if data is None or data.empty:
            logger.warning(f"No data provided for {ticker}")
            return None
        
        try:
            # Create a copy to avoid modifying original
            df = data.copy()
            
            # Ensure required columns exist
            required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
            if not all(col in df.columns for col in required_cols):
                logger.error(f"Missing required columns for {ticker}. Required: {required_cols}")
                return None
            
            # Calculate Simple Moving Averages (SMA)
            sma_periods = self.indicators_config.get("sma_periods", [20, 50, 100, 200])
            for period in sma_periods:
                df[f'SMA_{period}'] = ta.sma(df['Close'], length=period)
            
            # Calculate Exponential Moving Averages (EMA)
            ema_periods = self.indicators_config.get("ema_periods", [12, 26, 50, 200])
            for period in ema_periods:
                df[f'EMA_{period}'] = ta.ema(df['Close'], length=period)
            
            # Calculate RSI (Relative Strength Index)
            rsi_period = self.indicators_config.get("rsi_period", 14)
            df['RSI'] = ta.rsi(df['Close'], length=rsi_period)
            
            # Calculate MACD (Moving Average Convergence Divergence)
            macd_fast = self.indicators_config.get("macd_fast", 12)
            macd_slow = self.indicators_config.get("macd_slow", 26)
            macd_signal = self.indicators_config.get("macd_signal", 9)
            
            macd = ta.macd(df['Close'], fast=macd_fast, slow=macd_slow, signal=macd_signal)
            if macd is not None:
                df['MACD'] = macd[f'MACD_{macd_fast}_{macd_slow}_{macd_signal}']
                df['MACD_signal'] = macd[f'MACDs_{macd_fast}_{macd_slow}_{macd_signal}']
                df['MACD_histogram'] = macd[f'MACDh_{macd_fast}_{macd_slow}_{macd_signal}']
            
            # Calculate OBV (On-Balance Volume)
            df['OBV'] = ta.obv(df['Close'], df['Volume'])
            
            # Calculate Bollinger Bands
            bbands = ta.bbands(df['Close'], length=20, std=2)
            if bbands is not None and not bbands.empty:
                # Handle different pandas_ta versions
                if 'BBL_20_2.0' in bbands.columns:
                    df['BB_lower'] = bbands['BBL_20_2.0']
                    df['BB_middle'] = bbands['BBM_20_2.0']
                    df['BB_upper'] = bbands['BBU_20_2.0']
                elif 'BBL_20_2' in bbands.columns:
                    df['BB_lower'] = bbands['BBL_20_2']
                    df['BB_middle'] = bbands['BBM_20_2']
                    df['BB_upper'] = bbands['BBU_20_2']
                else:
                    # Try to extract columns that start with BB
                    cols = [c for c in bbands.columns if c.startswith('BB')]
                    if len(cols) >= 3:
                        df['BB_lower'] = bbands[cols[0]]
                        df['BB_middle'] = bbands[cols[1]]
                        df['BB_upper'] = bbands[cols[2]]
            
            # Calculate ATR (Average True Range) - for volatility
            df['ATR'] = ta.atr(df['High'], df['Low'], df['Close'], length=14)
            
            # Calculate Stochastic Oscillator
            stoch = ta.stoch(df['High'], df['Low'], df['Close'])
            if stoch is not None:
                df['STOCH_k'] = stoch['STOCHk_14_3_3']
                df['STOCH_d'] = stoch['STOCHd_14_3_3']
            
            # Calculate ADX (Average Directional Index) - trend strength
            adx = ta.adx(df['High'], df['Low'], df['Close'], length=14)
            if adx is not None:
                df['ADX'] = adx['ADX_14']
                df['DI_plus'] = adx['DMP_14']
                df['DI_minus'] = adx['DMN_14']
            
            # Calculate Volume SMA
            df['Volume_SMA_20'] = ta.sma(df['Volume'], length=20)
            
            # Calculate Daily Returns
            df['Daily_Return'] = df['Close'].pct_change()
            
            # Calculate Cumulative Returns
            df['Cumulative_Return'] = (1 + df['Daily_Return']).cumprod() - 1
            
            # Calculate Rolling Volatility (20-day)
            df['Volatility_20d'] = df['Daily_Return'].rolling(window=20).std()
            
            logger.debug(f"Calculated indicators for {ticker}")
            return df
            
        except Exception as e:
            logger.error(f"Failed to calculate indicators for {ticker}: {e}")
            return None
    
    def get_latest_indicators(self, ticker: str, data: pd.DataFrame) -> Optional[TechnicalIndicators]:
        """
        Get the latest technical indicators as a structured object.
        
        Args:
            ticker: Stock ticker symbol
            data: DataFrame with calculated indicators
        
        Returns:
            TechnicalIndicators object or None if failed
        """
        if data is None or data.empty:
            return None
        
        try:
            # Get the latest row
            latest = data.iloc[-1]
            
            # Create TechnicalIndicators object
            indicators = TechnicalIndicators(
                ticker=ticker,
                date=latest.name if hasattr(latest, 'name') else pd.Timestamp.now(),
                sma_20=latest.get('SMA_20'),
                sma_50=latest.get('SMA_50'),
                sma_100=latest.get('SMA_100'),
                sma_200=latest.get('SMA_200'),
                ema_12=latest.get('EMA_12'),
                ema_26=latest.get('EMA_26'),
                ema_50=latest.get('EMA_50'),
                ema_200=latest.get('EMA_200'),
                rsi=latest.get('RSI'),
                macd=latest.get('MACD'),
                macd_signal=latest.get('MACD_signal'),
                macd_histogram=latest.get('MACD_histogram'),
                obv=latest.get('OBV')
            )
            
            return indicators
            
        except Exception as e:
            logger.error(f"Failed to get latest indicators for {ticker}: {e}")
            return None
    
    def check_golden_cross(self, data: pd.DataFrame) -> bool:
        """
        Check for Golden Cross pattern (50-day SMA crosses above 200-day SMA).
        
        Args:
            data: DataFrame with SMA indicators
        
        Returns:
            True if golden cross detected, False otherwise
        """
        if data is None or len(data) < 2:
            return False
        
        try:
            # Check if we have the required SMAs
            if 'SMA_50' not in data.columns or 'SMA_200' not in data.columns:
                return False
            
            # Get last two rows
            current = data.iloc[-1]
            previous = data.iloc[-2]
            
            # Golden cross: SMA_50 crosses above SMA_200
            if (previous['SMA_50'] <= previous['SMA_200'] and 
                current['SMA_50'] > current['SMA_200']):
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking golden cross: {e}")
            return False
    
    def check_death_cross(self, data: pd.DataFrame) -> bool:
        """
        Check for Death Cross pattern (50-day SMA crosses below 200-day SMA).
        
        Args:
            data: DataFrame with SMA indicators
        
        Returns:
            True if death cross detected, False otherwise
        """
        if data is None or len(data) < 2:
            return False
        
        try:
            if 'SMA_50' not in data.columns or 'SMA_200' not in data.columns:
                return False
            
            current = data.iloc[-1]
            previous = data.iloc[-2]
            
            # Death cross: SMA_50 crosses below SMA_200
            if (previous['SMA_50'] >= previous['SMA_200'] and 
                current['SMA_50'] < current['SMA_200']):
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking death cross: {e}")
            return False
    
    def check_rsi_oversold(self, data: pd.DataFrame, threshold: float = 30) -> bool:
        """
        Check if RSI indicates oversold condition.
        
        Args:
            data: DataFrame with RSI indicator
            threshold: RSI threshold for oversold (default: 30)
        
        Returns:
            True if oversold, False otherwise
        """
        if data is None or data.empty or 'RSI' not in data.columns:
            return False
        
        try:
            current_rsi = data['RSI'].iloc[-1]
            return current_rsi < threshold
        except Exception:
            return False
    
    def check_rsi_overbought(self, data: pd.DataFrame, threshold: float = 70) -> bool:
        """
        Check if RSI indicates overbought condition.
        
        Args:
            data: DataFrame with RSI indicator
            threshold: RSI threshold for overbought (default: 70)
        
        Returns:
            True if overbought, False otherwise
        """
        if data is None or data.empty or 'RSI' not in data.columns:
            return False
        
        try:
            current_rsi = data['RSI'].iloc[-1]
            return current_rsi > threshold
        except Exception:
            return False
    
    def check_macd_bullish_crossover(self, data: pd.DataFrame) -> bool:
        """
        Check for MACD bullish crossover (MACD crosses above signal line).
        
        Args:
            data: DataFrame with MACD indicators
        
        Returns:
            True if bullish crossover detected, False otherwise
        """
        if data is None or len(data) < 2:
            return False
        
        try:
            if 'MACD' not in data.columns or 'MACD_signal' not in data.columns:
                return False
            
            current = data.iloc[-1]
            previous = data.iloc[-2]
            
            # Bullish crossover: MACD crosses above signal
            if (previous['MACD'] <= previous['MACD_signal'] and 
                current['MACD'] > current['MACD_signal']):
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking MACD crossover: {e}")
            return False
    
    def get_indicator_value(self, data: pd.DataFrame, indicator_name: str) -> Optional[float]:
        """
        Get the latest value of a specific indicator.
        
        Args:
            data: DataFrame with indicators
            indicator_name: Name of the indicator (e.g., 'RSI', 'SMA_50')
        
        Returns:
            Latest indicator value or None if not available
        """
        if data is None or data.empty:
            return None
        
        try:
            # Map common indicator names to actual column names
            indicator_map = {
                'rsi': 'RSI',
                'sma_20': 'SMA_20',
                'sma_50': 'SMA_50',
                'sma_100': 'SMA_100',
                'sma_200': 'SMA_200',
                'ema_12': 'EMA_12',
                'ema_26': 'EMA_26',
                'ema_50': 'EMA_50',
                'ema_200': 'EMA_200',
                'macd': 'MACD',
                'macd_signal': 'MACD_signal',
                'macd_histogram': 'MACD_histogram',
                'obv': 'OBV',
                'atr': 'ATR',
                'adx': 'ADX'
            }
            
            # Normalize indicator name
            normalized_name = indicator_name.lower()
            column_name = indicator_map.get(normalized_name, indicator_name)
            
            if column_name in data.columns:
                value = data[column_name].iloc[-1]
                return float(value) if pd.notna(value) else None
            
            logger.warning(f"Indicator '{indicator_name}' not found in data")
            return None
            
        except Exception as e:
            logger.error(f"Error getting indicator value: {e}")
            return None

