from pydantic import BaseSettings, AnyUrl
from typing import Optional

class Settings(BaseSettings):
    app_name: str = "Audit Monkee API"
    debug: bool = True
    database_url: str = "sqlite:///./dev.db"
    redis_url: str = "redis://localhost:6379/0"
    ghl_client_id: Optional[str] = None
    ghl_client_secret: Optional[str] = None
    ghl_redirect_uri: Optional[str] = None
    jwt_secret: str = "change-me"
    psi_api_key: Optional[str] = None
    headcore_private_key: Optional[str] = None  # base64url Ed25519
    headcore_public_key: Optional[str] = None   # base64url Ed25519
    allow_origins: str = "*"  # comma-separated

    class Config:
        env_file = ".env"

settings = Settings()
