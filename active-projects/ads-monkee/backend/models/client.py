"""
Client Model
============

Represents a client account (business using Ads Monkee services).
"""

from datetime import datetime
from typing import List

from sqlalchemy import Column, DateTime, String, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum

from backend.models.base import BaseModel


class ClientStatus(str, enum.Enum):
    """Client account status."""
    ACTIVE = "active"
    PAUSED = "paused"
    ARCHIVED = "archived"


class Client(BaseModel):
    """
    Client Account Model
    
    Represents a business using Ads Monkee services.
    Each client may have Google Ads, LSA, and call tracking data.
    """
    
    __tablename__ = "clients"
    
    # Basic Information
    name = Column(String(255), nullable=False, index=True)
    slug = Column(String(255), nullable=False, unique=True, index=True)
    
    # Status
    status = Column(
        SQLEnum(ClientStatus),
        nullable=False,
        default=ClientStatus.ACTIVE,
        index=True
    )
    
    # Google Ads Integration
    google_ads_customer_id = Column(String(50), unique=True, index=True)
    google_ads_account_name = Column(String(255))
    
    # GoHighLevel Integration
    ghl_location_id = Column(String(100), index=True)
    ghl_contact_id = Column(String(100), index=True)
    
    # Sync Tracking
    last_sync_at = Column(DateTime, nullable=True)
    last_analysis_at = Column(DateTime, nullable=True)
    
    # Relationships
    users = relationship("User", back_populates="client", lazy="selectin")
    google_ads_campaigns = relationship(
        "GoogleAdsCampaign",
        back_populates="client",
        lazy="select"
    )
    analyses = relationship("Analysis", back_populates="client", lazy="select")
    campaign_modifications = relationship(
        "CampaignModification",
        back_populates="client",
        lazy="select"
    )
    analysis_runs = relationship(
        "AnalysisRun",
        back_populates="client",
        lazy="select",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<Client(id={self.id}, name='{self.name}', status={self.status.value})>"
    
    @property
    def is_active(self) -> bool:
        """Check if client is active."""
        return self.status == ClientStatus.ACTIVE
    
    @property
    def google_ads_customer_id_formatted(self) -> str:
        """Get Google Ads customer ID with dashes (XXX-XXX-XXXX)."""
        if not self.google_ads_customer_id:
            return None
        
        # Remove existing dashes
        clean_id = self.google_ads_customer_id.replace("-", "")
        
        # Format as XXX-XXX-XXXX
        if len(clean_id) == 10:
            return f"{clean_id[:3]}-{clean_id[3:6]}-{clean_id[6:]}"
        
        return clean_id

