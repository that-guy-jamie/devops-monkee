#!/usr/bin/env python3
"""
Test access to specific Google Ads client account.
Safe read-only test - no modifications made.
"""
import sys
from pathlib import Path

# Ensure project root on path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.integrations.google_ads_client import GoogleAdsWrapper

def test_client_access(customer_id: str, client_name: str) -> bool:
    """Test if we can access the specified Google Ads client account."""
    wrapper = GoogleAdsWrapper()

    try:
        print(f"Testing access to {client_name} (Customer ID: {customer_id})...")

        # Test 1: Basic account info query
        service = wrapper._ga_service()
        query = f"""
        SELECT
          customer.id,
          customer.descriptive_name,
          customer.currency_code,
          customer.time_zone,
          customer.has_partners_badge,
          customer.manager,
          customer.test_account
        FROM customer
        WHERE customer.id = {customer_id}
        LIMIT 1
        """

        print(f"Executing query: {query.strip()}")

        response = service.search(customer_id=customer_id, query=query)

        for row in response:
            print("SUCCESS! Account found and accessible:")
            print(f"   Name: {row.customer.descriptive_name}")
            print(f"   Currency: {row.customer.currency_code}")
            print(f"   Time Zone: {row.customer.time_zone}")
            print(f"   Manager: {row.customer.manager}")
            print(f"   Test Account: {row.customer.test_account}")
            print(f"   Has Partners Badge: {row.customer.has_partners_badge}")
            return True

        print("Account not found or not accessible")
        return False

    except Exception as e:
        print(f"Error accessing account: {e}")
        return False

def main():
    # Test the specific client account
    customer_id = "8582877691"  # Remove dashes for API
    client_name = "One Click SEO (TEST CLIENT)"

    print("=" * 60)
    print("GOOGLE ADS CLIENT ACCESS TEST")
    print("=" * 60)
    print(f"Target: {client_name}")
    print(f"Customer ID: {customer_id}")
    print()

    success = test_client_access(customer_id, client_name)

    print()
    print("=" * 60)
    if success:
        print("ACCESS TEST PASSED!")
        print("This client account is accessible via the current Google Ads API configuration.")
    else:
        print("ACCESS TEST FAILED!")
        print("This client account is NOT accessible or doesn't exist.")
        print("Check: Customer ID, authentication, or account permissions.")
    print("=" * 60)

if __name__ == "__main__":
    main()
