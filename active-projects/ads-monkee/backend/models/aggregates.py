"""
Aggregate Tables & Client Targets
==================================

Pre-aggregated data for efficient AI analysis.
These tables are populated by scheduled jobs from raw Google Ads data.
"""

from sqlalchemy import (
    Column,
    Date,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.types import Numeric as SQLDecimal

from backend.models.base import BaseModel


class ClientTargets(BaseModel):
    """
    Client Performance Targets
    
    Stores client goals for CPA, ROAS, and budgets.
    Used by focus views to identify underperforming elements.
    """
    __tablename__ = "client_targets"
    
    client_id = Column(Integer, ForeignKey("clients.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    
    # Performance targets
    target_cpa = Column(SQLDecimal(10, 2), nullable=True)
    target_roas = Column(SQLDecimal(10, 2), nullable=True)
    
    # Budget targets
    monthly_budget = Column(SQLDecimal(12, 2), nullable=True)
    daily_budget_limit = Column(SQLDecimal(10, 2), nullable=True)
    
    # Thresholds for alerts
    cpa_alert_threshold_pct = Column(Float, nullable=False, default=1.3)  # Alert if CPA > target * 1.3
    roas_alert_threshold_pct = Column(Float, nullable=False, default=0.7)  # Alert if ROAS < target * 0.7
    
    # Relationships
    client = relationship("Client")


class AggCampaignDaily(BaseModel):
    """
    Daily Campaign Aggregates
    
    Pre-aggregated campaign metrics for fast analysis.
    Populated from google_ads_campaigns table.
    """
    __tablename__ = "agg_campaign_daily"
    
    client_id = Column(Integer, ForeignKey("clients.id", ondelete="CASCADE"), nullable=False, index=True)
    campaign_id = Column(String(100), nullable=False, index=True)
    campaign_name = Column(String(255), nullable=False)
    date = Column(Date, nullable=False, index=True)
    
    # Metrics
    impressions = Column(Integer, nullable=False, default=0)
    clicks = Column(Integer, nullable=False, default=0)
    cost = Column(SQLDecimal(12, 2), nullable=False, default=0)
    conversions = Column(SQLDecimal(10, 2), nullable=False, default=0)
    conversions_value = Column(SQLDecimal(12, 2), nullable=False, default=0)
    
    # Calculated metrics
    ctr = Column(Float, nullable=True)  # clicks / impressions
    cpc = Column(SQLDecimal(10, 2), nullable=True)  # cost / clicks
    cpa = Column(SQLDecimal(10, 2), nullable=True)  # cost / conversions
    roas = Column(SQLDecimal(10, 2), nullable=True)  # conversions_value / cost
    cvr = Column(Float, nullable=True)  # conversions / clicks
    
    # Relationships
    client = relationship("Client")
    
    __table_args__ = (
        UniqueConstraint("client_id", "campaign_id", "date", name="uq_agg_campaign_daily"),
        Index("idx_agg_campaign_date", "client_id", "date"),
        Index("idx_agg_campaign_perf", "client_id", "cpa", "roas"),
    )


class AggAdGroupDaily(BaseModel):
    """
    Daily Ad Group Aggregates
    
    Pre-aggregated ad group metrics.
    """
    __tablename__ = "agg_adgroup_daily"
    
    client_id = Column(Integer, ForeignKey("clients.id", ondelete="CASCADE"), nullable=False, index=True)
    campaign_id = Column(String(100), nullable=False, index=True)
    campaign_name = Column(String(255), nullable=False)
    ad_group_id = Column(String(100), nullable=False, index=True)
    ad_group_name = Column(String(255), nullable=False)
    date = Column(Date, nullable=False, index=True)
    
    # Metrics
    impressions = Column(Integer, nullable=False, default=0)
    clicks = Column(Integer, nullable=False, default=0)
    cost = Column(SQLDecimal(12, 2), nullable=False, default=0)
    conversions = Column(SQLDecimal(10, 2), nullable=False, default=0)
    conversions_value = Column(SQLDecimal(12, 2), nullable=False, default=0)
    
    # Calculated metrics
    ctr = Column(Float, nullable=True)
    cpc = Column(SQLDecimal(10, 2), nullable=True)
    cpa = Column(SQLDecimal(10, 2), nullable=True)
    roas = Column(SQLDecimal(10, 2), nullable=True)
    cvr = Column(Float, nullable=True)
    
    # Relationships
    client = relationship("Client")
    
    __table_args__ = (
        UniqueConstraint("client_id", "ad_group_id", "date", name="uq_agg_adgroup_daily"),
        Index("idx_agg_adgroup_date", "client_id", "date"),
        Index("idx_agg_adgroup_perf", "client_id", "cpa", "roas"),
    )


class AggKeywordDaily(BaseModel):
    """
    Daily Keyword Aggregates
    
    Pre-aggregated keyword metrics with quality scores.
    """
    __tablename__ = "agg_keyword_daily"
    
    client_id = Column(Integer, ForeignKey("clients.id", ondelete="CASCADE"), nullable=False, index=True)
    campaign_id = Column(String(100), nullable=False)
    campaign_name = Column(String(255), nullable=False)
    ad_group_id = Column(String(100), nullable=False)
    ad_group_name = Column(String(255), nullable=False)
    keyword_id = Column(String(100), nullable=False, index=True)
    keyword_text = Column(String(255), nullable=False, index=True)
    match_type = Column(String(50), nullable=False)
    date = Column(Date, nullable=False, index=True)
    
    # Metrics
    impressions = Column(Integer, nullable=False, default=0)
    clicks = Column(Integer, nullable=False, default=0)
    cost = Column(SQLDecimal(12, 2), nullable=False, default=0)
    conversions = Column(SQLDecimal(10, 2), nullable=False, default=0)
    conversions_value = Column(SQLDecimal(12, 2), nullable=False, default=0)
    
    # Quality metrics
    quality_score = Column(Integer, nullable=True)
    
    # Calculated metrics
    ctr = Column(Float, nullable=True)
    cpc = Column(SQLDecimal(10, 2), nullable=True)
    cpa = Column(SQLDecimal(10, 2), nullable=True)
    roas = Column(SQLDecimal(10, 2), nullable=True)
    cvr = Column(Float, nullable=True)
    
    # Relationships
    client = relationship("Client")
    
    __table_args__ = (
        UniqueConstraint("client_id", "ad_group_id", "keyword_id", "date", name="uq_agg_keyword_daily"),
        Index("idx_agg_keyword_date", "client_id", "date"),
        Index("idx_agg_keyword_perf", "client_id", "cpa", "quality_score"),
        Index("idx_agg_keyword_text", "client_id", "keyword_text"),
    )


class AggSearchTermDaily(BaseModel):
    """
    Daily Search Term Aggregates
    
    Pre-aggregated search term metrics for query hygiene analysis.
    """
    __tablename__ = "agg_search_term_daily"
    
    client_id = Column(Integer, ForeignKey("clients.id", ondelete="CASCADE"), nullable=False, index=True)
    campaign_id = Column(String(100), nullable=False)
    campaign_name = Column(String(255), nullable=False)
    ad_group_id = Column(String(100), nullable=False)
    ad_group_name = Column(String(255), nullable=False)
    search_term = Column(String(500), nullable=False, index=True)
    match_type_delivered = Column(String(50), nullable=False)
    date = Column(Date, nullable=False, index=True)
    
    # Metrics
    impressions = Column(Integer, nullable=False, default=0)
    clicks = Column(Integer, nullable=False, default=0)
    cost = Column(SQLDecimal(12, 2), nullable=False, default=0)
    conversions = Column(SQLDecimal(10, 2), nullable=False, default=0)
    conversions_value = Column(SQLDecimal(12, 2), nullable=False, default=0)
    
    # Calculated metrics
    ctr = Column(Float, nullable=True)
    cpc = Column(SQLDecimal(10, 2), nullable=True)
    cpa = Column(SQLDecimal(10, 2), nullable=True)
    roas = Column(SQLDecimal(10, 2), nullable=True)
    cvr = Column(Float, nullable=True)
    
    # Relationships
    client = relationship("Client")
    
    __table_args__ = (
        UniqueConstraint("client_id", "search_term", "date", name="uq_agg_search_term_daily"),
        Index("idx_agg_search_term_date", "client_id", "date"),
        Index("idx_agg_search_term_perf", "client_id", "cost", "conversions"),
        Index("idx_agg_search_term_text", "client_id", "search_term"),
    )


# Note: agg_geo_device_demo can be added later if needed for MVP
# For now, we'll focus on campaigns, ad groups, keywords, and search terms

