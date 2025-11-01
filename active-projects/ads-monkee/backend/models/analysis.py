"""
Analysis Models
===============

AI-powered campaign analysis and multi-agent consensus tracking.
"""

import enum
from datetime import date
from decimal import Decimal

from sqlalchemy import (
    Column,
    Date,
    Enum as SQLEnum,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.types import Numeric as SQLDecimal
from sqlalchemy.orm import relationship

from backend.models.base import BaseModel


class AnalysisStatus(str, enum.Enum):
    """Analysis processing status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Analysis(BaseModel):
    """
    Analysis Model
    
    Stores AI-generated campaign analysis results.
    """
    
    __tablename__ = "analyses"
    
    # Client Association
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False, index=True)
    
    # Date Range
    date_range_start = Column(Date, nullable=False)
    date_range_end = Column(Date, nullable=False)
    
    # Status
    status = Column(
        SQLEnum(AnalysisStatus),
        nullable=False,
        default=AnalysisStatus.PENDING,
        index=True
    )
    
    # Analysis Results (JSON)
    analysis_data = Column(JSON, nullable=True)
    # Structure:
    # {
    #   "executive_summary": {...},
    #   "key_metrics": {...},
    #   "search_terms_analysis": {...},
    #   "quality_score_analysis": {...},
    #   "budget_recommendations": [...],
    #   "recommendations": [...]
    # }
    
    # Multi-Agent Consensus
    consensus_similarity_score = Column(SQLDecimal(3, 2), nullable=True)
    # 0.00 to 1.00 - how much agents agreed
    
    required_debate = Column(Integer, default=0)
    # 0 = consensus without debate, 1 = required 3rd agent
    
    # Error Tracking
    error_message = Column(Text, nullable=True)
    
    # Relationships
    client = relationship("Client", back_populates="analyses")
    consensus_session = relationship(
        "AIConsensusSession",
        back_populates="analysis",
        uselist=False
    )
    campaign_modifications = relationship(
        "CampaignModification",
        back_populates="analysis"
    )
    reports = relationship("Report", back_populates="analysis")
    
    def __repr__(self) -> str:
        return (
            f"<Analysis(id={self.id}, client_id={self.client_id}, "
            f"status={self.status.value}, date_range={self.date_range_start} to {self.date_range_end})>"
        )


class AIConsensusSession(BaseModel):
    """
    AI Consensus Session Model
    
    Tracks multi-agent debate and consensus process.
    """
    
    __tablename__ = "ai_consensus_sessions"
    
    # Analysis Association
    analysis_id = Column(
        Integer,
        ForeignKey("analyses.id"),
        nullable=False,
        unique=True,
        index=True
    )
    
    # Agent Outputs (JSON)
    agent_1_output = Column(JSON, nullable=True)  # Python analyzer
    agent_2_output = Column(JSON, nullable=True)  # Claude analyzer
    agent_3_output = Column(JSON, nullable=True)  # Claude mediator (if needed)
    
    # Similarity Scores
    similarity_score_1_2 = Column(SQLDecimal(3, 2), nullable=True)
    # Similarity between agent 1 and 2
    
    # Consensus Details
    required_debate = Column(Integer, default=0)
    debate_rounds = Column(Integer, default=0)
    final_consensus = Column(JSON, nullable=True)
    
    # Processing Time
    agent_1_duration_seconds = Column(Integer, nullable=True)
    agent_2_duration_seconds = Column(Integer, nullable=True)
    agent_3_duration_seconds = Column(Integer, nullable=True)
    total_duration_seconds = Column(Integer, nullable=True)
    
    # Relationships
    analysis = relationship("Analysis", back_populates="consensus_session")
    
    def __repr__(self) -> str:
        return (
            f"<AIConsensusSession(id={self.id}, analysis_id={self.analysis_id}, "
            f"similarity={self.similarity_score_1_2}, debate={bool(self.required_debate)})>"
        )


class Report(BaseModel):
    """
    Report Model
    
    Generated PDF/Markdown reports from analyses.
    """
    
    __tablename__ = "reports"
    
    # Associations
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False, index=True)
    analysis_id = Column(Integer, ForeignKey("analyses.id"), nullable=False, index=True)
    
    # Report Details
    report_type = Column(String(50), nullable=False)
    # Types: "comprehensive", "monthly", "executive", "client"
    
    # File Storage
    file_url = Column(String(1000), nullable=True)
    # URL if uploaded to GHL or cloud storage
    
    ghl_file_id = Column(String(100), nullable=True)
    # GHL file ID if uploaded to client portal
    
    # Generation Metadata
    format = Column(String(20), nullable=False)  # "pdf", "markdown", "html"
    file_size_bytes = Column(Integer, nullable=True)
    
    # Relationships
    client = relationship("Client")
    analysis = relationship("Analysis", back_populates="reports")
    
    def __repr__(self) -> str:
        return (
            f"<Report(id={self.id}, type='{self.report_type}', "
            f"client_id={self.client_id}, format={self.format})>"
        )

