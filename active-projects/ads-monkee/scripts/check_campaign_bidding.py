#!/usr/bin/env python3
"""
Check the current bidding strategy of the Priority Roofing parallel campaign.
"""
import sys
from pathlib import Path

# Ensure project root on path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.integrations.google_ads_client import GoogleAdsWrapper

def check_campaign_bidding():
    """Check current campaign bidding strategy."""
    wrapper = GoogleAdsWrapper()

    service = wrapper._ga_service()
    query = """
    SELECT campaign.id, campaign.name, campaign.bidding_strategy_type, campaign.target_cpa.target_cpa_micros
    FROM campaign
    WHERE campaign.name = '[DRAFT] Priority Roofing - Optimized Parallel'
    LIMIT 1
    """

    response = service.search(customer_id="4139022884", query=query)

    for row in response:
        print(f"Campaign: {row.campaign.name}")
        print(f"Current bidding strategy: {row.campaign.bidding_strategy_type}")
        if row.campaign.target_cpa:
            print(f"Current target CPA: ${row.campaign.target_cpa.target_cpa_micros / 1000000:.2f}")
        else:
            print("No target CPA set")
        return

    print("Campaign not found")

def main():
    print("=" * 60)
    print("CHECK PRIORITY ROOFING CAMPAIGN BIDDING STRATEGY")
    print("=" * 60)

    check_campaign_bidding()

    print("=" * 60)

if __name__ == "__main__":
    main()
