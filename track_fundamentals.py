#!/usr/bin/env python3
"""
Track fundamental data over time by saving snapshots.
Run this script daily/weekly to build historical fundamental data.
"""
import sys
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Optional

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.utils.storage import StorageManager
from app.utils.logger import setup_logger
from app.database.connection import check_connection
import yfinance as yf

# Setup logger
logger = setup_logger("track_fundamentals", level="INFO")


def track_fundamental_snapshot(
    ticker: str,
    timestamp: Optional[datetime] = None
):
    """
    Capture a fundamental snapshot for a ticker at a specific time.
    
    Args:
        ticker: Stock ticker symbol
        timestamp: Snapshot timestamp (default: now)
    """
    logger.info(f"Capturing fundamental snapshot for {ticker}")
    
    storage = StorageManager()
    snapshot_time = timestamp or datetime.utcnow()
    
    try:
        # Fetch current fundamental data
        stock = yf.Ticker(ticker)
        info = stock.info
        
        if not info or len(info) <= 1:
            logger.warning(f"No fundamental data available for {ticker}")
            return False
        
        # Save snapshot with specific timestamp
        success = storage.save_fundamental_data(ticker, info, snapshot_time)
        
        if success:
            logger.info(f"✓ Saved fundamental snapshot for {ticker} at {snapshot_time}")
            # Log key metrics
            if 'trailingPE' in info:
                logger.info(f"  P/E: {info['trailingPE']:.2f}")
            if 'marketCap' in info:
                logger.info(f"  Market Cap: ${info['marketCap']:,.0f}")
            if 'profitMargins' in info:
                logger.info(f"  Profit Margin: {info['profitMargins']:.2%}")
        else:
            logger.error(f"❌ Failed to save snapshot for {ticker}")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"Error capturing snapshot for {ticker}: {e}")
        return False


def track_multiple_tickers(
    tickers: List[str],
    show_progress: bool = True
):
    """
    Track fundamentals for multiple tickers.
    
    Args:
        tickers: List of ticker symbols
        show_progress: Show progress during tracking
    """
    logger.info(f"Tracking fundamentals for {len(tickers)} tickers")
    logger.info("-" * 60)
    
    snapshot_time = datetime.utcnow()
    success_count = 0
    
    for i, ticker in enumerate(tickers, 1):
        if show_progress:
            logger.info(f"[{i}/{len(tickers)}] Processing {ticker}...")
        
        if track_fundamental_snapshot(ticker, snapshot_time):
            success_count += 1
    
    logger.info("\n" + "=" * 60)
    logger.info("Tracking Complete!")
    logger.info("=" * 60)
    logger.info(f"Successfully tracked: {success_count}/{len(tickers)} tickers")
    logger.info(f"Snapshot timestamp: {snapshot_time}")


def view_fundamental_history(ticker: str):
    """
    View historical fundamental snapshots for a ticker.
    
    Args:
        ticker: Stock ticker symbol
    """
    logger.info(f"Fundamental history for {ticker}")
    logger.info("=" * 60)
    
    storage = StorageManager()
    history = storage.load_fundamental_data_history(ticker)
    
    if not history:
        logger.info(f"No historical fundamental data found for {ticker}")
        return
    
    logger.info(f"Found {len(history)} snapshots\n")
    
    # Display each snapshot
    for i, snapshot in enumerate(history, 1):
        timestamp = snapshot.get('timestamp', 'Unknown')
        logger.info(f"{i}. Snapshot from {timestamp}")
        logger.info("-" * 40)
        
        # Display key metrics
        if snapshot.get('trailing_pe'):
            logger.info(f"   P/E Ratio: {snapshot['trailing_pe']:.2f}")
        if snapshot.get('market_cap'):
            logger.info(f"   Market Cap: ${snapshot['market_cap']:,.0f}")
        if snapshot.get('profit_margin'):
            logger.info(f"   Profit Margin: {snapshot['profit_margin']:.2%}")
        if snapshot.get('return_on_equity'):
            logger.info(f"   ROE: {snapshot['return_on_equity']:.2%}")
        if snapshot.get('revenue_growth'):
            logger.info(f"   Revenue Growth: {snapshot['revenue_growth']:.2%}")
        
        logger.info("")


def setup_scheduled_tracking(tickers: List[str]):
    """
    Display instructions for setting up scheduled tracking.
    
    Args:
        tickers: List of tickers to track
    """
    ticker_list = " ".join(tickers)
    
    logger.info("=" * 60)
    logger.info("Scheduled Tracking Setup Instructions")
    logger.info("=" * 60)
    
    logger.info("\n📅 To track fundamentals automatically, set up a cron job or scheduled task:\n")
    
    logger.info("1. Daily Tracking (recommended for active trading)")
    logger.info("   Add to crontab (crontab -e):")
    logger.info(f"   0 18 * * * cd {project_root} && source venv/bin/activate && python track_fundamentals.py --tickers {ticker_list}")
    logger.info("   (Runs daily at 6 PM)")
    
    logger.info("\n2. Weekly Tracking (good for long-term investing)")
    logger.info("   Add to crontab:")
    logger.info(f"   0 9 * * 1 cd {project_root} && source venv/bin/activate && python track_fundamentals.py --tickers {ticker_list}")
    logger.info("   (Runs every Monday at 9 AM)")
    
    logger.info("\n3. Monthly Tracking (minimal storage)")
    logger.info("   Add to crontab:")
    logger.info(f"   0 9 1 * * cd {project_root} && source venv/bin/activate && python track_fundamentals.py --tickers {ticker_list}")
    logger.info("   (Runs first day of each month at 9 AM)")
    
    logger.info("\n4. After Market Close (NYSE/NASDAQ)")
    logger.info("   Add to crontab:")
    logger.info(f"   0 17 * * 1-5 cd {project_root} && source venv/bin/activate && python track_fundamentals.py --tickers {ticker_list}")
    logger.info("   (Runs weekdays at 5 PM EST)")
    
    logger.info("\n💡 Tip: Over time, you'll build a rich historical dataset!")
    logger.info("   - Daily tracking = detailed trends")
    logger.info("   - Weekly tracking = good balance")
    logger.info("   - Monthly tracking = minimal storage\n")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Track fundamental data over time",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Track single ticker
  python track_fundamentals.py --ticker AAPL
  
  # Track multiple tickers
  python track_fundamentals.py --tickers AAPL MSFT GOOGL
  
  # View history
  python track_fundamentals.py --ticker AAPL --view-history
  
  # Setup scheduled tracking
  python track_fundamentals.py --tickers AAPL MSFT --setup-schedule
        """
    )
    
    parser.add_argument(
        "--ticker",
        type=str,
        help="Single ticker to track"
    )
    
    parser.add_argument(
        "--tickers",
        nargs="+",
        help="Multiple tickers to track"
    )
    
    parser.add_argument(
        "--view-history",
        action="store_true",
        help="View fundamental history for ticker"
    )
    
    parser.add_argument(
        "--setup-schedule",
        action="store_true",
        help="Show instructions for scheduled tracking"
    )
    
    args = parser.parse_args()
    
    # Check database connection
    if not args.setup_schedule:
        logger.info("Checking database connection...")
        if not check_connection():
            logger.error("❌ Database connection failed!")
            logger.error("Make sure TimescaleDB is running:")
            logger.error("  docker-compose up -d")
            sys.exit(1)
        logger.info("✓ Database connection successful\n")
    
    # Handle commands
    if args.view_history:
        if not args.ticker:
            logger.error("Please specify --ticker for viewing history")
            sys.exit(1)
        view_fundamental_history(args.ticker)
    elif args.setup_schedule:
        tickers = [args.ticker] if args.ticker else args.tickers
        if not tickers:
            logger.error("Please specify tickers for scheduled tracking")
            sys.exit(1)
        setup_scheduled_tracking(tickers)
    elif args.ticker:
        track_fundamental_snapshot(args.ticker)
    elif args.tickers:
        track_multiple_tickers(args.tickers)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()

