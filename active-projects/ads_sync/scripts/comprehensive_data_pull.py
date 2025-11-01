#!/usr/bin/env python3
"""
comprehensive_data_pull.py - Pull ALL Google Ads data for comprehensive campaign analysis

This script pulls every piece of data needed to analyze a Google Ads campaign:
- Campaign performance & settings
- Ad Group performance & targeting
- Keywords (bids, quality scores, match types, performance)
- Ads (copy, headlines, descriptions, performance)
- Search Terms (actual queries triggering ads)
- Geographic Performance (location breakdown)
- Device Performance (mobile/desktop/tablet)
- Age/Gender Performance (demographic data)

Usage:
    # Pull all data for a single client
    python scripts/comprehensive_data_pull.py --client priority-roofing --days 30

    # Pull all data for all clients
    python scripts/comprehensive_data_pull.py --all --days 90

    # Pull specific data types
    python scripts/comprehensive_data_pull.py --client priority-roofing --types campaigns,keywords,search_terms

Author: OneClickSEO PPC Management
Version: 0.1.0
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any
import pandas as pd
import pytz

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
import yaml


BASE_DIR = Path(__file__).resolve().parent.parent
CONFIGS_DIR = BASE_DIR / "configs" / "clients"
DATA_DIR = BASE_DIR / "data"
GOOGLE_ADS_YAML = BASE_DIR / "google-ads.yaml"


# --- Data Pull Functions ---

def fetch_campaign_details(
    client: GoogleAdsClient,
    customer_id: str,
    start_date: str,
    end_date: str
) -> pd.DataFrame:
    """
    Fetch comprehensive campaign data including performance and settings.
    """
    customer_id_clean = customer_id.replace("-", "")
    ga_service = client.get_service("GoogleAdsService")
    
    query = f"""
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
            metrics.average_cost,
            metrics.search_impression_share,
            metrics.search_budget_lost_impression_share,
            metrics.search_rank_lost_impression_share
        FROM campaign
        WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
        ORDER BY segments.date ASC
    """
    
    print(f"[CAMPAIGNS] Fetching campaign performance data...")
    
    try:
        response = ga_service.search(customer_id=customer_id_clean, query=query)
        
        rows = []
        for row in response:
            campaign = row.campaign
            metrics = row.metrics
            
            rows.append({
                'date': row.segments.date,
                'campaign_id': campaign.id,
                'campaign_name': campaign.name,
                'campaign_status': campaign.status.name,
                'channel_type': campaign.advertising_channel_type.name,
                'bidding_strategy': campaign.bidding_strategy_type.name,
                'impressions': metrics.impressions,
                'clicks': metrics.clicks,
                'cost': metrics.cost_micros / 1_000_000,
                'conversions': metrics.conversions,
                'conversions_value': metrics.conversions_value,
                'all_conversions': metrics.all_conversions,
                'view_through_conversions': metrics.view_through_conversions,
                'avg_cpc': metrics.average_cpc / 1_000_000 if metrics.average_cpc else None,
                'avg_cpm': metrics.average_cpm / 1_000_000 if metrics.average_cpm else None,
                'impression_share': metrics.search_impression_share,
                'budget_lost_is': metrics.search_budget_lost_impression_share,
                'rank_lost_is': metrics.search_rank_lost_impression_share,
            })
        
        df = pd.DataFrame(rows)
        print(f"[CAMPAIGNS] Fetched {len(df)} rows")
        return df
    
    except GoogleAdsException as ex:
        print(f"[ERROR] Google Ads API error (campaigns):")
        for error in ex.failure.errors:
            print(f"  {error.message}")
        raise


def fetch_ad_group_details(
    client: GoogleAdsClient,
    customer_id: str,
    start_date: str,
    end_date: str
) -> pd.DataFrame:
    """
    Fetch ad group performance data.
    """
    customer_id_clean = customer_id.replace("-", "")
    ga_service = client.get_service("GoogleAdsService")
    
    query = f"""
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
            metrics.average_cpc,
            metrics.average_cost
        FROM ad_group
        WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
        ORDER BY segments.date ASC
    """
    
    print(f"[AD GROUPS] Fetching ad group performance data...")
    
    try:
        response = ga_service.search(customer_id=customer_id_clean, query=query)
        
        rows = []
        for row in response:
            rows.append({
                'date': row.segments.date,
                'campaign_id': row.campaign.id,
                'campaign_name': row.campaign.name,
                'ad_group_id': row.ad_group.id,
                'ad_group_name': row.ad_group.name,
                'ad_group_status': row.ad_group.status.name,
                'ad_group_type': row.ad_group.type.name,
                'cpc_bid': row.ad_group.cpc_bid_micros / 1_000_000 if row.ad_group.cpc_bid_micros else None,
                'impressions': row.metrics.impressions,
                'clicks': row.metrics.clicks,
                'cost': row.metrics.cost_micros / 1_000_000,
                'conversions': row.metrics.conversions,
                'conversions_value': row.metrics.conversions_value,
                'avg_cpc': row.metrics.average_cpc / 1_000_000 if row.metrics.average_cpc else None,
            })
        
        df = pd.DataFrame(rows)
        print(f"[AD GROUPS] Fetched {len(df)} rows")
        return df
    
    except GoogleAdsException as ex:
        print(f"[ERROR] Google Ads API error (ad groups):")
        for error in ex.failure.errors:
            print(f"  {error.message}")
        raise


def fetch_keyword_details(
    client: GoogleAdsClient,
    customer_id: str,
    start_date: str,
    end_date: str
) -> pd.DataFrame:
    """
    Fetch keyword performance data including quality scores and match types.
    """
    customer_id_clean = customer_id.replace("-", "")
    ga_service = client.get_service("GoogleAdsService")
    
    query = f"""
        SELECT
            segments.date,
            campaign.id,
            campaign.name,
            ad_group.id,
            ad_group.name,
            ad_group_criterion.keyword.text,
            ad_group_criterion.keyword.match_type,
            ad_group_criterion.criterion_id,
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
    
    print(f"[KEYWORDS] Fetching keyword performance data...")
    
    try:
        response = ga_service.search(customer_id=customer_id_clean, query=query)
        
        rows = []
        for row in response:
            criterion = row.ad_group_criterion
            quality_info = criterion.quality_info
            
            rows.append({
                'date': row.segments.date,
                'campaign_id': row.campaign.id,
                'campaign_name': row.campaign.name,
                'ad_group_id': row.ad_group.id,
                'ad_group_name': row.ad_group.name,
                'keyword_id': criterion.criterion_id,
                'keyword_text': criterion.keyword.text,
                'match_type': criterion.keyword.match_type.name,
                'keyword_status': criterion.status.name,
                'quality_score': quality_info.quality_score if quality_info.quality_score else None,
                'creative_quality': quality_info.creative_quality_score.name if quality_info.creative_quality_score else None,
                'landing_page_quality': quality_info.post_click_quality_score.name if quality_info.post_click_quality_score else None,
                'expected_ctr': quality_info.search_predicted_ctr.name if quality_info.search_predicted_ctr else None,
                'max_cpc_bid': criterion.cpc_bid_micros / 1_000_000 if criterion.cpc_bid_micros else None,
                'final_url': criterion.final_urls[0] if criterion.final_urls else None,
                'impressions': row.metrics.impressions,
                'clicks': row.metrics.clicks,
                'cost': row.metrics.cost_micros / 1_000_000,
                'conversions': row.metrics.conversions,
                'conversions_value': row.metrics.conversions_value,
                'avg_cpc': row.metrics.average_cpc / 1_000_000 if row.metrics.average_cpc else None,
            })
        
        df = pd.DataFrame(rows)
        print(f"[KEYWORDS] Fetched {len(df)} rows")
        return df
    
    except GoogleAdsException as ex:
        print(f"[ERROR] Google Ads API error (keywords):")
        for error in ex.failure.errors:
            print(f"  {error.message}")
        raise


def fetch_search_terms(
    client: GoogleAdsClient,
    customer_id: str,
    start_date: str,
    end_date: str
) -> pd.DataFrame:
    """
    Fetch search term report - actual queries that triggered ads.
    
    Note: Search term queries can be large, so we chunk by 30-day periods
    to avoid timeouts and process in batches.
    """
    customer_id_clean = customer_id.replace("-", "")
    ga_service = client.get_service("GoogleAdsService")
    
    # Convert dates to datetime for chunking
    from datetime import datetime, timedelta
    start_dt = datetime.strptime(start_date, '%Y-%m-%d')
    end_dt = datetime.strptime(end_date, '%Y-%m-%d')
    
    print(f"[SEARCH TERMS] Fetching search query report in 30-day chunks...")
    
    all_rows = []
    chunk_size = 30  # days per chunk
    current_start = start_dt
    
    while current_start <= end_dt:
        current_end = min(current_start + timedelta(days=chunk_size - 1), end_dt)
        chunk_start_str = current_start.strftime('%Y-%m-%d')
        chunk_end_str = current_end.strftime('%Y-%m-%d')
        
        print(f"[SEARCH TERMS]   Chunk: {chunk_start_str} to {chunk_end_str}")
        
        query = f"""
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
            WHERE segments.date BETWEEN '{chunk_start_str}' AND '{chunk_end_str}'
            ORDER BY segments.date ASC
        """
        
        try:
            response = ga_service.search(customer_id=customer_id_clean, query=query)
            
            chunk_rows = 0
            for row in response:
                all_rows.append({
                    'date': row.segments.date,
                    'campaign_id': row.campaign.id,
                    'campaign_name': row.campaign.name,
                    'ad_group_id': row.ad_group.id,
                    'ad_group_name': row.ad_group.name,
                    'search_term': row.search_term_view.search_term,
                    'search_term_status': row.search_term_view.status.name,
                    'match_type_delivered': row.segments.search_term_match_type.name,
                    'impressions': row.metrics.impressions,
                    'clicks': row.metrics.clicks,
                    'cost': row.metrics.cost_micros / 1_000_000,
                    'conversions': row.metrics.conversions,
                    'conversions_value': row.metrics.conversions_value,
                })
                chunk_rows += 1
            
            print(f"[SEARCH TERMS]     → {chunk_rows} rows")
        
        except GoogleAdsException as ex:
            print(f"[ERROR] Google Ads API error (search terms chunk {chunk_start_str}):")
            for error in ex.failure.errors:
                print(f"  {error.message}")
            print(f"[WARNING] Skipping chunk {chunk_start_str} to {chunk_end_str}")
        
        current_start = current_end + timedelta(days=1)
    
    df = pd.DataFrame(all_rows)
    print(f"[SEARCH TERMS] Total fetched: {len(df)} rows")
    return df


def fetch_ad_details(
    client: GoogleAdsClient,
    customer_id: str,
    start_date: str,
    end_date: str
) -> pd.DataFrame:
    """
    Fetch ad copy and performance data.
    """
    customer_id_clean = customer_id.replace("-", "")
    ga_service = client.get_service("GoogleAdsService")
    
    query = f"""
        SELECT
            segments.date,
            campaign.id,
            campaign.name,
            ad_group.id,
            ad_group.name,
            ad_group_ad.ad.id,
            ad_group_ad.ad.type,
            ad_group_ad.ad.final_urls,
            ad_group_ad.ad.responsive_search_ad.headlines,
            ad_group_ad.ad.responsive_search_ad.descriptions,
            ad_group_ad.status,
            metrics.impressions,
            metrics.clicks,
            metrics.cost_micros,
            metrics.conversions,
            metrics.conversions_value
        FROM ad_group_ad
        WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
        ORDER BY segments.date ASC
    """
    
    print(f"[ADS] Fetching ad copy and performance...")
    
    try:
        response = ga_service.search(customer_id=customer_id_clean, query=query)
        
        rows = []
        for row in response:
            ad = row.ad_group_ad.ad
            
            # Extract headlines (max 15 for RSA)
            headlines = []
            if hasattr(ad, 'responsive_search_ad') and ad.responsive_search_ad.headlines:
                headlines = [h.text for h in ad.responsive_search_ad.headlines[:15]]
            
            # Extract descriptions (max 4 for RSA)
            descriptions = []
            if hasattr(ad, 'responsive_search_ad') and ad.responsive_search_ad.descriptions:
                descriptions = [d.text for d in ad.responsive_search_ad.descriptions[:4]]
            
            rows.append({
                'date': row.segments.date,
                'campaign_id': row.campaign.id,
                'campaign_name': row.campaign.name,
                'ad_group_id': row.ad_group.id,
                'ad_group_name': row.ad_group.name,
                'ad_id': ad.id,
                'ad_type': ad.type.name,
                'ad_status': row.ad_group_ad.status.name,
                'final_url': ad.final_urls[0] if ad.final_urls else None,
                'headline_1': headlines[0] if len(headlines) > 0 else None,
                'headline_2': headlines[1] if len(headlines) > 1 else None,
                'headline_3': headlines[2] if len(headlines) > 2 else None,
                'all_headlines': ' | '.join(headlines) if headlines else None,
                'description_1': descriptions[0] if len(descriptions) > 0 else None,
                'description_2': descriptions[1] if len(descriptions) > 1 else None,
                'all_descriptions': ' | '.join(descriptions) if descriptions else None,
                'impressions': row.metrics.impressions,
                'clicks': row.metrics.clicks,
                'cost': row.metrics.cost_micros / 1_000_000,
                'conversions': row.metrics.conversions,
                'conversions_value': row.metrics.conversions_value,
            })
        
        df = pd.DataFrame(rows)
        print(f"[ADS] Fetched {len(df)} rows")
        return df
    
    except GoogleAdsException as ex:
        print(f"[ERROR] Google Ads API error (ads):")
        for error in ex.failure.errors:
            print(f"  {error.message}")
        raise


def fetch_geographic_performance(
    client: GoogleAdsClient,
    customer_id: str,
    start_date: str,
    end_date: str
) -> pd.DataFrame:
    """
    Fetch performance by geographic location.
    """
    customer_id_clean = customer_id.replace("-", "")
    ga_service = client.get_service("GoogleAdsService")
    
    query = f"""
        SELECT
            segments.date,
            campaign.id,
            campaign.name,
            segments.geo_target_city,
            segments.geo_target_region,
            segments.geo_target_metro,
            user_location_view.country_criterion_id,
            metrics.impressions,
            metrics.clicks,
            metrics.cost_micros,
            metrics.conversions,
            metrics.conversions_value
        FROM user_location_view
        WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
        ORDER BY segments.date ASC
    """
    
    print(f"[GEOGRAPHIC] Fetching geographic performance data...")
    
    try:
        response = ga_service.search(customer_id=customer_id_clean, query=query)
        
        rows = []
        for row in response:
            rows.append({
                'date': row.segments.date,
                'campaign_id': row.campaign.id,
                'campaign_name': row.campaign.name,
                'city': row.segments.geo_target_city if row.segments.geo_target_city else None,
                'region': row.segments.geo_target_region if row.segments.geo_target_region else None,
                'metro': row.segments.geo_target_metro if row.segments.geo_target_metro else None,
                'country_id': row.user_location_view.country_criterion_id if row.user_location_view.country_criterion_id else None,
                'impressions': row.metrics.impressions,
                'clicks': row.metrics.clicks,
                'cost': row.metrics.cost_micros / 1_000_000,
                'conversions': row.metrics.conversions,
                'conversions_value': row.metrics.conversions_value,
            })
        
        df = pd.DataFrame(rows)
        print(f"[GEOGRAPHIC] Fetched {len(df)} rows")
        return df
    
    except GoogleAdsException as ex:
        print(f"[ERROR] Google Ads API error (geographic):")
        for error in ex.failure.errors:
            print(f"  {error.message}")
        raise


def fetch_device_performance(
    client: GoogleAdsClient,
    customer_id: str,
    start_date: str,
    end_date: str
) -> pd.DataFrame:
    """
    Fetch performance by device type (mobile/desktop/tablet).
    """
    customer_id_clean = customer_id.replace("-", "")
    ga_service = client.get_service("GoogleAdsService")
    
    query = f"""
        SELECT
            segments.date,
            campaign.id,
            campaign.name,
            segments.device,
            metrics.impressions,
            metrics.clicks,
            metrics.cost_micros,
            metrics.conversions,
            metrics.conversions_value,
            metrics.average_cpc
        FROM campaign
        WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
        ORDER BY segments.date ASC
    """
    
    print(f"[DEVICE] Fetching device performance data...")
    
    try:
        response = ga_service.search(customer_id=customer_id_clean, query=query)
        
        rows = []
        for row in response:
            rows.append({
                'date': row.segments.date,
                'campaign_id': row.campaign.id,
                'campaign_name': row.campaign.name,
                'device': row.segments.device.name,
                'impressions': row.metrics.impressions,
                'clicks': row.metrics.clicks,
                'cost': row.metrics.cost_micros / 1_000_000,
                'conversions': row.metrics.conversions,
                'conversions_value': row.metrics.conversions_value,
                'avg_cpc': row.metrics.average_cpc / 1_000_000 if row.metrics.average_cpc else None,
            })
        
        df = pd.DataFrame(rows)
        print(f"[DEVICE] Fetched {len(df)} rows")
        return df
    
    except GoogleAdsException as ex:
        print(f"[ERROR] Google Ads API error (device):")
        for error in ex.failure.errors:
            print(f"  {error.message}")
        raise


def fetch_demographic_performance(
    client: GoogleAdsClient,
    customer_id: str,
    start_date: str,
    end_date: str
) -> pd.DataFrame:
    """
    Fetch performance by age and gender demographics.
    """
    customer_id_clean = customer_id.replace("-", "")
    ga_service = client.get_service("GoogleAdsService")
    
    query = f"""
        SELECT
            segments.date,
            campaign.id,
            campaign.name,
            ad_group.id,
            ad_group.name,
            segments.age_range,
            segments.gender,
            metrics.impressions,
            metrics.clicks,
            metrics.cost_micros,
            metrics.conversions,
            metrics.conversions_value
        FROM age_range_view
        WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
        ORDER BY segments.date ASC
    """
    
    print(f"[DEMOGRAPHICS] Fetching age/gender performance data...")
    
    try:
        response = ga_service.search(customer_id=customer_id_clean, query=query)
        
        rows = []
        for row in response:
            rows.append({
                'date': row.segments.date,
                'campaign_id': row.campaign.id,
                'campaign_name': row.campaign.name,
                'ad_group_id': row.ad_group.id,
                'ad_group_name': row.ad_group.name,
                'age_range': row.segments.age_range.name,
                'gender': row.segments.gender.name,
                'impressions': row.metrics.impressions,
                'clicks': row.metrics.clicks,
                'cost': row.metrics.cost_micros / 1_000_000,
                'conversions': row.metrics.conversions,
                'conversions_value': row.metrics.conversions_value,
            })
        
        df = pd.DataFrame(rows)
        print(f"[DEMOGRAPHICS] Fetched {len(df)} rows")
        return df
    
    except GoogleAdsException as ex:
        print(f"[ERROR] Google Ads API error (demographics):")
        for error in ex.failure.errors:
            print(f"  {error.message}")
        raise


# --- Main Execution ---

def pull_all_data(client_slug: str, days: int, data_types: List[str]):
    """
    Pull all specified data types for a client.
    """
    # Load client config
    config_path = CONFIGS_DIR / f"{client_slug}.yaml"
    if not config_path.exists():
        print(f"[ERROR] Config not found: {config_path}")
        return False
    
    with open(config_path) as f:
        config = yaml.safe_load(f)
    
    customer_id = config['client_id']
    client_name = config['client_name']
    
    # Calculate date range
    end_date = datetime.now(pytz.UTC) - timedelta(days=1)
    start_date = end_date - timedelta(days=days)
    
    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')
    
    print("\n" + "=" * 80)
    print(f"COMPREHENSIVE DATA PULL")
    print("=" * 80)
    print(f"Client:       {client_name} ({client_slug})")
    print(f"Customer ID:  {customer_id}")
    print(f"Date Range:   {start_date_str} to {end_date_str} ({days} days)")
    print(f"Data Types:   {', '.join(data_types)}")
    print("=" * 80 + "\n")
    
    # Initialize Google Ads client
    try:
        client = GoogleAdsClient.load_from_storage(str(GOOGLE_ADS_YAML))
    except Exception as e:
        print(f"[ERROR] Failed to initialize Google Ads client: {e}")
        return False
    
    # Create output directory
    output_dir = DATA_DIR / client_slug / "comprehensive"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Pull each data type
    results = {}
    
    if 'campaigns' in data_types:
        try:
            df = fetch_campaign_details(client, customer_id, start_date_str, end_date_str)
            output_file = output_dir / f"{client_slug}-campaigns-{timestamp}.csv"
            df.to_csv(output_file, index=False)
            print(f"[OK] Saved campaigns to: {output_file}\n")
            results['campaigns'] = len(df)
        except Exception as e:
            print(f"[ERROR] Failed to pull campaigns: {e}\n")
            results['campaigns'] = 0
    
    if 'ad_groups' in data_types:
        try:
            df = fetch_ad_group_details(client, customer_id, start_date_str, end_date_str)
            output_file = output_dir / f"{client_slug}-ad_groups-{timestamp}.csv"
            df.to_csv(output_file, index=False)
            print(f"[OK] Saved ad groups to: {output_file}\n")
            results['ad_groups'] = len(df)
        except Exception as e:
            print(f"[ERROR] Failed to pull ad groups: {e}\n")
            results['ad_groups'] = 0
    
    if 'keywords' in data_types:
        try:
            df = fetch_keyword_details(client, customer_id, start_date_str, end_date_str)
            output_file = output_dir / f"{client_slug}-keywords-{timestamp}.csv"
            df.to_csv(output_file, index=False)
            print(f"[OK] Saved keywords to: {output_file}\n")
            results['keywords'] = len(df)
        except Exception as e:
            print(f"[ERROR] Failed to pull keywords: {e}\n")
            results['keywords'] = 0
    
    if 'search_terms' in data_types:
        try:
            df = fetch_search_terms(client, customer_id, start_date_str, end_date_str)
            output_file = output_dir / f"{client_slug}-search_terms-{timestamp}.csv"
            df.to_csv(output_file, index=False)
            print(f"[OK] Saved search terms to: {output_file}\n")
            results['search_terms'] = len(df)
        except Exception as e:
            print(f"[ERROR] Failed to pull search terms: {e}\n")
            results['search_terms'] = 0
    
    if 'ads' in data_types:
        try:
            df = fetch_ad_details(client, customer_id, start_date_str, end_date_str)
            output_file = output_dir / f"{client_slug}-ads-{timestamp}.csv"
            df.to_csv(output_file, index=False)
            print(f"[OK] Saved ads to: {output_file}\n")
            results['ads'] = len(df)
        except Exception as e:
            print(f"[ERROR] Failed to pull ads: {e}\n")
            results['ads'] = 0
    
    if 'geographic' in data_types:
        try:
            df = fetch_geographic_performance(client, customer_id, start_date_str, end_date_str)
            output_file = output_dir / f"{client_slug}-geographic-{timestamp}.csv"
            df.to_csv(output_file, index=False)
            print(f"[OK] Saved geographic data to: {output_file}\n")
            results['geographic'] = len(df)
        except Exception as e:
            print(f"[ERROR] Failed to pull geographic data: {e}\n")
            results['geographic'] = 0
    
    if 'device' in data_types:
        try:
            df = fetch_device_performance(client, customer_id, start_date_str, end_date_str)
            output_file = output_dir / f"{client_slug}-device-{timestamp}.csv"
            df.to_csv(output_file, index=False)
            print(f"[OK] Saved device data to: {output_file}\n")
            results['device'] = len(df)
        except Exception as e:
            print(f"[ERROR] Failed to pull device data: {e}\n")
            results['device'] = 0
    
    if 'demographics' in data_types:
        try:
            df = fetch_demographic_performance(client, customer_id, start_date_str, end_date_str)
            output_file = output_dir / f"{client_slug}-demographics-{timestamp}.csv"
            df.to_csv(output_file, index=False)
            print(f"[OK] Saved demographics data to: {output_file}\n")
            results['demographics'] = len(df)
        except Exception as e:
            print(f"[ERROR] Failed to pull demographics data: {e}\n")
            results['demographics'] = 0
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    for data_type, row_count in results.items():
        print(f"{data_type:<20} {row_count:>10} rows")
    print("=" * 80)
    print(f"\nAll data saved to: {output_dir}\n")
    
    return True


def main():
    parser = argparse.ArgumentParser(
        description='Pull comprehensive Google Ads data for campaign analysis'
    )
    parser.add_argument(
        '--client',
        type=str,
        help='Client slug (e.g., priority-roofing)'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Pull data for all clients'
    )
    parser.add_argument(
        '--days',
        type=int,
        default=30,
        help='Number of days to pull (default: 30)'
    )
    parser.add_argument(
        '--types',
        type=str,
        default='campaigns,ad_groups,keywords,search_terms,ads,geographic,device,demographics',
        help='Comma-separated list of data types to pull (default: all)'
    )
    
    args = parser.parse_args()
    
    # Parse data types
    data_types = [t.strip() for t in args.types.split(',')]
    
    if args.all:
        # Pull for all clients
        config_files = list(CONFIGS_DIR.glob("*.yaml"))
        print(f"\n[INFO] Found {len(config_files)} client configs")
        
        for config_file in config_files:
            client_slug = config_file.stem
            pull_all_data(client_slug, args.days, data_types)
    
    elif args.client:
        # Pull for single client
        pull_all_data(args.client, args.days, data_types)
    
    else:
        print("[ERROR] Must specify --client or --all")
        parser.print_help()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

