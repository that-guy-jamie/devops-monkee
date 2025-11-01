#!/usr/bin/env python3
"""
Delete the incorrectly created campaign in Sunlight Contractors' account.
"""
import sys
from pathlib import Path

# Ensure project root on path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.integrations.google_ads_client import GoogleAdsWrapper

def delete_campaign(customer_id: str, campaign_resource_name: str):
    """Delete a campaign."""
    wrapper = GoogleAdsWrapper()

    try:
        print(f"Deleting campaign: {campaign_resource_name}")

        # Delete the campaign using the correct API pattern
        campaign_service = wrapper._campaign_service()
        operation = wrapper.client.get_type("CampaignOperation")
        operation.remove = campaign_resource_name

        campaign_service.mutate_campaigns(
            customer_id=customer_id, operations=[operation]
        )

        print("Campaign deleted successfully!")
        return True

    except Exception as e:
        print(f"Error deleting campaign: {e}")
        return False

def main():
    # Sunlight Contractors account and campaign to delete
    customer_id = "9390713365"
    campaign_resource_name = "customers/9390713365/campaigns/23164101092"

    print("=" * 60)
    print("DELETE SUNLIGHT CONTRACTORS CAMPAIGN")
    print("=" * 60)
    print(f"Target Account: Sunlight Contractors (ID: {customer_id})")
    print(f"Campaign to Delete: {campaign_resource_name}")
    print()

    success = delete_campaign(customer_id, campaign_resource_name)

    print()
    print("=" * 60)
    if success:
        print("DELETION SUCCESSFUL!")
        print("Incorrectly created campaign has been removed.")
    else:
        print("DELETION FAILED!")
        print("Campaign deletion encountered an error.")
    print("=" * 60)

if __name__ == "__main__":
    main()
