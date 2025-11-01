#!/usr/bin/env python3
"""
Test direct access to the manager account itself.
This will help verify if the manager account is accessible and properly configured.
"""
import sys
from pathlib import Path

# Ensure project root on path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.integrations.google_ads_client import GoogleAdsWrapper

def test_manager_access(manager_id: str):
    """Test if we can access the manager account directly."""
    wrapper = GoogleAdsWrapper()

    try:
        print(f"Testing direct access to manager account: {manager_id}")

        # Test 1: Get manager account info
        service = wrapper._ga_service()
        query = f"""
        SELECT
          customer.id,
          customer.descriptive_name,
          customer.currency_code,
          customer.time_zone,
          customer.manager,
          customer.test_account
        FROM customer
        WHERE customer.id = {manager_id}
        LIMIT 1
        """

        print(f"Executing query: {query.strip()}")

        response = service.search(customer_id=manager_id, query=query)

        for row in response:
            print("SUCCESS! Manager account accessible:")
            print(f"   ID: {row.customer.id}")
            print(f"   Name: {row.customer.descriptive_name}")
            print(f"   Currency: {row.customer.currency_code}")
            print(f"   Timezone: {row.customer.time_zone}")
            print(f"   Is Manager: {row.customer.manager}")
            print(f"   Test Account: {row.customer.test_account}")
            return True

        print("Manager account not found")
        return False

    except Exception as e:
        print(f"Error accessing manager account: {e}")
        return False

def main():
    manager_id = "2996835705"

    print("=" * 60)
    print("GOOGLE ADS MANAGER ACCOUNT TEST")
    print("=" * 60)
    print(f"Testing Manager Account ID: {manager_id}")
    print()

    success = test_manager_access(manager_id)

    print()
    print("=" * 60)
    if success:
        print("MANAGER ACCOUNT TEST PASSED!")
        print("The manager account is accessible via the API.")
        print("Next step: Check account linking in Google Ads dashboard.")
    else:
        print("MANAGER ACCOUNT TEST FAILED!")
        print("Cannot access the manager account via API.")
        print("Check: Account funding, API permissions, or credentials.")
    print("=" * 60)

if __name__ == "__main__":
    main()
