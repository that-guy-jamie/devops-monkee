#!/usr/bin/env python3
"""
backfill_historical_data.py - Backfill historical Google Ads data for long-term analysis

This script pulls 2-5 years of historical data for pattern discovery and trend analysis.
Data is stored separately from the active 1-year operational dataset.

Use Cases:
- Seasonal trend analysis (multi-year comparison)
- Long-term ROI patterns
- Discovery of "hidden gems" (keywords/campaigns that worked historically)
- Market shift detection (how performance changed over time)

Usage:
    # Backfill 2 years for all clients
    poetry run python scripts/backfill_historical_data.py --years 2
    
    # Backfill 5 years for specific client
    poetry run python scripts/backfill_historical_data.py --client priority-roofing --years 5
    
    # Dry run to see what would be pulled
    poetry run python scripts/backfill_historical_data.py --years 3 --dry-run

Storage:
    Historical data is marked with a 'historical' flag in the database to distinguish
    it from the active 1-year operational dataset used for campaign optimization.

Performance Notes:
    - Uses aggressive 90-day chunking for search terms
    - Estimated time: ~5-10 minutes per client per year
    - Total for 30 clients x 2 years: ~3-5 hours

Author: OneClickSEO - Ads Monkee
Version: 1.0.0
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any
import pandas as pd
import pytz
from sqlalchemy.orm import sessionmaker

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

# Import our models
from backend.models import Client
from backend.config import settings
from backend.database import SessionLocal

# Import fetch functions from migration script
from migrate_all_clients_data import (
    print_header,
    print_success,
    print_error,
    print_warning,
    print_info,
    fetch_campaigns,
    fetch_ad_groups,
    fetch_keywords,
    fetch_search_terms,
    load_to_database,
    Colors
)


def backfill_client_historical(
    client_name: str,
    client_id: str,
    client_slug: str,
    years: int,
    google_ads_client: GoogleAdsClient,
    db_session,
    dry_run: bool = False,
    exclude_recent_months: int = 12
) -> Dict[str, Any]:
    """
    Backfill historical data for a single client.
    
    Args:
        client_name: Client display name
        client_id: Google Ads customer ID
        client_slug: Client slug for database lookup
        years: Number of years of historical data to pull
        google_ads_client: Initialized Google Ads API client
        db_session: Database session
        dry_run: If True, fetch but don't insert
        exclude_recent_months: Don't pull data from last N months (already in operational dataset)
    
    Returns:
        Dictionary with stats: total_rows, campaigns, ad_groups, keywords, search_terms
    """
    print_header(f"BACKFILLING: {client_name} ({client_slug}) - {years} YEARS")
    
    # Calculate date range
    # End date: 12 months ago (don't overlap with operational dataset)
    end_date = datetime.now(pytz.UTC) - timedelta(days=exclude_recent_months * 30)
    
    # Start date: N years before end date
    start_date = end_date - timedelta(days=years * 365)
    
    start_str = start_date.strftime('%Y-%m-%d')
    end_str = end_date.strftime('%Y-%m-%d')
    
    print_info(f"Historical Range: {start_str} to {end_str}")
    print_info(f"Excluding recent: Last {exclude_recent_months} months (operational dataset)")
    print_info(f"Google Ads ID: {client_id}")
    
    stats = {
        'total_rows': 0,
        'campaigns': 0,
        'ad_groups': 0,
        'keywords': 0,
        'search_terms': 0
    }
    
    try:
        # Fetch all data types
        print_info("Fetching historical data (this may take several minutes)...")
        
        campaigns_df = fetch_campaigns(google_ads_client, client_id, start_str, end_str)
        ad_groups_df = fetch_ad_groups(google_ads_client, client_id, start_str, end_str)
        keywords_df = fetch_keywords(google_ads_client, client_id, start_str, end_str)
        search_terms_df = fetch_search_terms(google_ads_client, client_id, start_str, end_str)
        
        # Check if we got any data
        stats['campaigns'] = len(campaigns_df)
        stats['ad_groups'] = len(ad_groups_df)
        stats['keywords'] = len(keywords_df)
        stats['search_terms'] = len(search_terms_df)
        stats['total_rows'] = sum([stats['campaigns'], stats['ad_groups'], stats['keywords'], stats['search_terms']])
        
        if stats['total_rows'] == 0:
            print_warning(f"No historical data found for {client_name}")
            return stats
        
        print_success(f"Total historical rows fetched: {stats['total_rows']:,}")
        print_info(f"  Campaigns: {stats['campaigns']:,}")
        print_info(f"  Ad Groups: {stats['ad_groups']:,}")
        print_info(f"  Keywords: {stats['keywords']:,}")
        print_info(f"  Search Terms: {stats['search_terms']:,}")
        
        # Load to database
        load_stats = load_to_database(
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
            print_success(f"✅ BACKFILLED: {client_name} - {stats['total_rows']:,} historical records")
        
        return stats
        
    except Exception as e:
        print_error(f"Failed to backfill {client_name}: {str(e)}")
        import traceback
        traceback.print_exc()
        return stats


def main():
    """Main backfill orchestrator."""
    parser = argparse.ArgumentParser(description='Backfill historical client data for long-term analysis')
    parser.add_argument('--years', type=int, default=2, help='Years of historical data to pull (default: 2)')
    parser.add_argument('--client', type=str, help='Single client slug to backfill (default: all)')
    parser.add_argument('--exclude-recent', type=int, default=12, help='Exclude last N months (default: 12)')
    parser.add_argument('--dry-run', action='store_true', help='Fetch data but don\'t insert')
    args = parser.parse_args()
    
    print_header("ADS MONKEE - HISTORICAL DATA BACKFILL")
    print_info(f"Historical Period: {args.years} years")
    print_info(f"Excluding Recent: Last {args.exclude_recent} months (operational dataset)")
    print_info(f"Mode: {'DRY RUN' if args.dry_run else 'LIVE BACKFILL'}")
    
    # Warnings
    print_warning("⏰ This process may take several hours for 30 clients x multiple years")
    print_warning("💾 Ensure sufficient database storage for historical data")
    
    if not args.dry_run:
        confirm = input(f"\n{Colors.WARNING}Proceed with backfill? (yes/no): {Colors.ENDC}")
        if confirm.lower() != 'yes':
            print_info("Backfill cancelled by user")
            return 0
    
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
        # Get clients from database
        if args.client:
            db_clients = db_session.query(Client).filter_by(slug=args.client).all()
            if not db_clients:
                print_error(f"Client '{args.client}' not found in database")
                return 1
        else:
            db_clients = db_session.query(Client).all()
        
        if not db_clients:
            print_error("No clients found in database! Run 'poetry run python scripts/seed_clients.py' first.")
            return 1
        
        print_success(f"Found {len(db_clients)} clients to backfill")
        
        # Estimate time
        estimated_minutes = len(db_clients) * args.years * 7  # ~7 min per client-year
        print_info(f"Estimated time: ~{estimated_minutes} minutes ({estimated_minutes/60:.1f} hours)")
        
        # Backfill each client
        results = {
            'success': [],
            'no_data': [],
            'failed': []
        }
        
        grand_total_rows = 0
        
        for idx, client in enumerate(db_clients, 1):
            print(f"\n{'='*80}")
            print(f"{Colors.BOLD}Progress: {idx}/{len(db_clients)} ({idx/len(db_clients)*100:.1f}%){Colors.ENDC}")
            print(f"{'='*80}")
            
            stats = backfill_client_historical(
                client_name=client.name,
                client_id=client.google_ads_id,
                client_slug=client.slug,
                years=args.years,
                google_ads_client=google_ads_client,
                db_session=db_session,
                dry_run=args.dry_run,
                exclude_recent_months=args.exclude_recent
            )
            
            grand_total_rows += stats['total_rows']
            
            if stats['total_rows'] > 0:
                results['success'].append({
                    'name': client.name,
                    'rows': stats['total_rows']
                })
            elif stats['total_rows'] == 0:
                results['no_data'].append(client.name)
        
        # Final summary
        print_header("BACKFILL COMPLETE")
        print_success(f"Total historical records: {grand_total_rows:,}")
        print_success(f"Successfully backfilled: {len(results['success'])} clients")
        
        if results['success']:
            print(f"\n{Colors.OKGREEN}Top 10 clients by historical data volume:{Colors.ENDC}")
            sorted_clients = sorted(results['success'], key=lambda x: x['rows'], reverse=True)[:10]
            for i, client_info in enumerate(sorted_clients, 1):
                print(f"  {i:2d}. {client_info['name']}: {client_info['rows']:,} rows")
        
        if results['no_data']:
            print_warning(f"\nNo historical data: {len(results['no_data'])} clients")
            for name in results['no_data']:
                print(f"  - {name}")
        
        if results['failed']:
            print_error(f"\nFailed: {len(results['failed'])} clients")
        
        print(f"\n{Colors.OKGREEN}{Colors.BOLD}✅ HISTORICAL BACKFILL COMPLETE!{Colors.ENDC}\n")
        
        # Usage tips
        print_header("NEXT STEPS - HISTORICAL ANALYSIS")
        print_info("1. Run long-term trend analysis:")
        print(f"   {Colors.OKCYAN}poetry run python scripts/analyze_historical_trends.py --client priority-roofing{Colors.ENDC}")
        print_info("2. Discover historical winners:")
        print(f"   {Colors.OKCYAN}poetry run python scripts/find_historical_gems.py --min-roas 3.0{Colors.ENDC}")
        print_info("3. Compare seasonal patterns:")
        print(f"   {Colors.OKCYAN}poetry run python scripts/seasonal_analysis.py --years {args.years}{Colors.ENDC}")
        
        return 0
        
    except Exception as e:
        print_error(f"Backfill failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
        
    finally:
        db_session.close()


if __name__ == "__main__":
    sys.exit(main())

