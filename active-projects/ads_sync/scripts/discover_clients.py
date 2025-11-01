#!/usr/bin/env python3
"""
discover_clients.py - Dynamically discover all accessible Google Ads accounts from MCC

This script queries the Google Ads API to get all customer accounts accessible
through the MCC (Manager Account) and creates/updates client configuration files.

Usage:
    python scripts/discover_clients.py
    python scripts/discover_clients.py --export clients.csv
    python scripts/discover_clients.py --create-configs

Author: OneClickSEO PPC Management
Version: 0.1.0
"""

import argparse
import csv
import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Any

# Add parent directory to path to import google.ads
sys.path.insert(0, str(Path(__file__).parent.parent))

from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
import yaml


BASE_DIR = Path(__file__).resolve().parent.parent
CONFIGS_DIR = BASE_DIR / "configs" / "clients"
GOOGLE_ADS_YAML = BASE_DIR / "google-ads.yaml"


def slugify(text: str) -> str:
    """Convert a client name to a URL-friendly slug."""
    # Convert to lowercase
    text = text.lower()
    # Replace spaces and special chars with hyphens
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    # Remove leading/trailing hyphens
    return text.strip('-')


def get_accessible_customers(client: GoogleAdsClient, mcc_id: str) -> List[Dict[str, Any]]:
    """
    Query Google Ads API to get all accessible customer accounts.
    
    Args:
        client: GoogleAdsClient instance
        mcc_id: Manager account ID (MCC)
    
    Returns:
        List of customer account dictionaries with details
    """
    customer_service = client.get_service("CustomerService")
    
    # Get accessible customers
    accessible_customers = customer_service.list_accessible_customers()
    resource_names = accessible_customers.resource_names
    
    customers = []
    ga_service = client.get_service("GoogleAdsService")
    
    # Query from the MCC account to get all client details
    query = """
        SELECT
            customer_client.id,
            customer_client.descriptive_name,
            customer_client.status,
            customer_client.currency_code,
            customer_client.time_zone,
            customer_client.manager,
            customer_client.test_account
        FROM customer_client
        WHERE customer_client.status = 'ENABLED'
    """
    
    try:
        # Query from MCC to get all client accounts
        response = ga_service.search(customer_id=mcc_id, query=query)
        
        for row in response:
            customer = row.customer_client
            
            # Skip manager accounts (we only want client accounts)
            if customer.manager:
                continue
            
            # Skip test accounts
            if customer.test_account:
                continue
            
            # Extract customer ID
            customer_id = str(customer.id)
            
            # Format customer ID with hyphens (e.g., 123-456-7890)
            formatted_id = f"{customer_id[:3]}-{customer_id[3:6]}-{customer_id[6:]}"
            
            customers.append({
                'customer_id': formatted_id,
                'customer_id_raw': customer_id,
                'name': customer.descriptive_name or f"Customer {formatted_id}",
                'status': customer.status.name,
                'currency_code': customer.currency_code or 'USD',
                'time_zone': customer.time_zone or 'America/Chicago',
                'slug': slugify(customer.descriptive_name or f"customer-{formatted_id}")
            })
    
    except GoogleAdsException as ex:
        print(f"[ERROR] Could not query MCC for clients:", file=sys.stderr)
        for error in ex.failure.errors:
            print(f"  {error.message}", file=sys.stderr)
        raise
    
    return customers


def export_to_csv(customers: List[Dict[str, Any]], output_path: Path):
    """Export customer list to CSV file."""
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['customer_id', 'name', 'status', 'currency_code', 'time_zone', 'slug'])
        writer.writeheader()
        writer.writerows(customers)
    
    print(f"[OK] Exported {len(customers)} customers to {output_path}")


def create_config_file(customer: Dict[str, Any], configs_dir: Path) -> bool:
    """
    Create a YAML configuration file for a customer.
    
    Args:
        customer: Customer details dictionary
        configs_dir: Directory to save config files
    
    Returns:
        True if created, False if skipped (already exists)
    """
    config_path = configs_dir / f"{customer['slug']}.yaml"
    
    # Skip if config already exists
    if config_path.exists():
        return False
    
    config = {
        'client_id': customer['customer_id'],
        'client_name': customer['name'],
        'time_zone': customer['time_zone'],
        'currency_code': customer['currency_code'],
        'data_sources': {
            'google_ads': {
                'enabled': True,
                'mcc_id': None,  # Will use login_customer_id from google-ads.yaml
            },
            'google_lsa': {
                'enabled': False,
                'import_method': 'csv'
            }
        },
        'reporting': {
            'default_template': 'campaign_report.md.j2',
            'default_scope': 'LAST-30-DAYS'
        }
    }
    
    # Create config file
    configs_dir.mkdir(parents=True, exist_ok=True)
    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)
    
    return True


def main():
    parser = argparse.ArgumentParser(
        description='Discover all accessible Google Ads accounts from MCC'
    )
    parser.add_argument(
        '--export',
        type=str,
        metavar='FILE',
        help='Export customer list to CSV file'
    )
    parser.add_argument(
        '--create-configs',
        action='store_true',
        help='Create YAML config files for all discovered customers'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output results as JSON'
    )
    
    args = parser.parse_args()
    
    # Initialize Google Ads client
    try:
        client = GoogleAdsClient.load_from_storage(str(GOOGLE_ADS_YAML))
        mcc_id = client.login_customer_id
    except Exception as e:
        print(f"[ERROR] Failed to initialize Google Ads client: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Discover customers
    print(f"\n[DISCOVERY] Querying Google Ads API for accessible accounts...")
    print(f"[DISCOVERY] MCC ID: {mcc_id}\n")
    
    try:
        customers = get_accessible_customers(client, mcc_id)
    except GoogleAdsException as ex:
        print(f"\n[ERROR] Google Ads API error:", file=sys.stderr)
        for error in ex.failure.errors:
            print(f"  Error: {error.message}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)
    
    if not customers:
        print("[WARN] No accessible customer accounts found.")
        sys.exit(0)
    
    # Sort by name
    customers.sort(key=lambda x: x['name'])
    
    print(f"[OK] Found {len(customers)} accessible customer accounts\n")
    print("=" * 100)
    
    # Output format
    if args.json:
        import json
        print(json.dumps(customers, indent=2))
    else:
        # Print table
        print(f"{'Customer ID':<15} {'Name':<40} {'Status':<10} {'Slug':<30}")
        print("-" * 100)
        for c in customers:
            print(f"{c['customer_id']:<15} {c['name']:<40} {c['status']:<10} {c['slug']:<30}")
    
    print("=" * 100)
    
    # Export to CSV
    if args.export:
        export_to_csv(customers, Path(args.export))
    
    # Create config files
    if args.create_configs:
        print(f"\n[SETUP] Creating config files for {len(customers)} customers...")
        created = 0
        skipped = 0
        
        for customer in customers:
            if create_config_file(customer, CONFIGS_DIR):
                print(f"[OK] Created: {customer['slug']}")
                created += 1
            else:
                print(f"[SKIP] Already exists: {customer['slug']}")
                skipped += 1
        
        print("\n" + "=" * 60)
        print("[SUMMARY]")
        print("=" * 60)
        print(f"Total Customers:  {len(customers)}")
        print(f"Created:          {created}")
        print(f"Skipped:          {skipped}")
        print("=" * 60)
        print(f"\n[OK] Config files location: {CONFIGS_DIR}\n")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

