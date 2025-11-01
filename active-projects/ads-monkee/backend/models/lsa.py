"""
LSA (Local Services Ads) Models
================================

Models for LSA lead tracking and survey management.
Integrates with existing LSA Survey Monitor.
"""

import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from backend.models.base import BaseModel


class LSALeadStatus(str, enum.Enum):
    """LSA lead status."""
    NEW = "new"
    CONTACTED = "contacted"
    BOOKED = "booked"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class LSALead(BaseModel):
    """
    LSA Lead Model
    
    Tracks Local Services Ads leads with survey management.
    
    CRITICAL RULES (per GPT analysis):
    1. Only charged leads get surveys (filter charged = true)
    2. Dual-flag tracking: Google boolean + internal ledger
    3. Survey API is write-only (can't read back)
    """
    
    __tablename__ = "lsa_leads"
    
    # Client Association
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False, index=True)
    
    # Google LSA IDs
    lead_id = Column(String(100), unique=True, nullable=False, index=True)
    # Google's unique lead identifier
    
    # Lead Details
    customer_name = Column(String(255))
    phone_number = Column(String(50))
    email = Column(String(255))
    
    # Lead Timing
    creation_timestamp = Column(DateTime, nullable=False)
    # When lead was created in Google LSA
    
    # Charging Status (CRITICAL FILTER)
    charged = Column(Boolean, default=False, nullable=False, index=True)
    # TRUE = lead was charged (eligible for survey)
    # FALSE = lead not charged (DO NOT survey)
    
    charge_status = Column(String(50))
    # "CHARGED", "NOT_CHARGED", "DISPUTED", etc.
    
    # Lead Status
    status = Column(
        SQLEnum(LSALeadStatus),
        default=LSALeadStatus.NEW,
        nullable=False,
        index=True
    )
    
    # Survey Tracking (Dual-Flag System)
    survey_sent_google = Column(Boolean, default=False, nullable=False)
    # Google's survey boolean (from their API)
    
    survey_sent_internal = Column(Boolean, default=False, nullable=False)
    # Our internal ledger (source of truth)
    
    survey_sent_at = Column(DateTime, nullable=True)
    # When we sent the survey
    
    survey_response_received = Column(Boolean, default=False, nullable=False)
    # Whether customer responded
    
    survey_rating = Column(Integer, nullable=True)
    # 1-5 star rating (if provided)
    
    # Additional Lead Data (JSON)
    lead_data = Column(JSON, nullable=True)
    # Full lead payload from Google
    
    # Service Details
    service_category = Column(String(100))
    job_type = Column(String(100))
    
    # Notes & Tracking
    notes = Column(Text, nullable=True)
    last_contact_at = Column(DateTime, nullable=True)
    
    # Audit
    last_synced_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    # When this lead was last synced from LSA API
    
    # Relationships
    client = relationship("Client")
    survey_attempts = relationship("LSASurveyAttempt", back_populates="lead")
    
    def __repr__(self) -> str:
        return (
            f"<LSALead(id={self.id}, lead_id='{self.lead_id}', "
            f"charged={self.charged}, survey_sent={self.survey_sent_internal})>"
        )
    
    @property
    def is_survey_eligible(self) -> bool:
        """
        Check if lead is eligible for survey.
        
        RULE: Only charged leads can receive surveys.
        """
        return self.charged and not self.survey_sent_internal
    
    @property
    def survey_status_consistent(self) -> bool:
        """
        Check if dual-flag survey status is consistent.
        
        Returns True if Google flag matches internal ledger.
        """
        return self.survey_sent_google == self.survey_sent_internal
    
    def mark_survey_sent(self) -> None:
        """Mark survey as sent (updates both flags)."""
        self.survey_sent_internal = True
        self.survey_sent_google = True
        self.survey_sent_at = datetime.utcnow()


class LSASurveyAttempt(BaseModel):
    """
    LSA Survey Attempt Model
    
    Tracks each attempt to send a survey to an LSA lead.
    Useful for debugging survey API issues.
    """
    
    __tablename__ = "lsa_survey_attempts"
    
    # Lead Association
    lead_id = Column(
        Integer,
        ForeignKey("lsa_leads.id"),
        nullable=False,
        index=True
    )
    
    # Attempt Details
    attempted_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    success = Column(Boolean, default=False, nullable=False)
    
    # API Response
    api_response = Column(JSON, nullable=True)
    # Full response from Google LSA API
    
    error_message = Column(Text, nullable=True)
    
    # Request Details
    request_payload = Column(JSON, nullable=True)
    # What we sent to the API
    
    # Relationships
    lead = relationship("LSALead", back_populates="survey_attempts")
    
    def __repr__(self) -> str:
        return (
            f"<LSASurveyAttempt(id={self.id}, lead_id={self.lead_id}, "
            f"success={self.success})>"
        )


class LSAMetrics(BaseModel):
    """
    LSA Aggregated Metrics Model
    
    Daily rollup of LSA performance by client.
    Calculated from lsa_leads table.
    """
    
    __tablename__ = "lsa_metrics"
    
    # Client Association
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False, index=True)
    
    # Date
    date = Column(DateTime, nullable=False, index=True)
    # Date these metrics represent
    
    # Lead Counts
    total_leads = Column(Integer, default=0)
    charged_leads = Column(Integer, default=0)
    uncharged_leads = Column(Integer, default=0)
    
    # Survey Metrics
    surveys_sent = Column(Integer, default=0)
    surveys_responded = Column(Integer, default=0)
    average_rating = Column(Integer, nullable=True)
    
    # Status Breakdown
    leads_new = Column(Integer, default=0)
    leads_contacted = Column(Integer, default=0)
    leads_booked = Column(Integer, default=0)
    leads_completed = Column(Integer, default=0)
    leads_cancelled = Column(Integer, default=0)
    
    # Relationships
    client = relationship("Client")
    
    def __repr__(self) -> str:
        return (
            f"<LSAMetrics(id={self.id}, client_id={self.client_id}, "
            f"date={self.date}, charged_leads={self.charged_leads})>"
        )

