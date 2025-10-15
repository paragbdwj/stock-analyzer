"""
FastAPI route definitions.
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
import pandas as pd

from app.models.schemas import (
    ScanRequest, ScanResult, StockInfo,
    HealthResponse, ExchangeInfo
)
from app.services.scanner_service import ScannerService
from app.services.data_service import DataService
from app.config import config
from app.utils.logger import get_logger
from app import __version__


logger = get_logger(__name__)
router = APIRouter()

# Initialize services
scanner_service = ScannerService()
data_service = DataService()


@router.get("/", response_model=dict)
async def root():
    """
    Root endpoint with API information.
    """
    return {
        "name": "Stock Analyzer API",
        "version": __version__,
        "description": "Daily stock scanner using technical and fundamental analysis",
        "endpoints": {
            "health": "/health",
            "scan": "/scan",
            "analyze": "/analyze/{ticker}",
            "exchanges": "/exchanges",
            "tickers": "/tickers/{exchange}",
            "docs": "/docs"
        }
    }


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.
    """
    return HealthResponse(
        status="healthy",
        version=__version__
    )


@router.post("/scan", response_model=ScanResult)
async def scan_stocks(request: ScanRequest):
    """
    Scan stocks based on technical and fundamental filters.
    
    Args:
        request: ScanRequest with filtering criteria
    
    Returns:
        ScanResult with matched stocks
    
    Example request:
    ```json
    {
        "exchange": "NSE",
        "technical_filters": [
            {"field": "rsi", "operator": "<", "value": 30}
        ],
        "fundamental_filters": [
            {"field": "trailing_pe", "operator": "<", "value": 20}
        ],
        "filter_logic": "AND"
    }
    ```
    """
    try:
        logger.info(f"Received scan request for exchange: {request.exchange}")
        result = scanner_service.scan_stocks(request)
        return result
    except Exception as e:
        logger.error(f"Error processing scan request: {e}")
        raise HTTPException(status_code=500, detail=f"Scan failed: {str(e)}")


@router.get("/analyze/{ticker}", response_model=StockInfo)
async def analyze_stock(
    ticker: str,
    force_refresh: bool = Query(False, description="Force refresh data from source")
):
    """
    Get detailed analysis for a specific stock.
    
    Args:
        ticker: Stock ticker symbol (e.g., RELIANCE.NS, AAPL)
        force_refresh: Force refresh data even if cached
    
    Returns:
        StockInfo with complete technical and fundamental analysis
    
    Example:
        GET /analyze/RELIANCE.NS
        GET /analyze/AAPL?force_refresh=true
    """
    try:
        logger.info(f"Analyzing stock: {ticker} (force_refresh={force_refresh})")
        stock_info = scanner_service.get_stock_analysis(ticker, force_refresh=force_refresh)
        
        if stock_info is None:
            raise HTTPException(
                status_code=404,
                detail=f"Unable to fetch data for ticker: {ticker}"
            )
        
        return stock_info
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing {ticker}: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.get("/exchanges", response_model=List[ExchangeInfo])
async def get_exchanges():
    """
    Get list of supported exchanges.
    
    Returns:
        List of ExchangeInfo objects
    """
    exchanges = []
    
    for code, info in config.exchanges.items():
        exchanges.append(ExchangeInfo(
            code=code,
            suffix=info.get("suffix", ""),
            description=info.get("description", ""),
            available=True
        ))
    
    return exchanges


@router.get("/tickers/{exchange}", response_model=List[str])
async def get_tickers(
    exchange: str,
    top_n: Optional[int] = Query(None, description="Limit to top N stocks", ge=1)
):
    """
    Get list of tickers for a specific exchange.
    
    Args:
        exchange: Exchange code (NSE, BSE, NASDAQ, NYSE)
        top_n: Limit to top N stocks (optional)
    
    Returns:
        List of ticker symbols
    
    Example:
        GET /tickers/NSE
        GET /tickers/NASDAQ?top_n=10
    """
    try:
        exchange_upper = exchange.upper()
        
        if exchange_upper not in config.exchanges:
            raise HTTPException(
                status_code=404,
                detail=f"Exchange '{exchange}' not found. Available: {list(config.exchanges.keys())}"
            )
        
        tickers = data_service.get_exchange_tickers(exchange_upper, top_n=top_n)
        
        return tickers
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting tickers for {exchange}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get tickers: {str(e)}")


@router.get("/cache/info", response_model=dict)
async def get_cache_info():
    """
    Get information about cached data.
    
    Returns:
        Dictionary with cache statistics
    """
    try:
        cache_info = data_service.storage.get_cache_info()
        return cache_info
    except Exception as e:
        logger.error(f"Error getting cache info: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get cache info: {str(e)}")


@router.delete("/cache/clear")
async def clear_cache(
    ticker: Optional[str] = Query(None, description="Specific ticker to clear (optional)")
):
    """
    Clear cached data.
    
    Args:
        ticker: Specific ticker to clear (if None, clears all)
    
    Returns:
        Confirmation message
    
    Example:
        DELETE /cache/clear
        DELETE /cache/clear?ticker=RELIANCE.NS
    """
    try:
        data_service.storage.clear_cache(ticker)
        
        if ticker:
            message = f"Cache cleared for {ticker}"
        else:
            message = "All cache cleared"
        
        logger.info(message)
        return {"message": message}
        
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to clear cache: {str(e)}")


@router.get("/price/{ticker}", response_model=dict)
async def get_current_price(ticker: str):
    """
    Get current price for a ticker.
    
    Args:
        ticker: Stock ticker symbol
    
    Returns:
        Dictionary with ticker and current price
    
    Example:
        GET /price/RELIANCE.NS
    """
    try:
        price = data_service.get_latest_price(ticker)
        
        if price is None:
            raise HTTPException(
                status_code=404,
                detail=f"Unable to fetch price for ticker: {ticker}"
            )
        
        return {
            "ticker": ticker,
            "price": price
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting price for {ticker}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get price: {str(e)}")


@router.get("/history/{ticker}", response_model=dict)
async def get_historical_data(
    ticker: str,
    period: str = Query("1y", description="Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)"),
    interval: str = Query("1d", description="Data interval (1d, 1wk, 1mo)"),
    use_cache: bool = Query(True, description="Use cached data if available")
):
    """
    Get historical OHLC data for a ticker.
    
    Args:
        ticker: Stock ticker symbol
        period: Time period for historical data
        interval: Data interval
        use_cache: Whether to use cached data
    
    Returns:
        Dictionary with historical OHLC data
    
    Example:
        GET /history/RELIANCE.NS?period=1y&interval=1d
    """
    try:
        logger.info(f"Fetching historical data for {ticker} (period={period}, interval={interval}, use_cache={use_cache})")
        
        # Fetch stock data (use_cache opposite of force_refresh)
        df = data_service.fetch_stock_data(
            ticker=ticker,
            period=period,
            interval=interval,
            force_refresh=not use_cache
        )
        
        if df is None or df.empty:
            raise HTTPException(
                status_code=404,
                detail=f"No historical data found for ticker: {ticker}"
            )
        
        # Convert DataFrame to list of records
        # Reset index to include Date as a column
        df_reset = df.reset_index()
        
        # Convert to records format
        records = []
        for _, row in df_reset.iterrows():
            record = {
                "date": row['Date'].isoformat() if hasattr(row['Date'], 'isoformat') else str(row['Date']),
                "open": float(row['Open']),
                "high": float(row['High']),
                "low": float(row['Low']),
                "close": float(row['Close']),
                "volume": int(row['Volume'])
            }
            if 'Adj Close' in row and row['Adj Close'] is not None:
                record['adj_close'] = float(row['Adj Close'])
            records.append(record)
        
        return {
            "ticker": ticker,
            "period": period,
            "interval": interval,
            "data": records,
            "total_records": len(records)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting historical data for {ticker}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get historical data: {str(e)}")


@router.get("/fundamentals/{ticker}", response_model=dict)
async def get_fundamentals(ticker: str):
    """
    Get latest fundamental data for a ticker.
    
    Args:
        ticker: Stock ticker symbol
    
    Returns:
        Dictionary with fundamental metrics
    
    Example:
        GET /fundamentals/AAPL
    """
    try:
        logger.info(f"Fetching fundamental data for {ticker}")
        
        fundamentals = data_service.storage.load_fundamental_data(ticker)
        
        if fundamentals is None:
            raise HTTPException(
                status_code=404,
                detail=f"No fundamental data found for ticker: {ticker}"
            )
        
        return {
            "ticker": ticker,
            "data": fundamentals
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting fundamentals for {ticker}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get fundamentals: {str(e)}")


@router.get("/fundamentals/{ticker}/history", response_model=dict)
async def get_fundamentals_history(
    ticker: str,
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)")
):
    """
    Get historical fundamental data for a ticker.
    
    Args:
        ticker: Stock ticker symbol
        start_date: Optional start date for filtering
        end_date: Optional end date for filtering
    
    Returns:
        Dictionary with historical fundamental snapshots
    
    Example:
        GET /fundamentals/AAPL/history
        GET /fundamentals/AAPL/history?start_date=2020-01-01&end_date=2024-01-01
    """
    try:
        logger.info(f"Fetching fundamental history for {ticker}")
        
        # Parse dates if provided
        from datetime import datetime as dt
        start_dt = dt.fromisoformat(start_date) if start_date else None
        end_dt = dt.fromisoformat(end_date) if end_date else None
        
        history = data_service.storage.load_fundamental_data_history(ticker, start_dt, end_dt)
        
        if not history:
            raise HTTPException(
                status_code=404,
                detail=f"No historical fundamental data found for ticker: {ticker}"
            )
        
        return {
            "ticker": ticker,
            "snapshots": history,
            "total_snapshots": len(history)
        }
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")
    except Exception as e:
        logger.error(f"Error getting fundamental history for {ticker}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get fundamental history: {str(e)}")


@router.get("/indicators/{ticker}", response_model=dict)
async def get_technical_indicators(
    ticker: str,
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)")
):
    """
    Get technical indicators for a ticker.
    
    Args:
        ticker: Stock ticker symbol
        start_date: Optional start date for filtering
        end_date: Optional end date for filtering
    
    Returns:
        Dictionary with technical indicator time series
    
    Example:
        GET /indicators/AAPL
        GET /indicators/AAPL?start_date=2020-01-01&end_date=2024-01-01
    """
    try:
        logger.info(f"Fetching technical indicators for {ticker}")
        
        indicators_df = data_service.storage.load_technical_indicators(ticker)
        
        if indicators_df is None or indicators_df.empty:
            raise HTTPException(
                status_code=404,
                detail=f"No technical indicator data found for ticker: {ticker}"
            )
        
        # Filter by date range if provided
        if start_date:
            indicators_df = indicators_df[indicators_df.index >= start_date]
        if end_date:
            indicators_df = indicators_df[indicators_df.index <= end_date]
        
        # Convert to records format
        df_reset = indicators_df.reset_index()
        records = []
        for _, row in df_reset.iterrows():
            record = {"date": row['Date'].isoformat() if hasattr(row['Date'], 'isoformat') else str(row['Date'])}
            # Add all indicator values
            for col in indicators_df.columns:
                if col != 'ticker':
                    val = row[col]
                    record[col] = float(val) if not pd.isna(val) else None
            records.append(record)
        
        # Also return latest values for quick access
        latest = indicators_df.iloc[-1].to_dict()
        latest_clean = {k: float(v) if not pd.isna(v) else None for k, v in latest.items() if k != 'ticker'}
        
        return {
            "ticker": ticker,
            "latest": latest_clean,
            "time_series": records,
            "total_records": len(records)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting indicators for {ticker}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get indicators: {str(e)}")

