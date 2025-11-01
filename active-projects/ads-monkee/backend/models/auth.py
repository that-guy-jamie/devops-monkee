"""
Authentication Models
=====================

Session management and JWT tracking.
"""

from datetime import datetime, timedelta

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from backend.models.base import BaseModel
from backend.config import settings


class AuthSession(BaseModel):
    """
    Authentication Session Model
    
    Tracks active JWT sessions for users.
    Sessions expire after JWT_EXPIRATION_HOURS.
    """
    
    __tablename__ = "auth_sessions"
    
    # User Association
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Token (hashed for security)
    token_hash = Column(String(255), nullable=False, unique=True, index=True)
    
    # Session Metadata
    expires_at = Column(DateTime, nullable=False, index=True)
    last_activity_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Client Information
    user_agent = Column(String(500))
    ip_address = Column(String(45))  # IPv4 or IPv6
    
    # GoHighLevel OAuth Tokens (encrypted in production)
    ghl_access_token = Column(Text, nullable=True)
    ghl_refresh_token = Column(Text, nullable=True)
    ghl_token_expires_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="auth_sessions")
    
    def __repr__(self) -> str:
        return f"<AuthSession(id={self.id}, user_id={self.user_id}, expires_at={self.expires_at})>"
    
    @property
    def is_expired(self) -> bool:
        """Check if session has expired."""
        return datetime.utcnow() > self.expires_at
    
    @property
    def is_valid(self) -> bool:
        """Check if session is still valid."""
        return not self.is_expired
    
    @classmethod
    def calculate_expiration(cls) -> datetime:
        """Calculate expiration time for new session."""
        return datetime.utcnow() + timedelta(hours=settings.JWT_EXPIRATION_HOURS)
    
    def refresh_activity(self) -> None:
        """Update last activity timestamp."""
        self.last_activity_at = datetime.utcnow()
    
    def needs_ghl_token_refresh(self) -> bool:
        """Check if GHL access token needs refresh."""
        if not self.ghl_token_expires_at:
            return False
        
        # Refresh if expires in next 5 minutes
        buffer = timedelta(minutes=5)
        return datetime.utcnow() + buffer >= self.ghl_token_expires_at

