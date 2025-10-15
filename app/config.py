"""
Configuration management for the Stock Analyzer application.
"""
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Settings
    fmp_api_key: Optional[str] = None
    environment: str = "development"
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class Config:
    """Main configuration class that loads settings from config.json."""
    
    def __init__(self, config_path: str = "config.json"):
        self.config_path = Path(config_path)
        self._config: Dict[str, Any] = {}
        self.settings = Settings()
        self.load_config()
    
    def load_config(self) -> None:
        """Load configuration from JSON file."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        
        with open(self.config_path, 'r') as f:
            self._config = json.load(f)
    
    @property
    def exchanges(self) -> Dict[str, Dict[str, str]]:
        """Get exchange configurations."""
        return self._config.get("exchanges", {})
    
    @property
    def default_exchange(self) -> str:
        """Get default exchange."""
        return self._config.get("default_exchange", "NSE")
    
    @property
    def data_storage(self) -> Dict[str, Any]:
        """Get data storage configuration."""
        return self._config.get("data_storage", {})
    
    @property
    def technical_indicators(self) -> Dict[str, Any]:
        """Get technical indicator configuration."""
        return self._config.get("technical_indicators", {})
    
    @property
    def fundamental_metrics(self) -> List[str]:
        """Get fundamental metrics to fetch."""
        return self._config.get("fundamental_metrics", [])
    
    @property
    def data_fetch(self) -> Dict[str, Any]:
        """Get data fetch configuration."""
        return self._config.get("data_fetch", {})
    
    @property
    def api(self) -> Dict[str, Any]:
        """Get API configuration."""
        return self._config.get("api", {})
    
    def get_exchange_suffix(self, exchange: str) -> str:
        """Get ticker suffix for a given exchange."""
        return self.exchanges.get(exchange, {}).get("suffix", "")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key."""
        return self._config.get(key, default)


# Global configuration instance
config = Config()

