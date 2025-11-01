"""
Configuration management using pydantic-settings.

Loads settings from environment variables or .env file.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class Settings(BaseSettings):
    """Application settings loaded from environment variables or .env file."""
    
    # Redis configuration
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    
    # ads_sync CLI path configuration
    ads_sync_project_path: str = "../ads_sync"
    ads_sync_cli_command: str = "poetry run python ads_sync_cli.py"
    
    # API configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # CORS configuration (can be "*" or comma-separated origins)
    cors_origins: str = "*"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    def get_redis_url(self) -> str:
        """Get Redis connection URL."""
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"
    
    def get_ads_sync_path(self) -> Path:
        """Get absolute path to ads_sync project."""
        return Path(__file__).parent.parent / self.ads_sync_project_path


# Global settings instance
settings = Settings()

