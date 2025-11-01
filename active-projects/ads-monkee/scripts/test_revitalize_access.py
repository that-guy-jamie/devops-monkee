#!/usr/bin/env python3
"""
Test access to Revitalize Property Solutions Google Ads account.
Safe read-only test - no modifications made.
"""
import sys
from pathlib import Path

# Ensure project root on path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.integrations.google_ads_client import GoogleAdsWrapper

def test_revitalize_access():
    """Test if we can access the Revitalize Property Solutions account."""
    wrapper = GoogleAdsWrapper()

    try:
        print("Testing access to Revitalize Property Solutions...")

        # Test 1: Basic account info query
        service = wrapper._ga_service()
        query = """
        SELECT
          customer.id,
          customer.descriptive_name,
          customer.currency_code,
          customer.time_zone,
          customer.manager,
          customer.test_account
        FROM customer
        WHERE customer.descriptive_name LIKE '%Revitalize%'
        LIMIT 1
        """

        print(f"Executing query: {query.strip()}")

        response = service.search(customer_id="1877202760", query=query)

        for row in response:
            print("SUCCESS! Revitalize Property Solutions found and accessible:")
            print(f"   ID: {row.customer.id}")
            print(f"   Name: {row.customer.descriptive_name}")
            print(f"   Currency: {row.customer.currency_code}")
            print(f"   Timezone: {row.customer.time_zone}")
            print(f"   Manager: {row.customer.manager}")
            print(f"   Test Account: {row.customer.test_account}")
            return str(row.customer.id)

        print("Revitalize Property Solutions not found")
        return None

    except Exception as e:
        print(f"Error accessing Revitalize account: {e}")
        return None

def main():
    print("=" * 60)
    print("REVITALIZE PROPERTY SOLUTIONS ACCESS TEST")
    print("=" * 60)

    revital_account_id = test_revitalize_access()

    print()
    print("=" * 60)
    if revital_account_id:
        print("REVITALIZE ACCOUNT TEST PASSED!")
        print(f"Account ID: {revital_account_id}")
        print("This account is accessible via the current Google Ads API configuration.")
        print("We can use this for parallel campaign testing.")
    else:
        print("REVITALIZE ACCOUNT TEST FAILED!")
        print("Revitalize Property Solutions is NOT accessible.")
        print("This account might not exist or isn't properly linked.")
    print("=" * 60)

    return revital_account_id

if __name__ == "__main__":
    account_id = main()
    if account_id:
        print(f"\nRevitalize Account ID for use: {account_id}")
