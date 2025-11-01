"""
Google Ads Models
=================

Models for Google Ads campaign performance data.
"""

from datetime import date
from decimal import Decimal

from sqlalchemy import (
    Column,
    Date,
    ForeignKey,
    Integer,
    String,
    BigInteger,
    UniqueConstraint,
    Index,
)
from sqlalchemy.types import Numeric as SQLDecimal
from sqlalchemy.orm import relationship

from backend.models.base import BaseModel


class GoogleAdsCampaign(BaseModel):
    """
    Google Ads Campaign Performance Model
    
    Daily performance metrics at campaign level.
    Synced daily via Celery task.
    """
    
    __tablename__ = "google_ads_campaigns"
    
    # Client Association
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False, index=True)
    
    # Google Ads IDs
    campaign_id = Column(BigInteger, nullable=False, index=True)
    campaign_name = Column(String(255), nullable=False)
    
    # Performance Date
    date = Column(Date, nullable=False, index=True)
    
    # Campaign Details
    campaign_status = Column(String(50))
    channel_type = Column(String(50))
    bidding_strategy = Column(String(50))
    
    # Core Metrics
    impressions = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    cost = Column(SQLDecimal(10, 2), default=0)
    conversions = Column(SQLDecimal(8, 2), default=0)
    conversions_value = Column(SQLDecimal(10, 2), default=0)
    all_conversions = Column(SQLDecimal(8, 2), default=0)
    view_through_conversions = Column(SQLDecimal(8, 2), default=0)
    
    # Averages
    avg_cpc = Column(SQLDecimal(8, 2), nullable=True)
    avg_cpm = Column(SQLDecimal(8, 2), nullable=True)
    
    # Impression Share
    impression_share = Column(SQLDecimal(5, 4), nullable=True)
    budget_lost_is = Column(SQLDecimal(5, 4), nullable=True)
    rank_lost_is = Column(SQLDecimal(5, 4), nullable=True)
    
    # Derived Metrics (calculated)
    ctr = Column(SQLDecimal(5, 4), nullable=True)
    cpc = Column(SQLDecimal(8, 2), nullable=True)
    cpa = Column(SQLDecimal(8, 2), nullable=True)
    roas = Column(SQLDecimal(8, 2), nullable=True)
    
    # Relationships
    client = relationship("Client", back_populates="google_ads_campaigns")
    
    __table_args__ = (
        UniqueConstraint("client_id", "campaign_id", "date", name="uq_campaign_date"),
        Index("idx_campaigns_client_date", "client_id", "date"),
        Index("idx_campaigns_campaign_id", "campaign_id"),
    )
    
    def __repr__(self) -> str:
        return (
            f"<GoogleAdsCampaign(id={self.id}, campaign='{self.campaign_name}', "
            f"date={self.date}, cost={self.cost})>"
        )


class GoogleAdsAdGroup(BaseModel):
    """
    Google Ads Ad Group Performance Model
    
    Daily performance metrics at ad group level.
    """
    
    __tablename__ = "google_ads_ad_groups"
    
    # Client Association
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False, index=True)
    
    # Google Ads IDs
    campaign_id = Column(BigInteger, nullable=False, index=True)
    campaign_name = Column(String(255), nullable=False)
    ad_group_id = Column(BigInteger, nullable=False, index=True)
    ad_group_name = Column(String(255), nullable=False)
    
    # Performance Date
    date = Column(Date, nullable=False, index=True)
    
    # Ad Group Details
    ad_group_status = Column(String(50))
    ad_group_type = Column(String(50))
    cpc_bid = Column(SQLDecimal(8, 2), nullable=True)
    
    # Core Metrics
    impressions = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    cost = Column(SQLDecimal(10, 2), default=0)
    conversions = Column(SQLDecimal(8, 2), default=0)
    conversions_value = Column(SQLDecimal(10, 2), default=0)
    avg_cpc = Column(SQLDecimal(8, 2), nullable=True)
    
    # Derived Metrics
    ctr = Column(SQLDecimal(5, 4), nullable=True)
    cpc = Column(SQLDecimal(8, 2), nullable=True)
    cpa = Column(SQLDecimal(8, 2), nullable=True)
    cvr = Column(SQLDecimal(5, 4), nullable=True)
    
    # Relationships
    client = relationship("Client")
    
    __table_args__ = (
        UniqueConstraint("client_id", "ad_group_id", "date", name="uq_ad_group_date"),
        Index("idx_ad_groups_client_date", "client_id", "date"),
    )


class GoogleAdsKeyword(BaseModel):
    """
    Google Ads Keyword Performance Model
    
    Daily performance metrics at keyword level.
    Includes quality score metrics.
    """
    
    __tablename__ = "google_ads_keywords"
    
    # Client Association
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False, index=True)
    
    # Google Ads IDs
    campaign_id = Column(BigInteger, nullable=False)
    campaign_name = Column(String(255), nullable=False)
    ad_group_id = Column(BigInteger, nullable=False)
    ad_group_name = Column(String(255), nullable=False)
    keyword_id = Column(BigInteger, nullable=False, index=True)
    
    # Performance Date
    date = Column(Date, nullable=False, index=True)
    
    # Keyword Details
    keyword_text = Column(String(500), nullable=False, index=True)
    match_type = Column(String(50))
    keyword_status = Column(String(50))
    
    # Quality Score Metrics
    quality_score = Column(Integer, nullable=True)
    creative_quality = Column(String(50), nullable=True)
    landing_page_quality = Column(String(50), nullable=True)
    expected_ctr = Column(String(50), nullable=True)
    
    # Bidding
    max_cpc_bid = Column(SQLDecimal(8, 2), nullable=True)
    final_url = Column(String(1000), nullable=True)
    
    # Core Metrics
    impressions = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    cost = Column(SQLDecimal(10, 2), default=0)
    conversions = Column(SQLDecimal(8, 2), default=0)
    conversions_value = Column(SQLDecimal(10, 2), default=0)
    avg_cpc = Column(SQLDecimal(8, 2), nullable=True)
    
    # Derived Metrics
    ctr = Column(SQLDecimal(5, 4), nullable=True)
    cpc = Column(SQLDecimal(8, 2), nullable=True)
    cpa = Column(SQLDecimal(8, 2), nullable=True)
    cvr = Column(SQLDecimal(5, 4), nullable=True)
    
    # Relationships
    client = relationship("Client")
    
    __table_args__ = (
        UniqueConstraint("client_id", "ad_group_id", "keyword_id", "date", name="uq_keyword_date"),
        Index("idx_keywords_client_date", "client_id", "date"),
        Index("idx_keywords_quality_score", "quality_score"),
    )


class GoogleAdsSearchTerm(BaseModel):
    """
    Google Ads Search Term Model
    
    Actual search queries that triggered ads.
    Critical for negative keyword discovery.
    """
    
    __tablename__ = "google_ads_search_terms"
    
    # Client Association
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False, index=True)
    
    # Google Ads IDs
    campaign_id = Column(BigInteger, nullable=False)
    campaign_name = Column(String(255), nullable=False)
    ad_group_id = Column(BigInteger, nullable=False)
    ad_group_name = Column(String(255), nullable=False)
    
    # Performance Date
    date = Column(Date, nullable=False, index=True)
    
    # Search Term Details
    search_term = Column(String(500), nullable=False, index=True)
    search_term_status = Column(String(50))
    match_type_delivered = Column(String(50))
    
    # Core Metrics
    impressions = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    cost = Column(SQLDecimal(10, 2), default=0)
    conversions = Column(SQLDecimal(8, 2), default=0)
    conversions_value = Column(SQLDecimal(10, 2), default=0)
    
    # Derived Metrics
    ctr = Column(SQLDecimal(5, 4), nullable=True)
    cpc = Column(SQLDecimal(8, 2), nullable=True)
    cpa = Column(SQLDecimal(8, 2), nullable=True)
    cvr = Column(SQLDecimal(5, 4), nullable=True)
    
    # Relationships
    client = relationship("Client")
    
    __table_args__ = (
        # No unique constraint - same search term can appear multiple times per day
        Index("idx_search_terms_client_date", "client_id", "date"),
        Index("idx_search_terms_search_term", "search_term"),
        Index("idx_search_terms_zero_conv", "conversions", "cost"),  # For waste detection
    )

