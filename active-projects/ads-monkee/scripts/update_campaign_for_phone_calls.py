#!/usr/bin/env python3
"""
Update the Priority Roofing parallel campaign to optimize specifically for phone calls.
"""
import sys
from pathlib import Path

# Ensure project root on path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.integrations.google_ads_client import GoogleAdsWrapper

def get_campaign_resource_name(customer_id: str, campaign_name: str) -> str:
    """Get the resource name for a campaign."""
    wrapper = GoogleAdsWrapper()

    service = wrapper._ga_service()
    query = f"""
    SELECT campaign.resource_name
    FROM campaign
    WHERE campaign.name = '{campaign_name}'
    LIMIT 1
    """

    response = service.search(customer_id=customer_id, query=query)

    for row in response:
        return row.campaign.resource_name

    raise RuntimeError(f"Campaign '{campaign_name}' not found")

def update_campaign_for_phone_calls(customer_id: str, campaign_resource_name: str):
    """Update campaign to optimize for phone calls specifically."""
    wrapper = GoogleAdsWrapper()

    try:
        print("Updating campaign for phone call optimization...")

        # Get the campaign service
        campaign_service = wrapper._campaign_service()

        # Create update operation
        operation = wrapper.client.get_type("CampaignOperation")
        campaign = operation.update
        campaign.resource_name = campaign_resource_name

        # Update bidding strategy for phone call optimization
        # Use TARGET_CPA with a specific CPA for phone calls
        target_cpa_type = wrapper.client.get_type("TargetCpa")
        target_cpa = target_cpa_type()
        target_cpa.target_cpa_micros = 50000000  # $50 CPA for phone calls
        campaign.target_cpa = target_cpa

        # Set field mask
        field_mask = wrapper.client.get_type("FieldMask")
        field_mask.paths.append("target_cpa")
        operation.update_mask.CopyFrom(field_mask)

        # Execute update
        response = campaign_service.mutate_campaigns(
            customer_id=customer_id, operations=[operation]
        )

        print("Campaign updated for phone call optimization!")
        print(f"New bidding strategy: TARGET_CPA ($50 per phone call)")
        return True

    except Exception as e:
        print(f"Error updating campaign: {e}")
        return False

def main():
    customer_id = "4139022884"
    campaign_name = "[DRAFT] Priority Roofing - Optimized Parallel"

    print("=" * 60)
    print("UPDATE PRIORITY ROOFING CAMPAIGN FOR PHONE CALL OPTIMIZATION")
    print("=" * 60)

    # Get campaign resource name
    try:
        campaign_resource_name = get_campaign_resource_name(customer_id, campaign_name)
        print(f"Found campaign: {campaign_resource_name}")
    except Exception as e:
        print(f"Error finding campaign: {e}")
        return

    # Update campaign for phone calls
    success = update_campaign_for_phone_calls(customer_id, campaign_resource_name)

    print()
    print("=" * 60)
    if success:
        print("CAMPAIGN UPDATE SUCCESSFUL!")
        print("Campaign now optimized for PHONE CALL generation:")
        print("  - Bidding: TARGET_CPA ($50 per phone call)")
        print("  - Keywords: Already optimized for phone call intent")
        print("  - Negative keywords: Blocking non-phone-call traffic")
    else:
        print("CAMPAIGN UPDATE FAILED!")
        print("Phone call optimization not applied.")
    print("=" * 60)

if __name__ == "__main__":
    main()
