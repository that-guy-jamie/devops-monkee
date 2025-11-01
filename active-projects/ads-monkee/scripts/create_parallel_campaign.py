#!/usr/bin/env python3
"""
Create parallel campaign v2 for Priority Roofing based on analysis.
Creates campaign in PAUSED state, validates budget parity, then activates.
"""
import json
import sys
from pathlib import Path

# Ensure project root on path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.integrations.google_ads_client import GoogleAdsWrapper


def get_priority_roofing_campaign(customer_id: str) -> tuple:
    """Get the Priority Roofing campaign info."""
    wrapper = GoogleAdsWrapper()

    # Find the main Priority Roofing campaign (any status)
    service = wrapper._ga_service()
    query = """
    SELECT campaign.id, campaign.name, campaign.status, campaign_budget.amount_micros
    FROM campaign
    WHERE campaign.name LIKE '%Roofing%'
    ORDER BY campaign_budget.amount_micros DESC
    LIMIT 1
    """

    response = service.search(customer_id=customer_id, query=query)

    for row in response:
        campaign_id = row.campaign.id
        campaign_name = row.campaign.name
        budget_micros = int(row.campaign_budget.amount_micros) if row.campaign_budget else 0

        print(f"Found Priority Roofing campaign: {campaign_name} (ID: {campaign_id})")
        print(f"Current daily budget: ${budget_micros / 1_000_000:.2f}")

        return campaign_id, campaign_name, budget_micros

    raise RuntimeError(f"No Roofing campaign found for customer {customer_id}")


def create_paused_campaign(customer_id: str, campaign_name: str, daily_budget_micros: int) -> str:
    """Create new campaign in PAUSED state."""
    wrapper = GoogleAdsWrapper()

    print(f"Creating campaign '{campaign_name}' with budget ${daily_budget_micros / 1_000_000:.2f}...")

    # First, let's check the existing campaign's bidding strategy
    service = wrapper._ga_service()
    query = """
    SELECT campaign.bidding_strategy_type
    FROM campaign
    WHERE campaign.id = 10062493377
    LIMIT 1
    """

    response = service.search(customer_id=customer_id, query=query)
    for row in response:
        print(f"Original campaign bidding strategy type: {row.campaign.bidding_strategy_type}")

    # Use a test or draft approach to avoid committing real changes
    # For safety, we'll create the campaign but recommend manual activation
    resource_name = wrapper.create_campaign_paused_with_budget(
        customer_id=customer_id,
        name=f"[DRAFT] {campaign_name}",  # Mark as draft
        daily_budget_micros=daily_budget_micros,
        bidding_strategy_type="MAXIMIZE_CONVERSIONS",
    )

    print(f"[SUCCESS] Campaign created successfully: {resource_name}")
    print(f"[WARNING] This is a DRAFT campaign. Review in Google Ads UI before activating.")
    return resource_name


def validate_campaign_budget(customer_id: str, resource_name: str, expected_budget: int) -> bool:
    """Validate the created campaign has the correct budget."""
    wrapper = GoogleAdsWrapper()

    snapshot = wrapper.get_campaign_snapshot(customer_id, resource_name)

    print("Campaign validation:")
    print(f"  Name: {snapshot.name}")
    print(f"  Status: {snapshot.status}")
    print(f"  Budget: ${snapshot.daily_budget_micros / 1_000_000:.2f}")
    print(f"  Bidding: {snapshot.bidding_strategy_type}")

    budget_match = snapshot.daily_budget_micros == expected_budget
    status_paused = snapshot.status == "PAUSED"

    print(f"[VALIDATION] Budget parity: {'PASS' if budget_match else 'FAIL'}")
    print(f"[VALIDATION] Status PAUSED: {'PASS' if status_paused else 'FAIL'}")

    return budget_match and status_paused


def main():
    # Use Priority Roofing setup
    customer_id = "9390713365"  # Priority Roofing customer ID
    new_campaign_name = "[DRAFT] Roofing Services 2025 - Optimized v2"

    print(f"[INFO] Starting parallel campaign creation for Priority Roofing")
    print("=" * 60)

    try:
        # Step 1: Get Priority Roofing campaign info
        campaign_id, original_campaign_name, original_budget = get_priority_roofing_campaign(customer_id)

        # Step 2: Create new campaign in PAUSED state
        resource_name = create_paused_campaign(
            customer_id=customer_id,
            campaign_name=new_campaign_name,
            daily_budget_micros=original_budget
        )

        # Step 3: Validate the created campaign
        validation_pass = validate_campaign_budget(customer_id, resource_name, original_budget)

        if validation_pass:
            print("\n[SUCCESS] PARALLEL CAMPAIGN CREATION SUCCESSFUL!")
            print(f"Campaign '{new_campaign_name}' is ready for activation.")
            print(f"Resource name: {resource_name}")
            print(f"Original campaign: {original_campaign_name} (ID: {campaign_id})")

            # Return the resource name for next steps
            return resource_name
        else:
            print("\n[ERROR] VALIDATION FAILED!")
            sys.exit(1)

    except Exception as e:
        print(f"\n[ERROR] {e}")
        sys.exit(1)


if __name__ == "__main__":
    resource_name = main()
    print(f"\n[INFO] Next step: Use resource name '{resource_name}' for activation")
