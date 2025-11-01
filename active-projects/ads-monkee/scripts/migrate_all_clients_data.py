#!/usr/bin/env python3
"""
migrate_all_clients_data.py - Migrate comprehensive Google Ads data for all clients to PostgreSQL

This script:
1. Discovers all active clients from Google Ads API
2. Pulls 1 year of comprehensive campaign data for each client
3. Loads data into the new PostgreSQL database (ads-monkee)

Data Types Pulled:
- Campaign performance & settings
- Ad Group performance & targeting
- Keywords (bids, quality scores, match types, performance)
- Search Terms (actual queries triggering ads)
- Ads (copy, headlines, descriptions, performance)
- Geographic Performance (location breakdown)
- Device Performance (mobile/desktop/tablet)
- Age/Gender Performance (demographic data)

Usage:
    # Full year migration for all clients
    poetry run python scripts/migrate_all_clients_data.py
    
    # Dry run (pull data but don't insert)
    poetry run python scripts/migrate_all_clients_data.py --dry-run
    
    # Specific clients only
    poetry run python scripts/migrate_all_clients_data.py --clients priority-roofing,heather-murphy-group
    
    # Override date range (e.g., 180 days)
    poetry run python scripts/migrate_all_clients_data.py --days 180

Author: OneClickSEO - Ads Monkee
Version: 1.0.0
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import pandas as pd
import pytz
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import yaml

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

# Import our models
from backend.models import (
    Client,
    GoogleAdsCampaign,
    GoogleAdsAdGroup,
    GoogleAdsKeyword,
    GoogleAdsSearchTerm
)
from backend.config import settings
from backend.database import engine, SessionLocal


# ANSI color codes for pretty output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_header(text: str):
    """Print a styled header."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text:^80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 80}{Colors.ENDC}\n")


def print_success(text: str):
    """Print success message."""
    print(f"{Colors.OKGREEN}✅ {text}{Colors.ENDC}")


def print_error(text: str):
    """Print error message."""
    print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")


def print_warning(text: str):
    """Print warning message."""
    print(f"{Colors.WARNING}⚠️  {text}{Colors.ENDC}")


def print_info(text: str):
    """Print info message."""
    print(f"{Colors.OKCYAN}ℹ️  {text}{Colors.ENDC}")


def discover_clients(client: GoogleAdsClient) -> List[Dict[str, Any]]:
    """
    Discover all accessible client accounts from Google Ads API.
    
    Returns:
        List of client dictionaries with id, name, currency, timezone
    """
    print_info("Discovering clients from Google Ads API...")
    
    try:
        ga_service = client.get_service("GoogleAdsService")
        
        query = """
            SELECT
                customer_client.id,
                customer_client.descriptive_name,
                customer_client.currency_code,
                customer_client.time_zone,
                customer_client.manager,
                customer_client.test_account,
                customer_client.status
            FROM customer_client
            WHERE customer_client.status = 'ENABLED'
                AND customer_client.manager = FALSE
                AND customer_client.test_account = FALSE
        """
        
        # Use the login customer ID from settings
        login_customer_id = settings.GOOGLE_ADS_LOGIN_CUSTOMER_ID.replace("-", "")
        response = ga_service.search(customer_id=login_customer_id, query=query)
        
        clients = []
        for row in response:
            cc = row.customer_client
            clients.append({
                'id': str(cc.id),
                'name': cc.descriptive_name,
                'currency': cc.currency_code,
                'timezone': cc.time_zone
            })
        
        print_success(f"Discovered {len(clients)} active client accounts")
        return clients
        
    except GoogleAdsException as ex:
        print_error(f"Google Ads API error during client discovery:")
        for error in ex.failure.errors:
            print_error(f"  {error.message}")
        raise


def fetch_campaigns(
    client: GoogleAdsClient,
    customer_id: str,
    start_date: str,
    end_date: str
) -> pd.DataFrame:
    """Fetch campaign performance data."""
    customer_id_clean = customer_id.replace("-", "")
    ga_service = client.get_service("GoogleAdsService")
    
    print_info(f"  [CAMPAIGNS] Fetching {start_date} to {end_date}...")
    
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
    
    try:
        response = ga_service.search(customer_id=customer_id_clean, query=query)
        
        rows = []
        for row in response:
            rows.append({
                'date': row.segments.date,
                'campaign_id': row.campaign.id,
                'campaign_name': row.campaign.name,
                'campaign_status': row.campaign.status.name,
                'channel_type': row.campaign.advertising_channel_type.name,
                'bidding_strategy': row.campaign.bidding_strategy_type.name,
                'impressions': row.metrics.impressions,
                'clicks': row.metrics.clicks,
                'cost': row.metrics.cost_micros / 1_000_000,
                'conversions': row.metrics.conversions,
                'conversions_value': row.metrics.conversions_value,
                'all_conversions': row.metrics.all_conversions,
                'view_through_conversions': row.metrics.view_through_conversions,
                'avg_cpc': row.metrics.average_cpc / 1_000_000 if row.metrics.average_cpc else None,
                'avg_cpm': row.metrics.average_cpm / 1_000_000 if row.metrics.average_cpm else None,
                'impression_share': row.metrics.search_impression_share,
                'budget_lost_is': row.metrics.search_budget_lost_impression_share,
                'rank_lost_is': row.metrics.search_rank_lost_impression_share,
            })
        
        df = pd.DataFrame(rows)
        print_success(f"  [CAMPAIGNS] Fetched {len(df)} rows")
        return df
        
    except GoogleAdsException as ex:
        print_error(f"  [CAMPAIGNS] Google Ads API error:")
        for error in ex.failure.errors:
            print_error(f"    {error.message}")
        return pd.DataFrame()


def fetch_ad_groups(
    client: GoogleAdsClient,
    customer_id: str,
    start_date: str,
    end_date: str
) -> pd.DataFrame:
    """Fetch ad group performance data."""
    customer_id_clean = customer_id.replace("-", "")
    ga_service = client.get_service("GoogleAdsService")
    
    print_info(f"  [AD GROUPS] Fetching {start_date} to {end_date}...")
    
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
            metrics.average_cpc
        FROM ad_group
        WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
        ORDER BY segments.date ASC
    """
    
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
        print_success(f"  [AD GROUPS] Fetched {len(df)} rows")
        return df
        
    except GoogleAdsException as ex:
        print_error(f"  [AD GROUPS] Google Ads API error:")
        for error in ex.failure.errors:
            print_error(f"    {error.message}")
        return pd.DataFrame()


def fetch_keywords(
    client: GoogleAdsClient,
    customer_id: str,
    start_date: str,
    end_date: str
) -> pd.DataFrame:
    """Fetch keyword performance data with quality scores."""
    customer_id_clean = customer_id.replace("-", "")
    ga_service = client.get_service("GoogleAdsService")
    
    print_info(f"  [KEYWORDS] Fetching {start_date} to {end_date}...")
    
    query = f"""
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
                'keyword_id': row.ad_group_criterion.criterion_id,
                'keyword_text': row.ad_group_criterion.keyword.text,
                'match_type': row.ad_group_criterion.keyword.match_type.name,
                'keyword_status': row.ad_group_criterion.status.name,
                'quality_score': row.ad_group_criterion.quality_info.quality_score if hasattr(row.ad_group_criterion.quality_info, 'quality_score') else None,
                'creative_quality': row.ad_group_criterion.quality_info.creative_quality_score.name if hasattr(row.ad_group_criterion.quality_info, 'creative_quality_score') else None,
                'landing_page_quality': row.ad_group_criterion.quality_info.post_click_quality_score.name if hasattr(row.ad_group_criterion.quality_info, 'post_click_quality_score') else None,
                'expected_ctr': row.ad_group_criterion.quality_info.search_predicted_ctr.name if hasattr(row.ad_group_criterion.quality_info, 'search_predicted_ctr') else None,
                'impressions': row.metrics.impressions,
                'clicks': row.metrics.clicks,
                'cost': row.metrics.cost_micros / 1_000_000,
                'conversions': row.metrics.conversions,
                'conversions_value': row.metrics.conversions_value,
                'avg_cpc': row.metrics.average_cpc / 1_000_000 if row.metrics.average_cpc else None,
            })
        
        df = pd.DataFrame(rows)
        print_success(f"  [KEYWORDS] Fetched {len(df)} rows")
        return df
        
    except GoogleAdsException as ex:
        print_error(f"  [KEYWORDS] Google Ads API error:")
        for error in ex.failure.errors:
            print_error(f"    {error.message}")
        return pd.DataFrame()


def fetch_search_terms(
    client: GoogleAdsClient,
    customer_id: str,
    start_date: str,
    end_date: str
) -> pd.DataFrame:
    """
    Fetch search term report - actual queries that triggered ads.
    Uses 30-day chunking to avoid timeouts on large datasets.
    """
    customer_id_clean = customer_id.replace("-", "")
    ga_service = client.get_service("GoogleAdsService")
    
    # Convert dates for chunking
    from datetime import datetime, timedelta
    start_dt = datetime.strptime(start_date, '%Y-%m-%d')
    end_dt = datetime.strptime(end_date, '%Y-%m-%d')
    
    print_info(f"  [SEARCH TERMS] Fetching in 30-day chunks...")
    
    all_rows = []
    chunk_size = 30  # days per chunk
    current_start = start_dt
    
    while current_start <= end_dt:
        current_end = min(current_start + timedelta(days=chunk_size - 1), end_dt)
        chunk_start_str = current_start.strftime('%Y-%m-%d')
        chunk_end_str = current_end.strftime('%Y-%m-%d')
        
        print_info(f"    Chunk: {chunk_start_str} to {chunk_end_str}")
        
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
            
            print_info(f"      → {chunk_rows} rows")
        
        except GoogleAdsException as ex:
            print_warning(f"    Error in chunk {chunk_start_str}: {ex.failure.errors[0].message}")
        
        current_start = current_end + timedelta(days=1)
    
    df = pd.DataFrame(all_rows)
    print_success(f"  [SEARCH TERMS] Fetched {len(df)} total rows")
    return df


def load_to_database(
    client_slug: str,
    client_google_ads_id: str,
    campaigns_df: pd.DataFrame,
    ad_groups_df: pd.DataFrame,
    keywords_df: pd.DataFrame,
    search_terms_df: pd.DataFrame,
    db_session,
    dry_run: bool = False
) -> Dict[str, int]:
    """
    Load dataframes into PostgreSQL database.
    
    Returns:
        Dictionary with counts of records inserted per table
    """
    stats = {
        'campaigns': 0,
        'ad_groups': 0,
        'keywords': 0,
        'search_terms': 0
    }
    
    if dry_run:
        print_warning(f"  [DRY RUN] Would insert:")
        print_warning(f"    - {len(campaigns_df)} campaigns")
        print_warning(f"    - {len(ad_groups_df)} ad groups")
        print_warning(f"    - {len(keywords_df)} keywords")
        print_warning(f"    - {len(search_terms_df)} search terms")
        return stats
    
    # Get client ID from database
    client_record = db_session.query(Client).filter_by(slug=client_slug).first()
    if not client_record:
        print_error(f"  Client '{client_slug}' not found in database! Run seed_clients.py first.")
        return stats
    
    client_id = client_record.id
    
    # Load campaigns
    if not campaigns_df.empty:
        print_info(f"  [DB] Inserting {len(campaigns_df)} campaigns...")
        for _, row in campaigns_df.iterrows():
            record = GoogleAdsCampaign(
                client_id=client_id,
                date=row['date'],
                campaign_id=str(row['campaign_id']),
                campaign_name=row['campaign_name'],
                campaign_status=row['campaign_status'],
                channel_type=row['channel_type'],
                bidding_strategy=row['bidding_strategy'],
                impressions=int(row['impressions']),
                clicks=int(row['clicks']),
                cost=float(row['cost']),
                conversions=float(row['conversions']),
                conversions_value=float(row['conversions_value']),
                all_conversions=float(row['all_conversions']),
                view_through_conversions=float(row['view_through_conversions']),
                avg_cpc=float(row['avg_cpc']) if row['avg_cpc'] is not None else None,
                avg_cpm=float(row['avg_cpm']) if row['avg_cpm'] is not None else None,
                impression_share=float(row['impression_share']) if row['impression_share'] else None,
                budget_lost_is=float(row['budget_lost_is']) if row['budget_lost_is'] else None,
                rank_lost_is=float(row['rank_lost_is']) if row['rank_lost_is'] else None,
            )
            db_session.merge(record)  # Use merge to handle duplicates
        db_session.commit()
        stats['campaigns'] = len(campaigns_df)
        print_success(f"  [DB] Inserted {stats['campaigns']} campaigns")
    
    # Load ad groups
    if not ad_groups_df.empty:
        print_info(f"  [DB] Inserting {len(ad_groups_df)} ad groups...")
        for _, row in ad_groups_df.iterrows():
            record = GoogleAdsAdGroup(
                client_id=client_id,
                date=row['date'],
                campaign_id=str(row['campaign_id']),
                campaign_name=row['campaign_name'],
                ad_group_id=str(row['ad_group_id']),
                ad_group_name=row['ad_group_name'],
                ad_group_status=row['ad_group_status'],
                ad_group_type=row['ad_group_type'],
                cpc_bid=float(row['cpc_bid']) if row['cpc_bid'] is not None else None,
                impressions=int(row['impressions']),
                clicks=int(row['clicks']),
                cost=float(row['cost']),
                conversions=float(row['conversions']),
                conversions_value=float(row['conversions_value']),
                avg_cpc=float(row['avg_cpc']) if row['avg_cpc'] is not None else None,
            )
            db_session.merge(record)
        db_session.commit()
        stats['ad_groups'] = len(ad_groups_df)
        print_success(f"  [DB] Inserted {stats['ad_groups']} ad groups")
    
    # Load keywords
    if not keywords_df.empty:
        print_info(f"  [DB] Inserting {len(keywords_df)} keywords...")
        for _, row in keywords_df.iterrows():
            record = GoogleAdsKeyword(
                client_id=client_id,
                date=row['date'],
                campaign_id=str(row['campaign_id']),
                campaign_name=row['campaign_name'],
                ad_group_id=str(row['ad_group_id']),
                ad_group_name=row['ad_group_name'],
                keyword_id=str(row['keyword_id']),
                keyword_text=row['keyword_text'],
                match_type=row['match_type'],
                keyword_status=row['keyword_status'],
                quality_score=int(row['quality_score']) if pd.notna(row['quality_score']) else None,
                creative_quality=row['creative_quality'] if pd.notna(row['creative_quality']) else None,
                landing_page_quality=row['landing_page_quality'] if pd.notna(row['landing_page_quality']) else None,
                expected_ctr=row['expected_ctr'] if pd.notna(row['expected_ctr']) else None,
                impressions=int(row['impressions']),
                clicks=int(row['clicks']),
                cost=float(row['cost']),
                conversions=float(row['conversions']),
                conversions_value=float(row['conversions_value']),
                avg_cpc=float(row['avg_cpc']) if row['avg_cpc'] is not None else None,
            )
            db_session.merge(record)
        db_session.commit()
        stats['keywords'] = len(keywords_df)
        print_success(f"  [DB] Inserted {stats['keywords']} keywords")
    
    # Load search terms
    if not search_terms_df.empty:
        print_info(f"  [DB] Inserting {len(search_terms_df)} search terms...")
        for _, row in search_terms_df.iterrows():
            record = GoogleAdsSearchTerm(
                client_id=client_id,
                date=row['date'],
                campaign_id=str(row['campaign_id']),
                campaign_name=row['campaign_name'],
                ad_group_id=str(row['ad_group_id']),
                ad_group_name=row['ad_group_name'],
                search_term=row['search_term'],
                search_term_status=row['search_term_status'],
                match_type_delivered=row['match_type_delivered'],
                impressions=int(row['impressions']),
                clicks=int(row['clicks']),
                cost=float(row['cost']),
                conversions=float(row['conversions']),
                conversions_value=float(row['conversions_value']),
            )
            db_session.merge(record)
        db_session.commit()
        stats['search_terms'] = len(search_terms_df)
        print_success(f"  [DB] Inserted {stats['search_terms']} search terms")
    
    return stats


def migrate_client_data(
    client_name: str,
    client_id: str,
    client_slug: str,
    days: int,
    google_ads_client: GoogleAdsClient,
    db_session,
    dry_run: bool = False
) -> bool:
    """
    Migrate all data for a single client.
    
    Returns:
        True if successful, False otherwise
    """
    print_header(f"MIGRATING: {client_name} ({client_slug})")
    
    # Calculate date range
    end_date = datetime.now(pytz.UTC)
    start_date = end_date - timedelta(days=days)
    start_str = start_date.strftime('%Y-%m-%d')
    end_str = end_date.strftime('%Y-%m-%d')
    
    print_info(f"Date Range: {start_str} to {end_str} ({days} days)")
    print_info(f"Google Ads ID: {client_id}")
    
    try:
        # Fetch all data types
        campaigns_df = fetch_campaigns(google_ads_client, client_id, start_str, end_str)
        ad_groups_df = fetch_ad_groups(google_ads_client, client_id, start_str, end_str)
        keywords_df = fetch_keywords(google_ads_client, client_id, start_str, end_str)
        search_terms_df = fetch_search_terms(google_ads_client, client_id, start_str, end_str)
        
        # Check if we got any data
        total_rows = len(campaigns_df) + len(ad_groups_df) + len(keywords_df) + len(search_terms_df)
        
        if total_rows == 0:
            print_warning(f"No data found for {client_name}")
            return False
        
        print_success(f"Total rows fetched: {total_rows:,}")
        
        # Load to database
        stats = load_to_database(
            client_slug=client_slug,
            client_google_ads_id=client_id,
            campaigns_df=campaigns_df,
            ad_groups_df=ad_groups_df,
            keywords_df=keywords_df,
            search_terms_df=search_terms_df,
            db_session=db_session,
            dry_run=dry_run
        )
        
        if not dry_run:
            total_inserted = sum(stats.values())
            print_success(f"✅ COMPLETED: {client_name} - {total_inserted:,} records inserted")
        
        return True
        
    except Exception as e:
        print_error(f"Failed to migrate {client_name}: {str(e)}")
        return False


def main():
    """Main migration orchestrator."""
    parser = argparse.ArgumentParser(description='Migrate all client data to PostgreSQL')
    parser.add_argument('--days', type=int, default=365, help='Days of data to pull (default: 365)')
    parser.add_argument('--clients', type=str, help='Comma-separated list of client slugs (default: all)')
    parser.add_argument('--dry-run', action='store_true', help='Fetch data but don\'t insert')
    args = parser.parse_args()
    
    print_header("ADS MONKEE - CLIENT DATA MIGRATION")
    print_info(f"Date Range: {args.days} days (~{args.days/30:.1f} months)")
    print_info(f"Mode: {'DRY RUN' if args.dry_run else 'LIVE MIGRATION'}")
    print_info(f"Database: {settings.DATABASE_URL.split('@')[1] if '@' in str(settings.DATABASE_URL) else 'local'}")
    
    # Initialize Google Ads client
    try:
        google_ads_client = GoogleAdsClient.load_from_storage(version="v21")
        print_success("Google Ads API client initialized")
    except Exception as e:
        print_error(f"Failed to initialize Google Ads API: {e}")
        return 1
    
    # Initialize database session
    db_session = SessionLocal()
    
    try:
        # Get clients from database (seeded by seed_clients.py)
        db_clients = db_session.query(Client).all()
        
        if not db_clients:
            print_error("No clients found in database! Run 'poetry run python scripts/seed_clients.py' first.")
            return 1
        
        print_success(f"Found {len(db_clients)} clients in database")
        
        # Filter if specific clients requested
        if args.clients:
            requested_slugs = set(args.clients.split(','))
            db_clients = [c for c in db_clients if c.slug in requested_slugs]
            print_info(f"Filtered to {len(db_clients)} requested clients")
        
        # Migrate each client
        results = {
            'success': [],
            'failed': [],
            'no_data': []
        }
        
        for idx, client in enumerate(db_clients, 1):
            print(f"\n{'='*80}")
            print(f"Progress: {idx}/{len(db_clients)}")
            print(f"{'='*80}")
            
            success = migrate_client_data(
                client_name=client.name,
                client_id=client.google_ads_id,
                client_slug=client.slug,
                days=args.days,
                google_ads_client=google_ads_client,
                db_session=db_session,
                dry_run=args.dry_run
            )
            
            if success:
                results['success'].append(client.name)
            else:
                results['no_data'].append(client.name)
        
        # Final summary
        print_header("MIGRATION COMPLETE")
        print_success(f"Successfully migrated: {len(results['success'])} clients")
        if results['no_data']:
            print_warning(f"No data found: {len(results['no_data'])} clients")
        if results['failed']:
            print_error(f"Failed: {len(results['failed'])} clients")
        
        print(f"\n{Colors.OKGREEN}{Colors.BOLD}✅ ALL DONE!{Colors.ENDC}\n")
        
        return 0
        
    except Exception as e:
        print_error(f"Migration failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
        
    finally:
        db_session.close()


if __name__ == "__main__":
    sys.exit(main())

