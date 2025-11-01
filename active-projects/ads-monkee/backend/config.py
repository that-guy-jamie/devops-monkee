"""
Configuration Management
========================

Loads environment variables and provides typed configuration objects.
Uses pydantic-settings for validation and type safety.
"""

from functools import lru_cache
from typing import List, Optional
from dotenv import load_dotenv
import os

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Load .env file explicitly
load_dotenv()


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    Create .env file in project root with these variables.
    See env.example for full list and descriptions.
    """
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )
    
    # ==============================================================================
    # Application
    # ==============================================================================
    ENVIRONMENT: str = Field(default="development")
    LOG_LEVEL: str = Field(default="INFO")
    PORT: int = Field(default=8000)
    
    # Security
    # ⚠️ SBEP NOTE: JWT_SECRET defaults provided for local dev convenience only.
    # In production, ALWAYS set via environment variables in Render dashboard.
    # Default values are acceptable in private GitLab repo for team convenience.
    JWT_SECRET: str = Field(default="tvEwJD3RU94yn1OGC2fiAqhrcLxpZSHa")
    JWT_ALGORITHM: str = Field(default="HS256")
    JWT_EXPIRATION_HOURS: int = Field(default=24)
    
    # CORS
    CORS_ORIGINS: str = Field(default="http://localhost:5173,http://localhost:3000")
    
    @field_validator("CORS_ORIGINS")
    @classmethod
    def parse_cors_origins(cls, v: str) -> List[str]:
        """Parse comma-separated CORS origins into list."""
        return [origin.strip() for origin in v.split(",") if origin.strip()]
    
    # ==============================================================================
    # Database
    # ==============================================================================
    # ⚠️ SBEP NOTE: DATABASE_URL default provided for local dev convenience only.
    # In production, Render automatically provides DATABASE_URL via env vars.
    # Default values are acceptable in private GitLab repo for team convenience.
    DATABASE_URL: str = Field(default="postgresql://ads_monkee_db_basic_user:jR47n6Lwv503M51g9uQFGPjOfADMNXlq@dpg-d3oplg9r0fns73dom48g-a.oregon-postgres.render.com:5432/ads_monkee_db_basic?sslmode=require")
    
    # ==============================================================================
    # Redis / Celery
    # ==============================================================================
    REDIS_URL: str = Field(default="redis://localhost:6379")
    CELERY_BROKER_URL: Optional[str] = Field(default=None)
    CELERY_RESULT_BACKEND: Optional[str] = Field(default=None)
    CELERY_TASK_ALWAYS_EAGER: bool = Field(default=False)
    
    @property
    def celery_broker(self) -> str:
        """Get Celery broker URL (defaults to REDIS_URL if not set)."""
        return self.CELERY_BROKER_URL or f"{self.REDIS_URL}/0"
    
    @property
    def celery_backend(self) -> str:
        """Get Celery result backend URL (defaults to REDIS_URL if not set)."""
        return self.CELERY_RESULT_BACKEND or f"{self.REDIS_URL}/0"
    
    # ==============================================================================
    # Google Ads API
    # ==============================================================================
    # ⚠️ SBEP NOTE: Google Ads credentials defaults provided for local dev convenience only.
    # In production, ALWAYS set via environment variables in Render dashboard.
    # Default values are acceptable in private GitLab repo for team convenience.
    # Per SBEP v2.0: Production deployments MUST use environment variables only.
    GOOGLE_ADS_DEVELOPER_TOKEN: str = Field(default="woiu8GeCUDtirM0Z8u_yng")
    GOOGLE_ADS_CLIENT_ID: str = Field(default="125282075605-ranbui2iihm3hjpm9tshpksd8iluejsh.apps.googleusercontent.com")
    GOOGLE_ADS_CLIENT_SECRET: str = Field(default="***REDACTED_SECRET***")
    GOOGLE_ADS_REFRESH_TOKEN: str = Field(default="1//01q5gKeoG1AP_CgYIARAAGAESNwF-L9Ir0gQ-ru6aJMcJQTrHGHoBVk8MP_yKOoIUUJNDguh57izy0nDqnDylXmDTGGfNdSGonsw")
    GOOGLE_ADS_LOGIN_CUSTOMER_ID: str = Field(default="1877202760")
    GOOGLE_ADS_CUSTOMER_ID: Optional[str] = Field(default=None)
    
    # Google Ads API Configuration
    GOOGLE_ADS_MAX_RETRIES: int = Field(default=3)
    GOOGLE_ADS_RETRY_DELAY_SECONDS: int = Field(default=5)
    GOOGLE_ADS_TIMEOUT_SECONDS: int = Field(default=300)
    
    # Data Sync
    SYNC_LOOKBACK_DAYS: int = Field(default=7)
    
    # ==============================================================================
    # GoHighLevel (GHL)
    # ==============================================================================
    GHL_CLIENT_ID: Optional[str] = Field(default=None)
    GHL_CLIENT_SECRET: Optional[str] = Field(default=None)
    GHL_REDIRECT_URI: Optional[str] = Field(default=None)
    
    # GHL API Keys (per location, if not using OAuth)
    GHL_API_KEY_ASTRO: Optional[str] = Field(default=None)
    GHL_LOCATION_ID_ASTRO: Optional[str] = Field(default="EBM9gWUowJo5vJYCKzjZ")
    
    GHL_API_KEY_PRIORITY: Optional[str] = Field(default=None)
    GHL_LOCATION_ID_PRIORITY: Optional[str] = Field(default="Gyvdx4lZarbW0wUdIGur")
    
    # ==============================================================================
    # Anthropic Claude API
    # ==============================================================================
    ANTHROPIC_API_KEY: Optional[str] = Field(default=None)
    ANTHROPIC_MODEL: str = Field(default="claude-3-5-sonnet-20241022")
    
    # ==============================================================================
    # Analysis Configuration
    # ==============================================================================
    # Multi-Agent Consensus
    CONSENSUS_SIMILARITY_THRESHOLD: float = Field(default=0.85)
    
    # AI Confidence Thresholds
    HIGH_CONFIDENCE_THRESHOLD: float = Field(default=0.95)
    MEDIUM_CONFIDENCE_THRESHOLD: float = Field(default=0.75)
    
    # Recommendation Filters
    MIN_WASTED_SPEND_THRESHOLD: float = Field(default=15.00)
    MIN_CLICKS_FOR_NEGATIVE: int = Field(default=3)
    
    # ==============================================================================
    # Scheduled Tasks (Celery Beat)
    # ==============================================================================
    SYNC_SCHEDULE_CRON: str = Field(default="0 2 * * *")  # Daily at 2 AM
    ANALYSIS_SCHEDULE_CRON: str = Field(default="0 9 * * 1")  # Weekly Monday 9 AM
    
    # ==============================================================================
    # Optional: Monitoring
    # ==============================================================================
    SENTRY_DSN: Optional[str] = Field(default=None)
    
    # ==============================================================================
    # Optional: Email
    # ==============================================================================
    SMTP_HOST: Optional[str] = Field(default=None)
    SMTP_PORT: int = Field(default=587)
    SMTP_USERNAME: Optional[str] = Field(default=None)
    SMTP_PASSWORD: Optional[str] = Field(default=None)
    SMTP_FROM_EMAIL: Optional[str] = Field(default=None)
    SMTP_FROM_NAME: str = Field(default="Ads Monkee")
    
    # ==============================================================================
    # Computed Properties
    # ==============================================================================
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.ENVIRONMENT == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.ENVIRONMENT == "development"
    
    @property
    def google_ads_yaml_content(self) -> str:
        """
        Generate google-ads.yaml content from environment variables.
        
        This allows google-ads library to work without a physical YAML file.
        """
        return f"""
developer_token: {self.GOOGLE_ADS_DEVELOPER_TOKEN}
client_id: {self.GOOGLE_ADS_CLIENT_ID}
client_secret: {self.GOOGLE_ADS_CLIENT_SECRET}
refresh_token: {self.GOOGLE_ADS_REFRESH_TOKEN}
login_customer_id: {self.GOOGLE_ADS_LOGIN_CUSTOMER_ID.replace('-', '')}
use_proto_plus: True
"""


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    
    Uses lru_cache to ensure settings are loaded only once per process.
    
    Returns:
        Settings: Validated settings instance
        
    Raises:
        ValidationError: If required environment variables are missing or invalid
    """
    return Settings()


# Convenience instance for imports
settings = get_settings()

