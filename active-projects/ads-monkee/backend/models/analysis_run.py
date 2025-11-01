"""
Analysis Run Models
===================

Database models for tracking AI analysis runs, results, and decisions.
"""

import enum
from datetime import datetime
from typing import Optional
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.types import Numeric as SQLDecimal

from backend.models.base import BaseModel


class AnalysisRunStatus(str, enum.Enum):
    """Analysis run status."""
    QUEUED = "queued"
    RUNNING = "running"
    DONE = "done"
    ERROR = "error"


class AnalysisRunPhase(str, enum.Enum):
    """Current phase of analysis run."""
    PREPARE = "prepare"
    KEYWORDS = "keywords"
    BIDDING = "bidding"
    SYNTHESIS = "synthesis"
    PERSIST = "persist"


class AnalysisRun(BaseModel):
    """
    Analysis Run Tracking
    
    Tracks each analysis run with metadata for caching and debugging.
    """
    __tablename__ = "analysis_runs"
    
    # Primary identification
    run_id = Column(UUID(as_uuid=True), unique=True, nullable=False, default=uuid4, index=True)
    client_id = Column(Integer, ForeignKey("clients.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Configuration
    window_days = Column(Integer, nullable=False, default=30)
    model = Column(String(100), nullable=True)  # e.g., "gpt-4-turbo", "claude-3-sonnet"
    prompt_version = Column(String(50), nullable=True)  # e.g., "v1.2.3"
    feature_hash = Column(String(64), nullable=True, index=True)  # For caching
    
    # Status tracking
    status = Column(Enum(AnalysisRunStatus), nullable=False, default=AnalysisRunStatus.QUEUED, index=True)
    current_phase = Column(Enum(AnalysisRunPhase), nullable=True)
    progress_pct = Column(Integer, nullable=True)  # 0-100
    error = Column(Text, nullable=True)
    
    # Timestamps
    started_at = Column(DateTime(timezone=True), nullable=True)
    finished_at = Column(DateTime(timezone=True), nullable=True)
    
    # Cost tracking
    input_tokens = Column(Integer, nullable=True)
    output_tokens = Column(Integer, nullable=True)
    cost_usd = Column(SQLDecimal(10, 4), nullable=True)
    
    # Relationships
    client = relationship("Client", back_populates="analysis_runs")
    report = relationship("AnalysisReport", back_populates="run", uselist=False, cascade="all, delete-orphan")
    recommendations = relationship("AnalysisRecommendation", back_populates="run", cascade="all, delete-orphan")
    
    __table_args__ = (
        # Cache lookup: skip if same feature_hash + prompt_version exists recently
        Index("idx_analysis_cache", "client_id", "feature_hash", "prompt_version", "created_at"),
        # Status queries
        Index("idx_analysis_status", "client_id", "status", "created_at"),
    )
    
    @property
    def duration_seconds(self) -> Optional[float]:
        """Calculate run duration in seconds."""
        if self.started_at and self.finished_at:
            return (self.finished_at - self.started_at).total_seconds()
        return None


class AnalysisReport(BaseModel):
    """
    Analysis Report Storage
    
    Stores the canonical JSON output and derived Markdown.
    """
    __tablename__ = "analysis_reports"
    
    # Link to run
    run_id = Column(UUID(as_uuid=True), ForeignKey("analysis_runs.run_id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    
    # Canonical output
    json = Column(JSON, nullable=False)  # Synthesis model as JSON
    markdown = Column(Text, nullable=True)  # Human-readable report
    
    # Quick access metrics
    health_score = Column(Float, nullable=True)
    top_issues_count = Column(Integer, nullable=True)
    recommendations_count = Column(Integer, nullable=True)
    has_parallel_campaign = Column(Boolean, nullable=False, default=False)
    
    # Relationships
    run = relationship("AnalysisRun", back_populates="report")
    
    __table_args__ = (
        Index("idx_report_health", "health_score", "created_at"),
    )


class RecommendationCategory(str, enum.Enum):
    """Recommendation category."""
    COST_EFFICIENCY = "cost_efficiency"
    QUERY_HYGIENE = "query_hygiene"
    BIDDING = "bidding"
    BUDGET = "budget"
    GEO = "geo"
    DEVICE = "device"
    DEMO = "demo"


class RecommendationAction(str, enum.Enum):
    """Recommendation action type."""
    ADD_NEGATIVE = "add_negative"
    PAUSE_KEYWORD = "pause_keyword"
    CHANGE_BID = "change_bid"
    SHIFT_BUDGET = "shift_budget"
    CREATE_PARALLEL_CAMPAIGN = "create_parallel_campaign"


class RiskLevel(str, enum.Enum):
    """Risk level for recommendation."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class AnalysisRecommendation(BaseModel):
    """
    Individual Recommendation
    
    Normalized storage of each recommendation for tracking and approval.
    """
    __tablename__ = "analysis_recommendations"
    
    # Link to run
    run_id = Column(UUID(as_uuid=True), ForeignKey("analysis_runs.run_id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Recommendation details
    entity_type = Column(String(50), nullable=False)  # campaign, ad_group, keyword, etc.
    entity_id = Column(String(100), nullable=False)
    category = Column(Enum(RecommendationCategory), nullable=False, index=True)
    action = Column(Enum(RecommendationAction), nullable=False, index=True)
    
    # Content
    rationale_md = Column(Text, nullable=False)
    expected_impact = Column(JSON, nullable=True)  # {'cpa': -15.5, 'conversions': +3.2}
    
    # Metadata
    risk = Column(Enum(RiskLevel), nullable=False, default=RiskLevel.MEDIUM)
    confidence = Column(Float, nullable=False, default=0.65)
    prerequisites = Column(JSON, nullable=True)  # List of prerequisite actions
    
    # Relationships
    run = relationship("AnalysisRun", back_populates="recommendations")
    decision = relationship("RecommendationDecision", back_populates="recommendation", uselist=False, cascade="all, delete-orphan")
    
    __table_args__ = (
        Index("idx_recommendation_category", "category", "action"),
        Index("idx_recommendation_risk", "risk", "confidence"),
    )


class DecisionStatus(str, enum.Enum):
    """Decision status for a recommendation."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    MODIFIED = "modified"


class RecommendationDecision(BaseModel):
    """
    Supervisor Decision
    
    Tracks approval/rejection of recommendations.
    """
    __tablename__ = "recommendation_decisions"
    
    # Link to recommendation
    recommendation_id = Column(Integer, ForeignKey("analysis_recommendations.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    
    # Decision
    decision = Column(Enum(DecisionStatus), nullable=False, default=DecisionStatus.PENDING, index=True)
    decided_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    decided_at = Column(DateTime(timezone=True), nullable=True)
    
    # Optional modifications
    notes = Column(Text, nullable=True)
    modified_values = Column(JSON, nullable=True)  # If decision=modified
    
    # Relationships
    recommendation = relationship("AnalysisRecommendation", back_populates="decision")
    decider = relationship("User")
    action = relationship("ActionExecution", back_populates="decision", uselist=False, cascade="all, delete-orphan")


class ActionStatus(str, enum.Enum):
    """Execution status for an action."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


class ActionExecution(BaseModel):
    """
    Action Execution Audit
    
    Tracks actual changes made to Google Ads campaigns.
    """
    __tablename__ = "action_executions"
    
    # Link to decision
    decision_id = Column(Integer, ForeignKey("recommendation_decisions.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    
    # Execution tracking
    status = Column(Enum(ActionStatus), nullable=False, default=ActionStatus.PENDING, index=True)
    executed_at = Column(DateTime(timezone=True), nullable=True)
    executed_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    # API interaction
    api_request = Column(JSON, nullable=True)  # Request sent to Google Ads API
    api_response = Column(JSON, nullable=True)  # Response from Google Ads API
    api_error = Column(Text, nullable=True)
    
    # Rollback support
    rollback_data = Column(JSON, nullable=True)  # Data needed to undo this action
    rolled_back_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    decision = relationship("RecommendationDecision", back_populates="action")
    executor = relationship("User", foreign_keys=[executed_by])
    
    __table_args__ = (
        Index("idx_action_status", "status", "executed_at"),
    )


# Add relationships to Client model
def init_client_relationships():
    """Add analysis relationships to Client model."""
    from backend.models.client import Client
    Client.analysis_runs = relationship("AnalysisRun", back_populates="client", cascade="all, delete-orphan")

