#!/usr/bin/env python3
"""
Verify that the parallel campaign was actually created and check its status.
"""
import sys
from pathlib import Path

# Ensure project root on path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.integrations.google_ads_client import GoogleAdsWrapper

def verify_campaign_exists(customer_id: str, campaign_resource_name: str):
    """Verify that the campaign exists and check its details."""
    wrapper = GoogleAdsWrapper()

    try:
        print(f"Verifying campaign exists: {campaign_resource_name}")

        # Check if campaign exists
        snapshot = wrapper.get_campaign_snapshot(customer_id, campaign_resource_name)

        print("Campaign verification results:")
        print(f"  Name: {snapshot.name}")
        print(f"  Status: {snapshot.status}")
        print(f"  Daily Budget: ${snapshot.daily_budget_micros / 1_000_000:.2f}")
        print(f"  Bidding Strategy: {snapshot.bidding_strategy_type}")
        print(f"  Advertising Channel: {snapshot.advertising_channel_type}")

        return True

    except Exception as e:
        print(f"Campaign verification failed: {e}")
        return False

def check_priority_campaigns(customer_id: str):
    """List all campaigns for Priority Roofing to see what's there."""
    wrapper = GoogleAdsWrapper()

    try:
        print(f"\nListing all campaigns for customer {customer_id}...")

        service = wrapper._ga_service()
        query = """
        SELECT campaign.id, campaign.name, campaign.status, campaign_budget.amount_micros
        FROM campaign
        WHERE campaign.name LIKE '%Roofing%'
        ORDER BY campaign.id DESC
        """

        response = service.search(customer_id=customer_id, query=query)

        campaigns = []
        for row in response:
            campaigns.append({
                'id': str(row.campaign.id),
                'name': row.campaign.name,
                'status': row.campaign.status.name,
                'budget_micros': int(row.campaign_budget.amount_micros) if row.campaign_budget else 0
            })

        if campaigns:
            print(f"Found {len(campaigns)} Roofing campaigns:")
            for i, campaign in enumerate(campaigns, 1):
                print(f"{i}. ID: {campaign['id']}")
                print(f"   Name: {campaign['name']}")
                print(f"   Status: {campaign['status']}")
                print(f"   Budget: ${campaign['budget_micros'] / 1_000_000:.2f}")
                print()
        else:
            print("No Roofing campaigns found.")

        return campaigns

    except Exception as e:
        print(f"Error listing campaigns: {e}")
        return []

def main():
    customer_id = "4139022884"  # Correct Priority Roofing customer ID

    print("=" * 60)
    print("CAMPAIGN CREATION VERIFICATION")
    print("=" * 60)

    # List all Roofing campaigns to find what exists
    all_campaigns = check_priority_campaigns(customer_id)
    
    # Check if the parallel campaign exists
    campaign_exists = False
    if all_campaigns:
        for campaign in all_campaigns:
            if "Parallel" in campaign['name']:
                expected_campaign = f"customers/{customer_id}/campaigns/{campaign['id']}"
                campaign_exists = verify_campaign_exists(customer_id, expected_campaign)
                break

    print("=" * 60)
    if campaign_exists:
        print("VERIFICATION PASSED!")
        print("The parallel campaign exists and is accessible via API.")
        print("Note: It might take a few minutes to appear in the Google Ads UI.")
    else:
        print("VERIFICATION FAILED!")
        print("The campaign creation might not have succeeded.")
        print("Check the API response and Google Ads dashboard.")

    print("=" * 60)

if __name__ == "__main__":
    main()
