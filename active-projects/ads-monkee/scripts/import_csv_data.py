#!/usr/bin/env python3
"""
Import CSV Data from ads_sync
==============================

Imports existing comprehensive CSV data from ads_sync into PostgreSQL.
This bypasses the Google Ads API for initial data load.

Usage:
    poetry run python scripts/import_csv_data.py --client priority-roofing
    poetry run python scripts/import_csv_data.py --all
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import pandas as pd
from sqlalchemy import text
from sqlalchemy.orm import Session

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.database import sync_engine, SyncSessionLocal
from backend.models import (
    Client,
    ClientStatus,
    GoogleAdsCampaign,
    GoogleAdsAdGroup,
    GoogleAdsKeyword,
    GoogleAdsSearchTerm,
)

# Paths
ADS_SYNC_DATA = Path(__file__).parent.parent.parent / "ads_sync" / "data"


def get_or_create_client(db: Session, slug: str, name: str, google_ads_id: str) -> Client:
    """Get existing client or create new one."""
    client = db.query(Client).filter(Client.slug == slug).first()
    
    if not client:
        client = Client(
            name=name,
            slug=slug,
            google_ads_customer_id=google_ads_id,
            status=ClientStatus.ACTIVE,
        )
        db.add(client)
        db.flush()
        print(f"  [+] Created client: {name} (ID: {client.id})")
    else:
        print(f"  [*] Client exists: {name} (ID: {client.id})")
    
    return client


def import_campaigns(db: Session, client: Client, csv_path: Path) -> int:
    """Import campaign data from CSV."""
    print(f"  [DATA] Importing campaigns from {csv_path.name}...")
    
    df = pd.read_csv(csv_path)
    print(f"     Found {len(df)} rows")
    
    # Convert types
    df['date'] = pd.to_datetime(df['date']).dt.date
    df['campaign_id'] = df['campaign_id'].astype(str)
    
    # Add client_id
    df['client_id'] = client.id
    
    # Map CSV columns to model fields
    records = []
    for _, row in df.iterrows():
        record = GoogleAdsCampaign(
            client_id=client.id,
            date=row['date'],
            campaign_id=row['campaign_id'],
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
            avg_cpc=float(row['avg_cpc']) if pd.notna(row['avg_cpc']) else None,
            avg_cpm=float(row['avg_cpm']) if pd.notna(row['avg_cpm']) else None,
            impression_share=float(row['impression_share']) if pd.notna(row['impression_share']) else None,
            budget_lost_is=float(row['budget_lost_is']) if pd.notna(row['budget_lost_is']) else None,
            rank_lost_is=float(row['rank_lost_is']) if pd.notna(row['rank_lost_is']) else None,
        )
        records.append(record)
    
    # Bulk insert
    db.bulk_save_objects(records)
    db.commit()
    
    print(f"     [OK] Imported {len(records)} campaign records")
    return len(records)


def import_ad_groups(db: Session, client: Client, csv_path: Path) -> int:
    """Import ad group data from CSV."""
    print(f"  [DATA] Importing ad groups from {csv_path.name}...")
    
    df = pd.read_csv(csv_path)
    print(f"     Found {len(df)} rows")
    
    df['date'] = pd.to_datetime(df['date']).dt.date
    df['campaign_id'] = df['campaign_id'].astype(str)
    df['ad_group_id'] = df['ad_group_id'].astype(str)
    
    records = []
    for _, row in df.iterrows():
        record = GoogleAdsAdGroup(
            client_id=client.id,
            date=row['date'],
            campaign_id=row['campaign_id'],
            campaign_name=row['campaign_name'],
            ad_group_id=row['ad_group_id'],
            ad_group_name=row['ad_group_name'],
            ad_group_status=row['ad_group_status'],
            ad_group_type=row['ad_group_type'],
            cpc_bid=float(row['cpc_bid']) if pd.notna(row['cpc_bid']) else None,
            impressions=int(row['impressions']),
            clicks=int(row['clicks']),
            cost=float(row['cost']),
            conversions=float(row['conversions']),
            conversions_value=float(row['conversions_value']),
            avg_cpc=float(row['avg_cpc']) if pd.notna(row['avg_cpc']) else None,
        )
        records.append(record)
    
    db.bulk_save_objects(records)
    db.commit()
    
    print(f"     [OK] Imported {len(records)} ad group records")
    return len(records)


def import_keywords(db: Session, client: Client, csv_path: Path) -> int:
    """Import keyword data from CSV."""
    print(f"  [DATA] Importing keywords from {csv_path.name}...")
    
    df = pd.read_csv(csv_path)
    print(f"     Found {len(df)} rows")
    
    df['date'] = pd.to_datetime(df['date']).dt.date
    df['campaign_id'] = df['campaign_id'].astype(str)
    df['ad_group_id'] = df['ad_group_id'].astype(str)
    df['keyword_id'] = df['keyword_id'].astype(str)
    
    records = []
    for _, row in df.iterrows():
        record = GoogleAdsKeyword(
            client_id=client.id,
            date=row['date'],
            campaign_id=row['campaign_id'],
            campaign_name=row['campaign_name'],
            ad_group_id=row['ad_group_id'],
            ad_group_name=row['ad_group_name'],
            keyword_id=row['keyword_id'],
            keyword_text=row['keyword_text'],
            match_type=row['match_type'],
            keyword_status=row['keyword_status'],
            quality_score=int(row['quality_score']) if pd.notna(row['quality_score']) else None,
            creative_quality=row['creative_quality'] if pd.notna(row['creative_quality']) else None,
            landing_page_quality=row['landing_page_quality'] if pd.notna(row['landing_page_quality']) else None,
            expected_ctr=row['expected_ctr'] if pd.notna(row['expected_ctr']) else None,
            max_cpc_bid=float(row['max_cpc_bid']) if pd.notna(row['max_cpc_bid']) else None,
            final_url=row['final_url'] if pd.notna(row['final_url']) else None,
            impressions=int(row['impressions']),
            clicks=int(row['clicks']),
            cost=float(row['cost']),
            conversions=float(row['conversions']),
            conversions_value=float(row['conversions_value']),
            avg_cpc=float(row['avg_cpc']) if pd.notna(row['avg_cpc']) else None,
        )
        records.append(record)
    
    db.bulk_save_objects(records)
    db.commit()
    
    print(f"     [OK] Imported {len(records)} keyword records")
    return len(records)


def import_search_terms(db: Session, client: Client, csv_path: Path) -> int:
    """Import search term data from CSV."""
    print(f"  [DATA] Importing search terms from {csv_path.name}...")
    
    df = pd.read_csv(csv_path)
    print(f"     Found {len(df)} rows")
    
    df['date'] = pd.to_datetime(df['date']).dt.date
    df['campaign_id'] = df['campaign_id'].astype(str)
    df['ad_group_id'] = df['ad_group_id'].astype(str)
    
    records = []
    for _, row in df.iterrows():
        record = GoogleAdsSearchTerm(
            client_id=client.id,
            date=row['date'],
            campaign_id=row['campaign_id'],
            campaign_name=row['campaign_name'],
            ad_group_id=row['ad_group_id'],
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
        records.append(record)
    
    db.bulk_save_objects(records)
    db.commit()
    
    print(f"     [OK] Imported {len(records)} search term records")
    return len(records)


def import_client_data(client_slug: str, client_name: str, google_ads_id: str, clear_existing: bool = False):
    """Import all data for a single client."""
    print(f"\n{'='*80}")
    print(f"IMPORTING: {client_name}")
    print(f"{'='*80}")
    
    # Find comprehensive data directory
    client_data_dir = ADS_SYNC_DATA / client_slug / "comprehensive"
    
    if not client_data_dir.exists():
        print(f"  [ERROR] No data directory found: {client_data_dir}")
        return
    
    # Find latest CSV files
    campaign_files = sorted(client_data_dir.glob(f"{client_slug}-campaigns-*.csv"))
    ad_group_files = sorted(client_data_dir.glob(f"{client_slug}-ad_groups-*.csv"))
    keyword_files = sorted(client_data_dir.glob(f"{client_slug}-keywords-*.csv"))
    search_term_files = sorted(client_data_dir.glob(f"{client_slug}-search_terms-*.csv"))
    
    if not campaign_files:
        print(f"  [ERROR] No CSV files found in {client_data_dir}")
        return
    
    # Use latest files
    campaign_csv = campaign_files[-1]
    ad_group_csv = ad_group_files[-1] if ad_group_files else None
    keyword_csv = keyword_files[-1] if keyword_files else None
    search_term_csv = search_term_files[-1] if search_term_files else None
    
    print(f"  [DIR] Data directory: {client_data_dir}")
    print(f"  [DATE] Using files from: {campaign_csv.stem.split('-')[-1]}")
    
    # Import data
    db = SyncSessionLocal()
    try:
        # Get or create client
        client = get_or_create_client(db, client_slug, client_name, google_ads_id)
        
        # Clear existing data if requested
        if clear_existing:
            print(f"  [CLEAR] Deleting existing data for {client_name}...")
            db.query(GoogleAdsSearchTerm).filter(GoogleAdsSearchTerm.client_id == client.id).delete()
            db.query(GoogleAdsKeyword).filter(GoogleAdsKeyword.client_id == client.id).delete()
            db.query(GoogleAdsAdGroup).filter(GoogleAdsAdGroup.client_id == client.id).delete()
            db.query(GoogleAdsCampaign).filter(GoogleAdsCampaign.client_id == client.id).delete()
            db.commit()
            print(f"  [CLEAR] Existing data cleared")
        
        # Import each data type
        total_records = 0
        
        if campaign_csv.exists():
            total_records += import_campaigns(db, client, campaign_csv)
        
        if ad_group_csv and ad_group_csv.exists():
            total_records += import_ad_groups(db, client, ad_group_csv)
        
        if keyword_csv and keyword_csv.exists():
            total_records += import_keywords(db, client, keyword_csv)
        
        if search_term_csv and search_term_csv.exists():
            total_records += import_search_terms(db, client, search_term_csv)
        
        print(f"\n  [OK] TOTAL: {total_records:,} records imported for {client_name}")
        
    except Exception as e:
        print(f"  [ERROR] ERROR: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(description="Import CSV data from ads_sync")
    parser.add_argument("--client", help="Client slug (e.g., priority-roofing)")
    parser.add_argument("--all", action="store_true", help="Import all clients")
    parser.add_argument("--clear", action="store_true", help="Clear existing data before import")
    
    args = parser.parse_args()
    
    print("\n" + "="*80)
    print("CSV DATA IMPORT FROM ads_sync")
    print("="*80)
    
    # Known clients (expand as needed)
    clients = {
        "priority-roofing": {
            "name": "Priority Roofing",
            "google_ads_id": "4889386895",
        },
        "heather-murphy-group": {
            "name": "Heather Murphy Group",
            "google_ads_id": "7119071973",
        },
        "donaldson-educational-services": {
            "name": "Donaldson Educational Services",
            "google_ads_id": "7608255009",
        },
    }
    
    if args.client:
        if args.client not in clients:
            print(f"[ERROR] Unknown client: {args.client}")
            print(f"Known clients: {', '.join(clients.keys())}")
            sys.exit(1)
        
        client_info = clients[args.client]
        import_client_data(args.client, client_info["name"], client_info["google_ads_id"], args.clear)
    
    elif args.all:
        for slug, info in clients.items():
            try:
                import_client_data(slug, info["name"], info["google_ads_id"], args.clear)
            except Exception as e:
                print(f"[ERROR] Failed to import {slug}: {e}")
                continue
    
    else:
        print("[ERROR] Please specify --client <slug> or --all")
        sys.exit(1)
    
    print("\n" + "="*80)
    print("IMPORT COMPLETE")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()

