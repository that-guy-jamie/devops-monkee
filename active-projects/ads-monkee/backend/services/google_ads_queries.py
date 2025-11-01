"""
Google Ads Query Templates
===========================

Standardized GAQL queries for pulling comprehensive campaign data.
These queries match the schema used in ads_sync/comprehensive_data_pull.py

All queries are tested and validated against Google Ads API v16+.
"""

from typing import Dict, Callable
from datetime import datetime


# =============================================================================
# Campaign Queries
# =============================================================================

def get_campaign_query(start_date: str, end_date: str) -> str:
    """
    Comprehensive campaign performance query.
    
    Returns:
        date, campaign_id, campaign_name, campaign_status, channel_type,
        bidding_strategy, impressions, clicks, cost, conversions,
        conversions_value, all_conversions, view_through_conversions,
        avg_cpc, avg_cpm, impression_share, budget_lost_is, rank_lost_is
    """
    return f"""
        SELECT
            segments.date,
            campaign.id,
            campaign.name,
            campaign.status,
            campaign.advertising_channel_type,
            campaign.bidding_strategy_type,
            metrics.impressions,
            metrics.clicks,
            metrics.cost_micros,
            metrics.conversions,
            metrics.conversions_value,
            metrics.all_conversions,
            metrics.view_through_conversions,
            metrics.average_cpc,
            metrics.average_cpm,
            metrics.search_impression_share,
            metrics.search_budget_lost_impression_share,
            metrics.search_rank_lost_impression_share
        FROM campaign
        WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
        ORDER BY segments.date ASC
    """


# =============================================================================
# Ad Group Queries
# =============================================================================

def get_ad_group_query(start_date: str, end_date: str) -> str:
    """
    Comprehensive ad group performance query.
    
    Returns:
        date, campaign_id, campaign_name, ad_group_id, ad_group_name,
        ad_group_status, ad_group_type, cpc_bid, impressions, clicks,
        cost, conversions, conversions_value, avg_cpc
    """
    return f"""
        SELECT
            segments.date,
            campaign.id,
            campaign.name,
            ad_group.id,
            ad_group.name,
            ad_group.status,
            ad_group.type,
            ad_group.cpc_bid_micros,
            metrics.impressions,
            metrics.clicks,
            metrics.cost_micros,
            metrics.conversions,
            metrics.conversions_value,
            metrics.average_cpc
        FROM ad_group
        WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
        ORDER BY segments.date ASC
    """


# =============================================================================
# Keyword Queries
# =============================================================================

def get_keyword_query(start_date: str, end_date: str) -> str:
    """
    Comprehensive keyword performance query including quality scores.
    
    Returns:
        date, campaign_id, campaign_name, ad_group_id, ad_group_name,
        keyword_id, keyword_text, match_type, keyword_status,
        quality_score, creative_quality, landing_page_quality, expected_ctr,
        max_cpc_bid, final_url, impressions, clicks, cost,
        conversions, conversions_value, avg_cpc
    """
    return f"""
        SELECT
            segments.date,
            campaign.id,
            campaign.name,
            ad_group.id,
            ad_group.name,
            ad_group_criterion.criterion_id,
            ad_group_criterion.keyword.text,
            ad_group_criterion.keyword.match_type,
            ad_group_criterion.status,
            ad_group_criterion.quality_info.quality_score,
            ad_group_criterion.quality_info.creative_quality_score,
            ad_group_criterion.quality_info.post_click_quality_score,
            ad_group_criterion.quality_info.search_predicted_ctr,
            ad_group_criterion.cpc_bid_micros,
            ad_group_criterion.final_urls,
            metrics.impressions,
            metrics.clicks,
            metrics.cost_micros,
            metrics.conversions,
            metrics.conversions_value,
            metrics.average_cpc
        FROM keyword_view
        WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
        ORDER BY segments.date ASC
    """


# =============================================================================
# Search Term Queries
# =============================================================================

def get_search_terms_query(start_date: str, end_date: str) -> str:
    """
    Search term performance query (actual user queries).
    
    Note: Search term queries can be large. Consider chunking by 30-day periods.
    
    Returns:
        date, campaign_id, campaign_name, ad_group_id, ad_group_name,
        search_term, search_term_status, match_type_delivered,
        impressions, clicks, cost, conversions, conversions_value
    """
    return f"""
        SELECT
            segments.date,
            campaign.id,
            campaign.name,
            ad_group.id,
            ad_group.name,
            segments.search_term_match_type,
            search_term_view.search_term,
            search_term_view.status,
            metrics.impressions,
            metrics.clicks,
            metrics.cost_micros,
            metrics.conversions,
            metrics.conversions_value
        FROM search_term_view
        WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
        ORDER BY segments.date ASC
    """


# =============================================================================
# Query Registry
# =============================================================================

QUERY_REGISTRY: Dict[str, Callable[[str, str], str]] = {
    'campaigns': get_campaign_query,
    'ad_groups': get_ad_group_query,
    'keywords': get_keyword_query,
    'search_terms': get_search_terms_query,
}


def get_query(query_type: str, start_date: str, end_date: str) -> str:
    """
    Get a query by type.
    
    Args:
        query_type: One of 'campaigns', 'ad_groups', 'keywords', 'search_terms'
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        
    Returns:
        GAQL query string
        
    Raises:
        ValueError: If query_type is not recognized
    """
    if query_type not in QUERY_REGISTRY:
        raise ValueError(
            f"Unknown query type: {query_type}. "
            f"Valid types: {', '.join(QUERY_REGISTRY.keys())}"
        )
    
    return QUERY_REGISTRY[query_type](start_date, end_date)


# =============================================================================
# Field Mapping (API → CSV → Database)
# =============================================================================

# Maps API field names to CSV column names (for consistency with ads_sync)
FIELD_MAPPINGS = {
    'campaigns': {
        'segments.date': 'date',
        'campaign.id': 'campaign_id',
        'campaign.name': 'campaign_name',
        'campaign.status': 'campaign_status',
        'campaign.advertising_channel_type': 'channel_type',
        'campaign.bidding_strategy_type': 'bidding_strategy',
        'metrics.impressions': 'impressions',
        'metrics.clicks': 'clicks',
        'metrics.cost_micros': 'cost',  # Convert from micros
        'metrics.conversions': 'conversions',
        'metrics.conversions_value': 'conversions_value',
        'metrics.all_conversions': 'all_conversions',
        'metrics.view_through_conversions': 'view_through_conversions',
        'metrics.average_cpc': 'avg_cpc',  # Already in currency units
        'metrics.average_cpm': 'avg_cpm',
        'metrics.search_impression_share': 'impression_share',
        'metrics.search_budget_lost_impression_share': 'budget_lost_is',
        'metrics.search_rank_lost_impression_share': 'rank_lost_is',
    },
    'ad_groups': {
        'segments.date': 'date',
        'campaign.id': 'campaign_id',
        'campaign.name': 'campaign_name',
        'ad_group.id': 'ad_group_id',
        'ad_group.name': 'ad_group_name',
        'ad_group.status': 'ad_group_status',
        'ad_group.type': 'ad_group_type',
        'ad_group.cpc_bid_micros': 'cpc_bid',  # Convert from micros
        'metrics.impressions': 'impressions',
        'metrics.clicks': 'clicks',
        'metrics.cost_micros': 'cost',
        'metrics.conversions': 'conversions',
        'metrics.conversions_value': 'conversions_value',
        'metrics.average_cpc': 'avg_cpc',
    },
    'keywords': {
        'segments.date': 'date',
        'campaign.id': 'campaign_id',
        'campaign.name': 'campaign_name',
        'ad_group.id': 'ad_group_id',
        'ad_group.name': 'ad_group_name',
        'ad_group_criterion.criterion_id': 'keyword_id',
        'ad_group_criterion.keyword.text': 'keyword_text',
        'ad_group_criterion.keyword.match_type': 'match_type',
        'ad_group_criterion.status': 'keyword_status',
        'ad_group_criterion.quality_info.quality_score': 'quality_score',
        'ad_group_criterion.quality_info.creative_quality_score': 'creative_quality',
        'ad_group_criterion.quality_info.post_click_quality_score': 'landing_page_quality',
        'ad_group_criterion.quality_info.search_predicted_ctr': 'expected_ctr',
        'ad_group_criterion.cpc_bid_micros': 'max_cpc_bid',
        'ad_group_criterion.final_urls': 'final_url',  # Take first URL
        'metrics.impressions': 'impressions',
        'metrics.clicks': 'clicks',
        'metrics.cost_micros': 'cost',
        'metrics.conversions': 'conversions',
        'metrics.conversions_value': 'conversions_value',
        'metrics.average_cpc': 'avg_cpc',
    },
    'search_terms': {
        'segments.date': 'date',
        'campaign.id': 'campaign_id',
        'campaign.name': 'campaign_name',
        'ad_group.id': 'ad_group_id',
        'ad_group.name': 'ad_group_name',
        'search_term_view.search_term': 'search_term',
        'search_term_view.status': 'search_term_status',
        'segments.search_term_match_type': 'match_type_delivered',
        'metrics.impressions': 'impressions',
        'metrics.clicks': 'clicks',
        'metrics.cost_micros': 'cost',
        'metrics.conversions': 'conversions',
        'metrics.conversions_value': 'conversions_value',
    },
}


def convert_micros_to_currency(value: int) -> float:
    """Convert micros (1/1,000,000 of currency unit) to currency units."""
    return value / 1_000_000.0

