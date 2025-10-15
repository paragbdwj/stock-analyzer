"""
Pydantic schemas for request/response models.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, validator


class StockData(BaseModel):
    """Stock OHLCV data model."""
    ticker: str
    date: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int
    adj_close: Optional[float] = None


class TechnicalIndicators(BaseModel):
    """Technical indicators model."""
    ticker: str
    date: datetime
    
    # Moving Averages
    sma_20: Optional[float] = None
    sma_50: Optional[float] = None
    sma_100: Optional[float] = None
    sma_200: Optional[float] = None
    
    ema_12: Optional[float] = None
    ema_26: Optional[float] = None
    ema_50: Optional[float] = None
    ema_200: Optional[float] = None
    
    # Momentum Indicators
    rsi: Optional[float] = None
    
    # Trend Indicators
    macd: Optional[float] = None
    macd_signal: Optional[float] = None
    macd_histogram: Optional[float] = None
    
    # Volume Indicators
    obv: Optional[float] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "ticker": "RELIANCE.NS",
                "date": "2024-01-15",
                "sma_50": 2450.5,
                "sma_200": 2380.0,
                "rsi": 65.5,
                "macd": 12.5,
                "macd_signal": 10.2,
                "macd_histogram": 2.3
            }
        }


class FundamentalData(BaseModel):
    """Fundamental data model."""
    ticker: str
    
    # Valuation Ratios
    trailing_pe: Optional[float] = Field(None, alias="trailingPE")
    forward_pe: Optional[float] = Field(None, alias="forwardPE")
    price_to_book: Optional[float] = Field(None, alias="priceToBook")
    
    # Financial Health
    debt_to_equity: Optional[float] = Field(None, alias="debtToEquity")
    current_ratio: Optional[float] = Field(None, alias="currentRatio")
    
    # General Information
    market_cap: Optional[float] = Field(None, alias="marketCap")
    sector: Optional[str] = None
    industry: Optional[str] = None
    
    # Additional metrics
    beta: Optional[float] = None
    dividend_yield: Optional[float] = Field(None, alias="dividendYield")
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "ticker": "RELIANCE.NS",
                "trailing_pe": 25.5,
                "price_to_book": 3.2,
                "debt_to_equity": 0.45,
                "market_cap": 1500000000000,
                "sector": "Energy",
                "industry": "Oil & Gas Refining & Marketing"
            }
        }


class FilterRule(BaseModel):
    """Filter rule for stock scanning."""
    field: str = Field(..., description="Field to filter on (e.g., 'rsi', 'trailing_pe')")
    operator: str = Field(..., description="Comparison operator: <, >, <=, >=, ==, !=")
    value: float = Field(..., description="Value to compare against")
    
    @validator('operator')
    def validate_operator(cls, v):
        allowed = ['<', '>', '<=', '>=', '==', '!=']
        if v not in allowed:
            raise ValueError(f"Operator must be one of: {allowed}")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "field": "rsi",
                "operator": "<",
                "value": 30
            }
        }


class ScanRequest(BaseModel):
    """Request model for stock scanning."""
    exchange: str = Field("NSE", description="Exchange to scan (NSE, BSE, NASDAQ, NYSE)")
    tickers: Optional[List[str]] = Field(None, description="Specific tickers to scan (optional)")
    
    # Filter rules
    technical_filters: Optional[List[FilterRule]] = Field(None, description="Technical indicator filters")
    fundamental_filters: Optional[List[FilterRule]] = Field(None, description="Fundamental data filters")
    
    # Combine filters with AND or OR
    filter_logic: str = Field("AND", description="How to combine filters: AND or OR")
    
    # Data fetch options
    force_refresh: bool = Field(False, description="Force refresh data from source")
    
    @validator('filter_logic')
    def validate_logic(cls, v):
        if v.upper() not in ['AND', 'OR']:
            raise ValueError("filter_logic must be either 'AND' or 'OR'")
        return v.upper()
    
    class Config:
        json_schema_extra = {
            "example": {
                "exchange": "NSE",
                "technical_filters": [
                    {"field": "rsi", "operator": "<", "value": 30}
                ],
                "fundamental_filters": [
                    {"field": "trailing_pe", "operator": "<", "value": 20}
                ],
                "filter_logic": "AND"
            }
        }


class StockInfo(BaseModel):
    """Combined stock information."""
    ticker: str
    technical: Optional[TechnicalIndicators] = None
    fundamental: Optional[FundamentalData] = None
    current_price: Optional[float] = None
    matched_filters: List[str] = Field(default_factory=list)


class ScanResult(BaseModel):
    """Result model for stock scanning."""
    timestamp: datetime = Field(default_factory=datetime.now)
    exchange: str
    total_scanned: int
    total_matched: int
    stocks: List[StockInfo]
    scan_duration_seconds: float
    
    class Config:
        json_schema_extra = {
            "example": {
                "timestamp": "2024-01-15T10:30:00",
                "exchange": "NSE",
                "total_scanned": 100,
                "total_matched": 5,
                "stocks": [],
                "scan_duration_seconds": 45.5
            }
        }


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    timestamp: datetime = Field(default_factory=datetime.now)


class ExchangeInfo(BaseModel):
    """Exchange information model."""
    code: str
    suffix: str
    description: str
    available: bool = True

