"""
Database Models
===============

All SQLAlchemy models for Ads Monkee.
Import from here to ensure proper relationship loading.
"""

from backend.models.base import Base, BaseModel, TimestampMixin
from backend.models.client import Client, ClientStatus
from backend.models.user import User, UserRole
from backend.models.auth import AuthSession
from backend.models.audit_log import AuditLog
from backend.models.google_ads import (
    GoogleAdsAdGroup,
    GoogleAdsCampaign,
    GoogleAdsKeyword,
    GoogleAdsSearchTerm,
)
from backend.models.analysis import (
    AIConsensusSession,
    Analysis,
    AnalysisStatus,
    Report,
)
from backend.models.campaign_modification import (
    CampaignModification,
    ModificationActionType,
    ModificationPriority,
    ModificationStatus,
)
from backend.models.lsa import (
    LSALead,
    LSALeadStatus,
    LSAMetrics,
    LSASurveyAttempt,
)
from backend.models.aggregates import (
    AggAdGroupDaily,
    AggCampaignDaily,
    AggKeywordDaily,
    AggSearchTermDaily,
    ClientTargets,
)
from backend.models.analysis_run import (
    ActionExecution,
    ActionStatus,
    AnalysisRecommendation,
    AnalysisReport,
    AnalysisRun,
    AnalysisRunPhase,
    AnalysisRunStatus,
    DecisionStatus,
    RecommendationAction,
    RecommendationCategory,
    RecommendationDecision,
    RiskLevel,
)

__all__ = [
    # Base
    "Base",
    "BaseModel",
    "TimestampMixin",
    # Client
    "Client",
    "ClientStatus",
    # User & Auth
    "User",
    "UserRole",
    "AuthSession",
    # Audit
    "AuditLog",
    # Google Ads
    "GoogleAdsCampaign",
    "GoogleAdsAdGroup",
    "GoogleAdsKeyword",
    "GoogleAdsSearchTerm",
    # Analysis
    "Analysis",
    "AnalysisStatus",
    "AIConsensusSession",
    "Report",
    # Campaign Modifications
    "CampaignModification",
    "ModificationActionType",
    "ModificationPriority",
    "ModificationStatus",
    # LSA
    "LSALead",
    "LSALeadStatus",
    "LSAMetrics",
    "LSASurveyAttempt",
    # Aggregates
    "ClientTargets",
    "AggCampaignDaily",
    "AggAdGroupDaily",
    "AggKeywordDaily",
    "AggSearchTermDaily",
    # Analysis Runs
    "AnalysisRun",
    "AnalysisRunStatus",
    "AnalysisRunPhase",
    "AnalysisReport",
    "AnalysisRecommendation",
    "RecommendationCategory",
    "RecommendationAction",
    "RiskLevel",
    "RecommendationDecision",
    "DecisionStatus",
    "ActionExecution",
    "ActionStatus",
]
