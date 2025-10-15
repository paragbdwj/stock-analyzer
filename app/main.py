"""
Main FastAPI application for Stock Analyzer.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.api.routes import router
from app.config import config
from app.utils.logger import setup_logger, get_logger
from app import __version__


# Setup logger
logger = setup_logger(
    name="stock_analyzer",
    level=config.settings.log_level,
    log_file=None  # Set to "logs/app.log" if you want file logging
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup
    logger.info("=" * 60)
    logger.info(f"Starting Stock Analyzer API v{__version__}")
    logger.info(f"Environment: {config.settings.environment}")
    logger.info(f"Default Exchange: {config.default_exchange}")
    logger.info("=" * 60)
    
    # Check database connection
    from app.database.connection import check_connection
    logger.info("Checking database connection...")
    if check_connection():
        logger.info("✓ Database connection successful")
    else:
        logger.warning("⚠ Database connection failed - some features may not work")
        logger.warning("Make sure TimescaleDB is running: docker-compose up -d")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Stock Analyzer API")
    from app.database.connection import close_connection
    close_connection()


# Create FastAPI application
app = FastAPI(
    title="Stock Analyzer API",
    description="Daily stock scanner using technical and fundamental analysis",
    version=__version__,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router, tags=["Stock Analyzer"])


if __name__ == "__main__":
    import uvicorn
    
    # Get API configuration
    api_config = config.api
    
    uvicorn.run(
        "app.main:app",
        host=api_config.get("host", "0.0.0.0"),
        port=api_config.get("port", 8000),
        reload=api_config.get("reload", True),
        log_level=config.settings.log_level.lower()
    )

