"""
Campaign Modification Models
=============================

Proposed changes from AI analysis with approval workflow.
"""

import enum
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Column,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    Index,
)
from sqlalchemy.types import Numeric as SQLDecimal
from sqlalchemy.orm import relationship

from backend.models.base import BaseModel


class ModificationStatus(str, enum.Enum):
    """Status of campaign modification."""
    PENDING = "pending"        # Awaiting review
    APPROVED = "approved"      # Approved by staff
    REJECTED = "rejected"      # Rejected by staff
    APPLIED = "applied"        # Successfully executed via API
    FAILED = "failed"          # API execution failed


class ModificationActionType(str, enum.Enum):
    """Type of modification action."""
    # Keyword Actions
    ADD_NEGATIVE_KEYWORD = "add_negative_keyword"
    ADD_KEYWORD = "add_keyword"
    PAUSE_KEYWORD = "pause_keyword"
    ENABLE_KEYWORD = "enable_keyword"
    
    # Budget/Bid Actions
    ADJUST_BUDGET = "adjust_budget"
    ADJUST_BID = "adjust_bid"
    
    # Ad Copy Actions
    UPDATE_AD_COPY = "update_ad_copy"
    
    # Campaign Creation (Parallel Learning Strategy)
    CREATE_PARALLEL_CAMPAIGN = "create_parallel_campaign"
    # Creates new optimized campaign alongside existing
    # Allows learning phase before transitioning budget
    
    # Campaign Transition Actions
    TRANSITION_BUDGET = "transition_budget"
    # Gradually shift budget from old → new campaign
    
    PAUSE_OLD_CAMPAIGN = "pause_old_campaign"
    # Pause underperforming campaign after new one proves out


class ModificationPriority(str, enum.Enum):
    """Priority level for modification."""
    HIGH = "high"              # Immediate attention
    MEDIUM = "medium"          # Normal review
    LOW = "low"                # Optional/minor


class CampaignModification(BaseModel):
    """
    Campaign Modification Model
    
    Represents a proposed change to Google Ads campaign.
    Follows approval workflow before execution.
    """
    
    __tablename__ = "campaign_modifications"
    
    # Associations
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False, index=True)
    analysis_id = Column(Integer, ForeignKey("analyses.id"), nullable=False, index=True)
    
    # Modification Details
    action_type = Column(
        SQLEnum(ModificationActionType),
        nullable=False,
        index=True
    )
    
    target_type = Column(String(50), nullable=False)
    # "campaign", "ad_group", "keyword", "ad"
    
    target_id = Column(String(100), nullable=False, index=True)
    # Google Ads resource ID
    
    target_name = Column(String(255), nullable=True)
    # Human-readable name
    
    # Change Data (JSON)
    change_data = Column(JSON, nullable=False)
    # Structure depends on action_type:
    # add_negative_keyword: {"keyword": "...", "match_type": "...", "level": "campaign|ad_group"}
    # add_keyword: {"keyword": "...", "match_type": "...", "bid": 1.50}
    # adjust_budget: {"current": 50.00, "proposed": 65.00, "change_percent": 30}
    # adjust_bid: {"current": 1.50, "proposed": 2.00, "change_percent": 33}
    
    # AI Analysis
    ai_confidence_score = Column(SQLDecimal(3, 2), nullable=True)
    # 0.00 to 1.00 - how confident AI is in this recommendation
    
    priority = Column(
        SQLEnum(ModificationPriority),
        nullable=False,
        default=ModificationPriority.MEDIUM,
        index=True
    )
    
    # Impact Estimates
    estimated_monthly_impact = Column(SQLDecimal(10, 2), nullable=True)
    # Estimated monthly cost change (positive or negative)
    
    estimated_cpa_improvement = Column(SQLDecimal(8, 2), nullable=True)
    # Estimated CPA improvement
    
    reasoning = Column(Text, nullable=True)
    # AI's explanation for the recommendation
    
    # Workflow Status
    status = Column(
        SQLEnum(ModificationStatus),
        nullable=False,
        default=ModificationStatus.PENDING,
        index=True
    )
    
    # Review Tracking
    reviewed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    review_notes = Column(Text, nullable=True)
    
    # Execution Tracking
    applied_at = Column(DateTime, nullable=True)
    applied_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    api_response = Column(JSON, nullable=True)
    # Full API response from Google Ads
    
    error_message = Column(Text, nullable=True)
    
    # Relationships
    client = relationship("Client", back_populates="campaign_modifications")
    analysis = relationship("Analysis", back_populates="campaign_modifications")
    reviewer = relationship("User", foreign_keys=[reviewed_by])
    applier = relationship("User", foreign_keys=[applied_by])
    
    __table_args__ = (
        Index("idx_modifications_status_client", "status", "client_id"),
        Index("idx_modifications_priority", "priority", "status"),
    )
    
    def __repr__(self) -> str:
        return (
            f"<CampaignModification(id={self.id}, action={self.action_type.value}, "
            f"status={self.status.value}, priority={self.priority.value})>"
        )
    
    @property
    def is_pending(self) -> bool:
        """Check if modification is awaiting review."""
        return self.status == ModificationStatus.PENDING
    
    @property
    def is_approved(self) -> bool:
        """Check if modification is approved but not yet applied."""
        return self.status == ModificationStatus.APPROVED
    
    @property
    def is_applied(self) -> bool:
        """Check if modification has been successfully applied."""
        return self.status == ModificationStatus.APPLIED
    
    @property
    def can_be_applied(self) -> bool:
        """Check if modification can be executed."""
        return self.status == ModificationStatus.APPROVED
    
    def approve(self, user_id: int, notes: str = None) -> None:
        """Mark modification as approved."""
        self.status = ModificationStatus.APPROVED
        self.reviewed_by = user_id
        self.reviewed_at = datetime.utcnow()
        self.review_notes = notes
    
    def reject(self, user_id: int, notes: str = None) -> None:
        """Mark modification as rejected."""
        self.status = ModificationStatus.REJECTED
        self.reviewed_by = user_id
        self.reviewed_at = datetime.utcnow()
        self.review_notes = notes
    
    def mark_applied(self, user_id: int, api_response: dict) -> None:
        """Mark modification as successfully applied."""
        self.status = ModificationStatus.APPLIED
        self.applied_by = user_id
        self.applied_at = datetime.utcnow()
        self.api_response = api_response
    
    def mark_failed(self, error_message: str, api_response: dict = None) -> None:
        """Mark modification as failed."""
        self.status = ModificationStatus.FAILED
        self.error_message = error_message
        self.api_response = api_response

