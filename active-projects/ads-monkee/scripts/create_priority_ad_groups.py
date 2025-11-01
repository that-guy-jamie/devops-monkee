#!/usr/bin/env python3
"""
Create ad groups in the Priority Roofing parallel campaign.
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

def create_ad_group(customer_id: str, campaign_resource_name: str, ad_group_name: str, default_bid_micros: int = 1000000):
    """Create an ad group in the campaign."""
    wrapper = GoogleAdsWrapper()

    try:
        print(f"Creating ad group: {ad_group_name}")

        # Create ad group
        ad_group_service = wrapper.client.get_service("AdGroupService")

        operation = wrapper.client.get_type("AdGroupOperation")
        ad_group = operation.create
        ad_group.name = ad_group_name
        ad_group.campaign = campaign_resource_name
        ad_group.status = wrapper.client.enums.AdGroupStatusEnum.ENABLED

        # Set default bid (Max CPC)
        cpc_bid = wrapper.client.get_type("ManualCpc")
        cpc_bid.enhanced_cpc_enabled = False
        ad_group.cpc_bid_micros = default_bid_micros

        # Execute
        response = ad_group_service.mutate_ad_groups(
            customer_id=customer_id, operations=[operation]
        )

        ad_group_resource_name = response.results[0].resource_name
        print(f"Created ad group: {ad_group_resource_name}")
        return ad_group_resource_name

    except Exception as e:
        print(f"Failed to create ad group '{ad_group_name}': {e}")
        return None

def main():
    # Priority Roofing setup
    customer_id = "4139022884"
    campaign_name = "[DRAFT] Priority Roofing - Optimized Parallel"

    # Ad groups to create (from the keyword CSV analysis)
    ad_groups_to_create = [
        "Roof Repairs",
        "Local Roofing Contractors",
        "New Roof Installation",
        "Roof Inspections & Estimates"
    ]

    print("=" * 60)
    print("CREATE AD GROUPS FOR PRIORITY ROOFING CAMPAIGN")
    print("=" * 60)

    # Get campaign resource name
    try:
        campaign_resource_name = get_campaign_resource_name(customer_id, campaign_name)
        print(f"Found campaign: {campaign_resource_name}")
    except Exception as e:
        print(f"Error finding campaign: {e}")
        return

    print(f"\nCreating {len(ad_groups_to_create)} ad groups...")

    created_ad_groups = {}
    for ad_group_name in ad_groups_to_create:
        resource_name = create_ad_group(customer_id, campaign_resource_name, ad_group_name)
        if resource_name:
            created_ad_groups[ad_group_name] = resource_name

    print(f"\nAD GROUP CREATION COMPLETE!")
    print(f"Created {len(created_ad_groups)} ad groups:")
    for name, resource in created_ad_groups.items():
        print(f"  {name}: {resource}")

    print("=" * 60)

    # Save created ad groups for next step
    return created_ad_groups

if __name__ == "__main__":
    created_groups = main()
    if created_groups:
        print(f"\nCreated {len(created_groups)} ad groups for keyword addition")
