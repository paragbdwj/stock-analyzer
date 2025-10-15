#!/usr/bin/env python3
"""
Database initialization script.
Run this once to set up TimescaleDB schema and hypertables.
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.database.connection import init_db, check_connection
from app.utils.logger import setup_logger

# Setup logger
logger = setup_logger("init_db", level="INFO")


def main():
    """Initialize the database."""
    logger.info("=" * 60)
    logger.info("Stock Analyzer - Database Initialization")
    logger.info("=" * 60)
    
    # Check connection first
    logger.info("Checking database connection...")
    if not check_connection():
        logger.error("❌ Database connection failed!")
        logger.error("Make sure TimescaleDB is running:")
        logger.error("  docker-compose up -d")
        sys.exit(1)
    
    logger.info("✓ Database connection successful")
    
    # Initialize database
    logger.info("\nInitializing database schema...")
    try:
        init_db()
        logger.info("\n" + "=" * 60)
        logger.info("✓ Database initialization complete!")
        logger.info("=" * 60)
        logger.info("\nYou can now start the application:")
        logger.info("  python run.py")
        
    except Exception as e:
        logger.error(f"\n❌ Database initialization failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

