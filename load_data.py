#!/usr/bin/env python3
"""
Bulk data loading script for Stock Analyzer.
Loads historical stock data into TimescaleDB for faster subsequent queries.
"""
import sys
import argparse
from pathlib import Path
from typing import List, Optional

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.services.data_service import DataService
from app.utils.storage import StorageManager
from app.utils.logger import setup_logger
from app.database.connection import check_connection

# Setup logger
logger = setup_logger("load_data", level="INFO")


def load_exchange_data(
    exchange: str,
    top_n: Optional[int] = None,
    period: str = "20y",
    force_refresh: bool = False,
    include_indicators: bool = True,
    include_fundamentals: bool = True
):
    """
    Load data for all stocks in an exchange.
    
    Args:
        exchange: Exchange code (NSE, BSE, NASDAQ, NYSE)
        top_n: Limit to top N stocks (None = all)
        period: Time period for historical data (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, 20y, ytd, max)
        force_refresh: Force refresh even if data exists
        include_indicators: Calculate and store technical indicators
        include_fundamentals: Fetch and store fundamental data
    """
    logger.info("=" * 60)
    logger.info(f"Bulk Data Loader - {exchange}")
    logger.info("=" * 60)
    
    # Check database connection
    logger.info("Checking database connection...")
    if not check_connection():
        logger.error("❌ Database connection failed!")
        logger.error("Make sure TimescaleDB is running:")
        logger.error("  docker-compose up -d")
        sys.exit(1)
    
    logger.info("✓ Database connection successful")
    
    # Initialize services
    data_service = DataService()
    
    # Get tickers for the exchange
    logger.info(f"\nGetting tickers for {exchange}...")
    tickers = data_service.get_exchange_tickers(exchange, top_n)
    logger.info(f"Found {len(tickers)} tickers")
    
    # Fetch and store data
    logger.info(f"\nFetching {period} historical data...")
    logger.info("This will automatically cache data in TimescaleDB")
    if include_indicators:
        logger.info("✓ Technical indicators will be calculated and stored")
    if include_fundamentals:
        logger.info("✓ Fundamental data will be fetched and stored")
    logger.info("-" * 60)
    
    results = data_service.fetch_multiple_stocks(
        tickers=tickers,
        period=period,
        interval="1d",
        force_refresh=force_refresh,
        show_progress=True,
        include_indicators=include_indicators,
        include_fundamentals=include_fundamentals
    )
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("Load Complete!")
    logger.info("=" * 60)
    logger.info(f"Successfully loaded: {len(results)}/{len(tickers)} stocks")
    logger.info(f"Failed: {len(tickers) - len(results)} stocks")
    
    # Show cache info
    storage = StorageManager()
    cache_info = storage.get_cache_info()
    logger.info(f"\nDatabase Stats:")
    logger.info(f"  Total tickers in DB: {cache_info['total_tickers']}")
    logger.info(f"  Total records: {cache_info['total_records']:,}")
    if cache_info.get('database_size'):
        logger.info(f"  Prices table size: {cache_info['database_size']['prices_table']}")
        logger.info(f"  Metadata table size: {cache_info['database_size']['metadata_table']}")


def load_specific_tickers(
    tickers: List[str],
    period: str = "20y",
    force_refresh: bool = False,
    include_indicators: bool = True,
    include_fundamentals: bool = True
):
    """
    Load data for specific tickers.
    
    Args:
        tickers: List of ticker symbols
        period: Time period for historical data
        force_refresh: Force refresh even if data exists
        include_indicators: Calculate and store technical indicators
        include_fundamentals: Fetch and store fundamental data
    """
    logger.info("=" * 60)
    logger.info("Bulk Data Loader - Specific Tickers")
    logger.info("=" * 60)
    
    # Check database connection
    logger.info("Checking database connection...")
    if not check_connection():
        logger.error("❌ Database connection failed!")
        logger.error("Make sure TimescaleDB is running:")
        logger.error("  docker-compose up -d")
        sys.exit(1)
    
    logger.info("✓ Database connection successful")
    
    # Initialize services
    data_service = DataService()
    
    logger.info(f"\nLoading data for {len(tickers)} tickers...")
    logger.info(f"Tickers: {', '.join(tickers)}")
    if include_indicators:
        logger.info("✓ Technical indicators will be calculated and stored")
    if include_fundamentals:
        logger.info("✓ Fundamental data will be fetched and stored")
    logger.info("-" * 60)
    
    results = data_service.fetch_multiple_stocks(
        tickers=tickers,
        period=period,
        interval="1d",
        force_refresh=force_refresh,
        show_progress=True,
        include_indicators=include_indicators,
        include_fundamentals=include_fundamentals
    )
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("Load Complete!")
    logger.info("=" * 60)
    logger.info(f"Successfully loaded: {len(results)}/{len(tickers)} stocks")
    
    if len(results) < len(tickers):
        failed = set(tickers) - set(results.keys())
        logger.warning(f"Failed tickers: {', '.join(failed)}")


def show_cache_info():
    """Show information about cached data."""
    logger.info("=" * 60)
    logger.info("TimescaleDB Cache Information")
    logger.info("=" * 60)
    
    storage = StorageManager()
    cache_info = storage.get_cache_info()
    
    logger.info(f"\nStorage Type: {cache_info['storage_type']}")
    logger.info(f"Total Tickers: {cache_info['total_tickers']}")
    logger.info(f"Total Records: {cache_info['total_records']:,}")
    
    if cache_info.get('date_range'):
        date_range = cache_info['date_range']
        if date_range['earliest'] and date_range['latest']:
            logger.info(f"Date Range: {date_range['earliest'][:10]} to {date_range['latest'][:10]}")
    
    if cache_info.get('database_size'):
        logger.info(f"\nDatabase Size:")
        logger.info(f"  Prices Table: {cache_info['database_size']['prices_table']}")
        logger.info(f"  Metadata Table: {cache_info['database_size']['metadata_table']}")
    
    if cache_info.get('tickers'):
        logger.info(f"\nCached Tickers ({len(cache_info['tickers'])}):")
        for ticker in sorted(cache_info['tickers'])[:20]:  # Show first 20
            logger.info(f"  - {ticker}")
        if len(cache_info['tickers']) > 20:
            logger.info(f"  ... and {len(cache_info['tickers']) - 20} more")


def clear_cache(ticker: Optional[str] = None):
    """Clear cached data."""
    logger.info("=" * 60)
    logger.info("Clear Cache")
    logger.info("=" * 60)
    
    storage = StorageManager()
    
    if ticker:
        logger.info(f"\nClearing cache for {ticker}...")
        storage.clear_cache(ticker)
        logger.info(f"✓ Cache cleared for {ticker}")
    else:
        confirm = input("\n⚠️  This will delete ALL cached data. Are you sure? (yes/no): ")
        if confirm.lower() == 'yes':
            logger.info("\nClearing all cached data...")
            storage.clear_cache()
            logger.info("✓ All cache cleared")
        else:
            logger.info("Operation cancelled")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Bulk data loader for Stock Analyzer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Load NSE top 30 stocks (20 years of data with indicators & fundamentals)
  python load_data.py --exchange NSE --top-n 30

  # Load all NASDAQ stocks (max available data)
  python load_data.py --exchange NASDAQ --period max

  # Load specific tickers with all data types
  python load_data.py --tickers AAPL MSFT GOOGL

  # Load specific NSE stocks
  python load_data.py --tickers RELIANCE.NS TCS.NS INFY.NS

  # Load only OHLCV data without indicators/fundamentals
  python load_data.py --exchange NSE --no-indicators --no-fundamentals

  # Load only price data without fundamentals
  python load_data.py --tickers AAPL --no-fundamentals

  # Force refresh existing data
  python load_data.py --exchange NSE --force-refresh

  # Show cache information
  python load_data.py --info

  # Clear cache for specific ticker
  python load_data.py --clear --ticker AAPL

  # Clear all cache
  python load_data.py --clear
        """
    )
    
    parser.add_argument(
        "--exchange",
        type=str,
        choices=["NSE", "BSE", "NASDAQ", "NYSE"],
        help="Exchange to load data for"
    )
    
    parser.add_argument(
        "--top-n",
        type=int,
        help="Limit to top N stocks from exchange"
    )
    
    parser.add_argument(
        "--tickers",
        nargs="+",
        help="Specific ticker symbols to load"
    )
    
    parser.add_argument(
        "--period",
        type=str,
        default="20y",
        choices=["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "20y", "ytd", "max"],
        help="Time period for historical data (default: 20y)"
    )
    
    parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Force refresh data even if cached"
    )
    
    parser.add_argument(
        "--no-indicators",
        action="store_true",
        help="Skip calculating and storing technical indicators"
    )
    
    parser.add_argument(
        "--no-fundamentals",
        action="store_true",
        help="Skip fetching and storing fundamental data"
    )
    
    parser.add_argument(
        "--info",
        action="store_true",
        help="Show cache information"
    )
    
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear cached data"
    )
    
    parser.add_argument(
        "--ticker",
        type=str,
        help="Specific ticker to clear (use with --clear)"
    )
    
    args = parser.parse_args()
    
    # Handle different commands
    if args.info:
        show_cache_info()
    elif args.clear:
        clear_cache(args.ticker)
    elif args.exchange:
        load_exchange_data(
            exchange=args.exchange,
            top_n=args.top_n,
            period=args.period,
            force_refresh=args.force_refresh,
            include_indicators=not args.no_indicators,
            include_fundamentals=not args.no_fundamentals
        )
    elif args.tickers:
        load_specific_tickers(
            tickers=args.tickers,
            period=args.period,
            force_refresh=args.force_refresh,
            include_indicators=not args.no_indicators,
            include_fundamentals=not args.no_fundamentals
        )
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()

