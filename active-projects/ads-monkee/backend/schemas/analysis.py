"""
Analysis Schemas
================

Pydantic models for AI analysis inputs and outputs.
These enforce strict JSON validation per the architecture.
"""

from datetime import datetime
from typing import Dict, List, Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


# ==============================================================================
# Core Analysis Models
# ==============================================================================

class Recommendation(BaseModel):
    """
    Single recommendation from AI analysis.
    
    This is the atomic unit of actionable insight.
    """
    entity_type: Literal["campaign", "ad_group", "keyword", "search_term", "segment"]
    entity_id: str
    category: Literal[
        "cost_efficiency",
        "query_hygiene",
        "bidding",
        "budget",
        "geo",
        "device",
        "demo"
    ]
    action: Literal[
        "add_negative",
        "pause_keyword",
        "change_bid",
        "shift_budget",
        "create_parallel_campaign"
    ]
    rationale_md: str = Field(..., description="Markdown-formatted rationale")
    expected_impact: Dict[str, float] = Field(
        default_factory=dict,
        description="Expected changes: {'cpa': -15.5, 'conversions': +3.2}"
    )
    risk: Literal["low", "medium", "high"] = "medium"
    confidence: float = Field(default=0.65, ge=0.0, le=1.0)
    prerequisites: List[str] = Field(
        default_factory=list,
        description="Actions that must be completed first"
    )
    
    @field_validator("rationale_md")
    @classmethod
    def validate_rationale(cls, v: str) -> str:
        """Ensure rationale is not empty."""
        if not v or not v.strip():
            raise ValueError("Rationale cannot be empty")
        return v.strip()


class ParallelCampaignProposal(BaseModel):
    """
    Proposal for creating a parallel campaign.
    
    See docs/PARALLEL-CAMPAIGN-STRATEGY.md for full context.
    """
    original_campaign_id: str
    original_campaign_name: str
    proposed_campaign_name: str
    
    # Budget split
    original_budget_pct: float = Field(default=0.7, ge=0.0, le=1.0)
    new_budget_pct: float = Field(default=0.3, ge=0.0, le=1.0)
    
    # Changes
    keyword_changes: Dict[str, List[str]] = Field(
        default_factory=dict,
        description="{'add': [...], 'remove': [...]}"
    )
    bidding_strategy_change: Optional[str] = None
    target_cpa: Optional[float] = None
    target_roas: Optional[float] = None
    
    # Metadata
    learning_period_days: int = Field(default=21, ge=7, le=60)
    transition_schedule: Literal["conservative", "aggressive"] = "conservative"
    
    # Expected impact
    expected_cpa_improvement: float = Field(default=0.0, description="Percentage improvement")
    expected_conversion_rate_improvement: float = Field(default=0.0)
    confidence: float = Field(default=0.65, ge=0.0, le=1.0)
    
    @field_validator("original_budget_pct", "new_budget_pct")
    @classmethod
    def validate_budget_split(cls, v: float, info) -> float:
        """Ensure budget percentages sum to 1.0."""
        # Note: Full validation requires both fields, done in model_validator
        return v


class Synthesis(BaseModel):
    """
    Complete analysis synthesis.
    
    This is the canonical output from the AI analysis pipeline.
    All other formats (Markdown, UI) are derived from this.
    """
    health_score: float = Field(..., ge=0.0, le=10.0, description="Overall campaign health 0-10")
    top_issues: List[str] = Field(..., min_length=1, max_length=10)
    recommendations: List[Recommendation] = Field(..., min_length=0)
    parallel_campaign: Optional[ParallelCampaignProposal] = None
    
    # Metadata
    analysis_window_days: int = Field(default=30)
    data_quality_score: float = Field(default=1.0, ge=0.0, le=1.0)
    confidence_notes: List[str] = Field(default_factory=list)
    
    @field_validator("top_issues")
    @classmethod
    def validate_top_issues(cls, v: List[str]) -> List[str]:
        """Ensure issues are not empty strings."""
        return [issue.strip() for issue in v if issue.strip()]


# ==============================================================================
# Analysis Run Tracking
# ==============================================================================

class AnalysisRunCreate(BaseModel):
    """Request to create a new analysis run."""
    client_id: int
    window_days: int = Field(default=30, ge=7, le=90)
    force_refresh: bool = Field(default=False, description="Ignore cache")


class AnalysisRunStatus(BaseModel):
    """Status response for an analysis run."""
    run_id: UUID
    client_id: int
    status: Literal["queued", "running", "done", "error"]
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    error: Optional[str] = None
    
    # Progress tracking
    current_phase: Optional[Literal["prepare", "keywords", "bidding", "synthesis", "persist"]] = None
    progress_pct: Optional[int] = Field(default=None, ge=0, le=100)


class AnalysisRunResult(BaseModel):
    """Complete analysis run result."""
    run_id: UUID
    client_id: int
    status: Literal["done", "error"]
    
    # Results (only when status=done)
    result_json: Optional[Synthesis] = Field(None, alias="json")
    markdown: Optional[str] = None
    
    class Config:
        populate_by_name = True  # Allow both 'result_json' and 'json' as input
    
    # Metadata
    model: Optional[str] = None
    prompt_version: Optional[str] = None
    cost: Optional[Dict[str, float]] = Field(
        default=None,
        description="{'input_tokens': 1234, 'output_tokens': 987, 'usd': 0.42}"
    )
    
    # Timestamps
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None


# ==============================================================================
# Decision Tracking
# ==============================================================================

class RecommendationDecision(BaseModel):
    """Supervisor decision on a recommendation."""
    recommendation_id: int
    decision: Literal["approved", "rejected", "modified"]
    notes: Optional[str] = None
    modified_values: Optional[Dict] = None


class BulkDecision(BaseModel):
    """Bulk approve/reject multiple recommendations."""
    run_id: UUID
    decisions: List[RecommendationDecision]


# ==============================================================================
# Context Building (Internal)
# ==============================================================================

class AnalysisContext(BaseModel):
    """
    Internal model for passing data between Celery tasks.
    
    This is built from focus views and aggregates.
    """
    client_id: int
    window_days: int
    
    # Aggregated summaries
    campaigns_summary: List[Dict] = Field(default_factory=list)
    
    # Focus data (token-capped)
    focus_keywords: List[Dict] = Field(default_factory=list, max_length=200)
    focus_search_terms: List[Dict] = Field(default_factory=list, max_length=200)
    focus_segments: List[Dict] = Field(default_factory=list, max_length=100)
    
    # Client goals
    target_cpa: Optional[float] = None
    target_roas: Optional[float] = None
    monthly_budget: Optional[float] = None
    
    # Feature hash for caching
    feature_hash: Optional[str] = None
    
    @field_validator("focus_keywords", "focus_search_terms", "focus_segments")
    @classmethod
    def enforce_row_limits(cls, v: List[Dict]) -> List[Dict]:
        """Hard cap on rows to prevent token creep."""
        max_length = cls.model_fields[cls.__name__].max_length
        if len(v) > max_length:
            raise ValueError(f"Exceeded maximum rows: {len(v)} > {max_length}")
        return v


# ==============================================================================
# Module Outputs (Internal)
# ==============================================================================

class KeywordQueryModuleOutput(BaseModel):
    """Output from keyword/query analysis module."""
    negative_keywords_to_add: List[str] = Field(default_factory=list)
    keywords_to_pause: List[Dict] = Field(default_factory=list)
    search_terms_with_issues: List[Dict] = Field(default_factory=list)
    recommendations: List[Recommendation] = Field(default_factory=list)


class BiddingBudgetModuleOutput(BaseModel):
    """Output from bidding/budget analysis module."""
    bidding_strategy_recommendations: List[Dict] = Field(default_factory=list)
    budget_reallocation: List[Dict] = Field(default_factory=list)
    recommendations: List[Recommendation] = Field(default_factory=list)

