"""
Build Aggregate Tables
=======================

Populates aggregate tables from raw Google Ads data.
These aggregates enable efficient AI analysis with token-capped queries.

Usage:
    # Full backfill (180 days)
    poetry run python scripts/build_aggregates.py
    
    # Incremental update (last 7 days)
    poetry run python scripts/build_aggregates.py --incremental
    
    # Specific client
    poetry run python scripts/build_aggregates.py --client-id 1
"""

import argparse
import sys
from datetime import datetime, timedelta
from pathlib import Path

from sqlalchemy import text

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.database import sync_engine


def build_campaign_aggregates(days: int = 180):
    """
    Build agg_campaign_daily from google_ads_campaigns.
    
    Aggregates daily campaign metrics with calculated fields.
    """
    print(f"[CAMPAIGNS] Building aggregates for last {days} days...")
    
    sql = f"""
    INSERT INTO agg_campaign_daily (
        client_id, campaign_id, campaign_name, date,
        impressions, clicks, cost, conversions, conversions_value,
        ctr, cpc, cpa, roas, cvr,
        created_at, updated_at
    )
    SELECT 
        client_id,
        campaign_id,
        campaign_name,
        date,
        SUM(impressions) as impressions,
        SUM(clicks) as clicks,
        SUM(cost) as cost,
        SUM(conversions) as conversions,
        SUM(conversions_value) as conversions_value,
        -- Calculated metrics
        CASE WHEN SUM(impressions) > 0 
            THEN SUM(clicks)::float / SUM(impressions) 
            ELSE NULL END as ctr,
        CASE WHEN SUM(clicks) > 0 
            THEN SUM(cost) / SUM(clicks) 
            ELSE NULL END as cpc,
        CASE WHEN SUM(conversions) > 0 
            THEN SUM(cost) / SUM(conversions) 
            ELSE NULL END as cpa,
        CASE WHEN SUM(cost) > 0 
            THEN SUM(conversions_value) / SUM(cost) 
            ELSE NULL END as roas,
        CASE WHEN SUM(clicks) > 0 
            THEN SUM(conversions)::float / SUM(clicks) 
            ELSE NULL END as cvr,
        NOW() as created_at,
        NOW() as updated_at
    FROM google_ads_campaigns
    WHERE date >= CURRENT_DATE - INTERVAL '{days} days'
    GROUP BY client_id, campaign_id, campaign_name, date
    ON CONFLICT (client_id, campaign_id, date) DO UPDATE SET
        impressions = EXCLUDED.impressions,
        clicks = EXCLUDED.clicks,
        cost = EXCLUDED.cost,
        conversions = EXCLUDED.conversions,
        conversions_value = EXCLUDED.conversions_value,
        ctr = EXCLUDED.ctr,
        cpc = EXCLUDED.cpc,
        cpa = EXCLUDED.cpa,
        roas = EXCLUDED.roas,
        cvr = EXCLUDED.cvr,
        updated_at = NOW();
    """
    
    with sync_engine.connect() as conn:
        result = conn.execute(text(sql))
        conn.commit()
        print(f"[CAMPAIGNS] Processed {result.rowcount} rows")


def build_adgroup_aggregates(days: int = 180):
    """
    Build agg_adgroup_daily from google_ads_ad_groups.
    """
    print(f"[AD GROUPS] Building aggregates for last {days} days...")
    
    sql = f"""
    INSERT INTO agg_adgroup_daily (
        client_id, campaign_id, campaign_name, ad_group_id, ad_group_name, date,
        impressions, clicks, cost, conversions, conversions_value,
        ctr, cpc, cpa, roas, cvr,
        created_at, updated_at
    )
    SELECT 
        client_id,
        campaign_id,
        campaign_name,
        ad_group_id,
        ad_group_name,
        date,
        SUM(impressions) as impressions,
        SUM(clicks) as clicks,
        SUM(cost) as cost,
        SUM(conversions) as conversions,
        SUM(conversions_value) as conversions_value,
        -- Calculated metrics
        CASE WHEN SUM(impressions) > 0 
            THEN SUM(clicks)::float / SUM(impressions) 
            ELSE NULL END as ctr,
        CASE WHEN SUM(clicks) > 0 
            THEN SUM(cost) / SUM(clicks) 
            ELSE NULL END as cpc,
        CASE WHEN SUM(conversions) > 0 
            THEN SUM(cost) / SUM(conversions) 
            ELSE NULL END as cpa,
        CASE WHEN SUM(cost) > 0 
            THEN SUM(conversions_value) / SUM(cost) 
            ELSE NULL END as roas,
        CASE WHEN SUM(clicks) > 0 
            THEN SUM(conversions)::float / SUM(clicks) 
            ELSE NULL END as cvr,
        NOW() as created_at,
        NOW() as updated_at
    FROM google_ads_ad_groups
    WHERE date >= CURRENT_DATE - INTERVAL '{days} days'
    GROUP BY client_id, campaign_id, campaign_name, ad_group_id, ad_group_name, date
    ON CONFLICT (client_id, ad_group_id, date) DO UPDATE SET
        impressions = EXCLUDED.impressions,
        clicks = EXCLUDED.clicks,
        cost = EXCLUDED.cost,
        conversions = EXCLUDED.conversions,
        conversions_value = EXCLUDED.conversions_value,
        ctr = EXCLUDED.ctr,
        cpc = EXCLUDED.cpc,
        cpa = EXCLUDED.cpa,
        roas = EXCLUDED.roas,
        cvr = EXCLUDED.cvr,
        updated_at = NOW();
    """
    
    with sync_engine.connect() as conn:
        result = conn.execute(text(sql))
        conn.commit()
        print(f"[AD GROUPS] Processed {result.rowcount} rows")


def build_keyword_aggregates(days: int = 180):
    """
    Build agg_keyword_daily from google_ads_keywords.

    Note: Data is already daily, so we just copy it with calculated metrics.
    """
    print(f"[KEYWORDS] Building aggregates for last {days} days...")

    # First, clear existing data for the date range to avoid conflicts
    # Use TRUNCATE for better performance on large datasets
    clear_sql = """
    TRUNCATE TABLE agg_keyword_daily RESTART IDENTITY
    """

    # Then insert fresh data
    insert_sql = f"""
    INSERT INTO agg_keyword_daily (
        client_id, campaign_id, campaign_name, ad_group_id, ad_group_name,
        keyword_id, keyword_text, match_type, date,
        impressions, clicks, cost, conversions, conversions_value,
        quality_score, ctr, cpc, cpa, roas, cvr,
        created_at, updated_at
    )
    SELECT
        client_id,
        campaign_id,
        campaign_name,
        ad_group_id,
        ad_group_name,
        keyword_id,
        keyword_text,
        match_type,
        date,
        impressions,
        clicks,
        cost,
        conversions,
        conversions_value,
        quality_score,
        -- Calculated metrics
        CASE WHEN impressions > 0
            THEN clicks::float / impressions
            ELSE NULL END as ctr,
        CASE WHEN clicks > 0
            THEN cost / clicks
            ELSE NULL END as cpc,
        CASE WHEN conversions > 0
            THEN cost / conversions
            ELSE NULL END as cpa,
        CASE WHEN cost > 0
            THEN conversions_value / cost
            ELSE NULL END as roas,
        CASE WHEN clicks > 0
            THEN conversions::float / clicks
            ELSE NULL END as cvr,
        NOW() as created_at,
        NOW() as updated_at
    FROM google_ads_keywords
    WHERE date >= CURRENT_DATE - INTERVAL '{days} days'
    """

    with sync_engine.connect() as conn:
        # Clear existing data
        conn.execute(text(clear_sql))
        conn.commit()
        print(f"[KEYWORDS] Cleared existing data for last {days} days")

        # Insert fresh data
        result = conn.execute(text(insert_sql))
        conn.commit()
        print(f"[KEYWORDS] Processed {result.rowcount} rows")


def build_search_term_aggregates(days: int = 180):
    """
    Build agg_search_term_daily from google_ads_search_terms.
    """
    print(f"[SEARCH TERMS] Building aggregates for last {days} days...")
    
    sql = f"""
    INSERT INTO agg_search_term_daily (
        client_id, campaign_id, campaign_name, ad_group_id, ad_group_name,
        search_term, match_type_delivered, date,
        impressions, clicks, cost, conversions, conversions_value,
        ctr, cpc, cpa, roas, cvr,
        created_at, updated_at
    )
    SELECT 
        client_id,
        campaign_id,
        campaign_name,
        ad_group_id,
        ad_group_name,
        search_term,
        match_type as match_type_delivered,
        date,
        SUM(impressions) as impressions,
        SUM(clicks) as clicks,
        SUM(cost) as cost,
        SUM(conversions) as conversions,
        SUM(conversions_value) as conversions_value,
        -- Calculated metrics
        CASE WHEN SUM(impressions) > 0 
            THEN SUM(clicks)::float / SUM(impressions) 
            ELSE NULL END as ctr,
        CASE WHEN SUM(clicks) > 0 
            THEN SUM(cost) / SUM(clicks) 
            ELSE NULL END as cpc,
        CASE WHEN SUM(conversions) > 0 
            THEN SUM(cost) / SUM(conversions) 
            ELSE NULL END as cpa,
        CASE WHEN SUM(cost) > 0 
            THEN SUM(conversions_value) / SUM(cost) 
            ELSE NULL END as roas,
        CASE WHEN SUM(clicks) > 0 
            THEN SUM(conversions)::float / SUM(clicks) 
            ELSE NULL END as cvr,
        NOW() as created_at,
        NOW() as updated_at
    FROM google_ads_search_terms
    WHERE date >= CURRENT_DATE - INTERVAL '{days} days'
    GROUP BY client_id, campaign_id, campaign_name, ad_group_id, ad_group_name,
             search_term, match_type, date
    ON CONFLICT (client_id, search_term, date) DO UPDATE SET
        impressions = EXCLUDED.impressions,
        clicks = EXCLUDED.clicks,
        cost = EXCLUDED.cost,
        conversions = EXCLUDED.conversions,
        conversions_value = EXCLUDED.conversions_value,
        ctr = EXCLUDED.ctr,
        cpc = EXCLUDED.cpc,
        cpa = EXCLUDED.cpa,
        roas = EXCLUDED.roas,
        cvr = EXCLUDED.cvr,
        updated_at = NOW();
    """
    
    with sync_engine.connect() as conn:
        result = conn.execute(text(sql))
        conn.commit()
        print(f"[SEARCH TERMS] Processed {result.rowcount} rows")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Build aggregate tables")
    parser.add_argument(
        "--incremental",
        action="store_true",
        help="Incremental update (last 7 days instead of 180)"
    )
    parser.add_argument(
        "--client-id",
        type=int,
        help="Process only specific client"
    )
    
    args = parser.parse_args()
    
    days = 7 if args.incremental else 180
    
    print(f"[BUILD AGGREGATES] Starting...")
    print(f"[BUILD AGGREGATES] Mode: {'Incremental (7 days)' if args.incremental else 'Full (180 days)'}")
    
    start_time = datetime.now()
    
    try:
        build_campaign_aggregates(days)
        build_adgroup_aggregates(days)
        build_keyword_aggregates(days)
        build_search_term_aggregates(days)
        
        duration = (datetime.now() - start_time).total_seconds()
        print()
        print(f"[BUILD AGGREGATES] Complete in {duration:.1f}s!")
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

