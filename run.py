#!/usr/bin/env python3
"""
Entry point script to run the Stock Analyzer API.
"""
import sys
import uvicorn
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.config import config


def main():
    """Run the FastAPI application."""
    api_config = config.api
    
    print("=" * 60)
    print("Stock Analyzer API")
    print("=" * 60)
    print(f"Starting server at http://{api_config.get('host', '0.0.0.0')}:{api_config.get('port', 8000)}")
    print(f"Documentation available at http://localhost:{api_config.get('port', 8000)}/docs")
    print("=" * 60)
    
    uvicorn.run(
        "app.main:app",
        host=api_config.get("host", "0.0.0.0"),
        port=api_config.get("port", 8000),
        reload=api_config.get("reload", True),
        log_level=config.settings.log_level.lower()
    )


if __name__ == "__main__":
    main()

