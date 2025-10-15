"""
Database connection management for TimescaleDB.
"""
from contextlib import contextmanager
from typing import Generator
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool

from app.config import config
from app.utils.logger import get_logger


logger = get_logger(__name__)

# Global engine instance
_engine = None
_SessionLocal = None


def get_database_url() -> str:
    """
    Construct database URL from configuration.
    
    Returns:
        Database connection URL
    """
    db_config = config.get("database", {})
    
    host = db_config.get("host", "localhost")
    port = db_config.get("port", 5432)
    database = db_config.get("database", "stock_analyzer")
    user = db_config.get("user", "postgres")
    password = db_config.get("password", "postgres")
    
    return f"postgresql://{user}:{password}@{host}:{port}/{database}"


def get_engine():
    """
    Get or create SQLAlchemy engine.
    
    Returns:
        SQLAlchemy Engine instance
    """
    global _engine
    
    if _engine is None:
        db_config = config.get("database", {})
        pool_size = db_config.get("pool_size", 10)
        max_overflow = db_config.get("max_overflow", 20)
        
        database_url = get_database_url()
        
        _engine = create_engine(
            database_url,
            poolclass=QueuePool,
            pool_size=pool_size,
            max_overflow=max_overflow,
            pool_pre_ping=True,
            echo=False
        )
        
        logger.info(f"Database engine created: {db_config.get('host')}:{db_config.get('port')}/{db_config.get('database')}")
    
    return _engine


def get_session_local():
    """
    Get or create SessionLocal class.
    
    Returns:
        SessionLocal class
    """
    global _SessionLocal
    
    if _SessionLocal is None:
        engine = get_engine()
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    return _SessionLocal


@contextmanager
def get_session() -> Generator[Session, None, None]:
    """
    Context manager for database sessions.
    
    Yields:
        SQLAlchemy Session
    
    Example:
        with get_session() as session:
            result = session.query(StockPrice).all()
    """
    SessionLocal = get_session_local()
    session = SessionLocal()
    
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Database session error: {e}")
        raise
    finally:
        session.close()


def init_db() -> None:
    """
    Initialize database schema and TimescaleDB hypertable.
    This should be called once during application startup.
    """
    from app.database.models import Base
    
    engine = get_engine()
    
    try:
        # Create TimescaleDB extension if not exists
        with engine.connect() as conn:
            # Check if TimescaleDB extension exists
            result = conn.execute(text(
                "SELECT EXISTS(SELECT 1 FROM pg_extension WHERE extname='timescaledb')"
            ))
            timescale_exists = result.scalar()
            
            if not timescale_exists:
                logger.info("Creating TimescaleDB extension...")
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS timescaledb"))
                conn.commit()
            
            logger.info("TimescaleDB extension is available")
        
        # Create all tables
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        
        # Convert stock_prices to hypertable if not already
        with engine.connect() as conn:
            # Check if hypertable exists
            result = conn.execute(text(
                """
                SELECT EXISTS(
                    SELECT 1 FROM timescaledb_information.hypertables 
                    WHERE hypertable_name = 'stock_prices'
                )
                """
            ))
            hypertable_exists = result.scalar()
            
            if not hypertable_exists:
                logger.info("Converting stock_prices to hypertable...")
                conn.execute(text(
                    """
                    SELECT create_hypertable(
                        'stock_prices',
                        'timestamp',
                        if_not_exists => TRUE,
                        chunk_time_interval => INTERVAL '7 days'
                    )
                    """
                ))
                conn.commit()
                logger.info("Hypertable created successfully")
            else:
                logger.info("Hypertable already exists")
        
        # Create indexes for better query performance
        with engine.connect() as conn:
            logger.info("Creating indexes...")
            
            # Index on ticker for fast ticker-based queries
            conn.execute(text(
                """
                CREATE INDEX IF NOT EXISTS idx_stock_prices_ticker 
                ON stock_prices (ticker, timestamp DESC)
                """
            ))
            
            # Index on ticker and timestamp for range queries
            conn.execute(text(
                """
                CREATE INDEX IF NOT EXISTS idx_stock_prices_ticker_time 
                ON stock_prices (ticker, timestamp)
                """
            ))
            
            conn.commit()
            logger.info("Indexes created successfully")
        
        # Enable compression for older data (optional but recommended)
        with engine.connect() as conn:
            try:
                logger.info("Enabling compression for old data...")
                conn.execute(text(
                    """
                    ALTER TABLE stock_prices SET (
                        timescaledb.compress,
                        timescaledb.compress_segmentby = 'ticker'
                    )
                    """
                ))
                
                # Add compression policy for data older than 30 days
                conn.execute(text(
                    """
                    SELECT add_compression_policy('stock_prices', INTERVAL '30 days', if_not_exists => TRUE)
                    """
                ))
                
                conn.commit()
                logger.info("Compression enabled successfully")
            except Exception as e:
                logger.warning(f"Could not enable compression (may already be enabled): {e}")
                conn.rollback()
        
        logger.info("Database initialization complete!")
        
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


def check_connection() -> bool:
    """
    Check if database connection is working.
    
    Returns:
        True if connection is successful, False otherwise
    """
    try:
        engine = get_engine()
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Database connection successful")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False


def close_connection() -> None:
    """
    Close database connection and cleanup resources.
    """
    global _engine, _SessionLocal
    
    if _engine is not None:
        _engine.dispose()
        _engine = None
        _SessionLocal = None
        logger.info("Database connection closed")

