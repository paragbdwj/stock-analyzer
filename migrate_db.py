#!/usr/bin/env python3
"""
Database migration script to add fundamental and technical indicator tables.
Run this after updating the models to create the new tables.
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.database.connection import get_engine, check_connection
from app.database.models import Base, StockFundamentals, StockTechnicalIndicators
from app.utils.logger import setup_logger
from sqlalchemy import text

logger = setup_logger("migrate_db", level="INFO")


def run_migration():
    """Run database migration to add new tables."""
    logger.info("=" * 60)
    logger.info("Database Migration - Adding Fundamentals & Technical Indicators")
    logger.info("=" * 60)
    
    # Check database connection
    logger.info("\n1. Checking database connection...")
    if not check_connection():
        logger.error("❌ Database connection failed!")
        logger.error("Make sure TimescaleDB is running:")
        logger.error("  docker-compose up -d")
        sys.exit(1)
    
    logger.info("✓ Database connection successful")
    
    # Create tables
    logger.info("\n2. Creating new tables...")
    try:
        engine = get_engine()
        
        # Create only the new tables (won't affect existing tables)
        StockFundamentals.__table__.create(engine, checkfirst=True)
        logger.info("✓ Created stock_fundamentals table")
        
        StockTechnicalIndicators.__table__.create(engine, checkfirst=True)
        logger.info("✓ Created stock_technical_indicators table")
        
        # Convert technical indicators table to hypertable
        logger.info("\n3. Converting technical_indicators to TimescaleDB hypertable...")
        with engine.connect() as conn:
            try:
                result = conn.execute(text(
                    """
                    SELECT create_hypertable(
                        'stock_technical_indicators',
                        'timestamp',
                        if_not_exists => TRUE,
                        migrate_data => TRUE
                    );
                    """
                ))
                conn.commit()
                logger.info("✓ Converted stock_technical_indicators to hypertable")
            except Exception as e:
                if "already a hypertable" in str(e):
                    logger.info("✓ stock_technical_indicators is already a hypertable")
                else:
                    logger.warning(f"Could not convert to hypertable: {e}")
        
        # Create indexes
        logger.info("\n4. Creating indexes...")
        with engine.connect() as conn:
            # Index for fundamentals
            conn.execute(text(
                """
                CREATE INDEX IF NOT EXISTS idx_stock_fundamentals_ticker 
                ON stock_fundamentals(ticker);
                """
            ))
            logger.info("✓ Created index on stock_fundamentals(ticker)")
            
            # Index for technical indicators
            conn.execute(text(
                """
                CREATE INDEX IF NOT EXISTS idx_stock_technical_ticker_time 
                ON stock_technical_indicators(ticker, timestamp DESC);
                """
            ))
            logger.info("✓ Created index on stock_technical_indicators(ticker, timestamp)")
            
            conn.commit()
        
        logger.info("\n" + "=" * 60)
        logger.info("Migration Complete!")
        logger.info("=" * 60)
        logger.info("\nNew tables created:")
        logger.info("  • stock_fundamentals - Stores fundamental metrics")
        logger.info("  • stock_technical_indicators - Stores technical indicators (hypertable)")
        logger.info("\nYou can now load data with:")
        logger.info("  python load_data.py --tickers AAPL")
        
    except Exception as e:
        logger.error(f"\n❌ Migration failed: {e}")
        sys.exit(1)


def show_table_info():
    """Show information about database tables."""
    logger.info("\n" + "=" * 60)
    logger.info("Database Tables Information")
    logger.info("=" * 60)
    
    try:
        engine = get_engine()
        with engine.connect() as conn:
            # Get all tables
            result = conn.execute(text(
                """
                SELECT table_name, 
                       pg_size_pretty(pg_total_relation_size(quote_ident(table_name))) as size
                FROM information_schema.tables
                WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
                ORDER BY table_name;
                """
            ))
            
            tables = result.fetchall()
            logger.info("\nExisting tables:")
            for table in tables:
                logger.info(f"  • {table[0]:<35} {table[1]:>15}")
            
            # Check hypertables
            result = conn.execute(text(
                """
                SELECT hypertable_name
                FROM timescaledb_information.hypertables;
                """
            ))
            
            hypertables = result.fetchall()
            if hypertables:
                logger.info("\nTimescaleDB Hypertables:")
                for ht in hypertables:
                    logger.info(f"  • {ht[0]}")
            
    except Exception as e:
        logger.error(f"Failed to get table info: {e}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Database migration script for Stock Analyzer"
    )
    parser.add_argument(
        "--info",
        action="store_true",
        help="Show database table information"
    )
    
    args = parser.parse_args()
    
    if args.info:
        show_table_info()
    else:
        run_migration()
        show_table_info()

