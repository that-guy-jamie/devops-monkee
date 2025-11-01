#!/usr/bin/env python3
"""
Test Google Ads API Connection
================================

Simple script to test if the Google Ads API is working correctly.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from google.ads.googleads.client import GoogleAdsClient

# Path to google-ads.yaml
GOOGLE_ADS_YAML = Path(__file__).parent.parent.parent / "ads_sync" / "google-ads.yaml"

def test_api_connection():
    """Test basic API connection."""
    print("="*80)
    print("TESTING GOOGLE ADS API CONNECTION")
    print("="*80)
    
    try:
        # Load client
        print(f"\n[1] Loading client from {GOOGLE_ADS_YAML}...")
        client = GoogleAdsClient.load_from_storage(str(GOOGLE_ADS_YAML))
        print("    [OK] Client loaded successfully")
        
        # Get service
        print("\n[2] Getting GoogleAdsService...")
        service = client.get_service("GoogleAdsService")
        print("    [OK] Service created successfully")
        
        # First, let's list accessible customers to verify access
        print("\n[3] Listing accessible customers...")
        customer_service = client.get_service("CustomerService")
        accessible_customers = customer_service.list_accessible_customers()
        
        print(f"    Accessible customer IDs:")
        for customer_resource_name in accessible_customers.resource_names:
            customer_id_from_resource = customer_resource_name.split('/')[-1]
            print(f"      - {customer_id_from_resource}")
        
        # Test query with the first accessible customer
        if accessible_customers.resource_names:
            test_customer_id = accessible_customers.resource_names[0].split('/')[-1]
            print(f"\n[4] Testing query for customer {test_customer_id}...")
            
            query = """
                SELECT
                    campaign.id,
                    campaign.name,
                    campaign.status
                FROM campaign
                WHERE campaign.status = 'ENABLED'
                LIMIT 5
            """
            
            print(f"    Query: {query.strip()}")
            
            response = service.search(customer_id=test_customer_id, query=query)
            
            print("\n    [OK] Query executed successfully!")
            print("\n    Results:")
            for row in response:
                print(f"      - Campaign ID: {row.campaign.id}")
                print(f"        Name: {row.campaign.name}")
                print(f"        Status: {row.campaign.status.name}")
                print()
        else:
            print("    [WARNING] No accessible customers found!")
        
        print("="*80)
        print("API CONNECTION TEST: SUCCESS")
        print("="*80)
        
    except Exception as e:
        print(f"\n    [ERROR] {type(e).__name__}: {e}")
        print("\n" + "="*80)
        print("API CONNECTION TEST: FAILED")
        print("="*80)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    test_api_connection()

