#!/usr/bin/env python3
"""
List all Google Ads accounts accessible under the current manager account.
This will help verify which accounts are actually linked and accessible.
"""
import sys
from pathlib import Path

# Ensure project root on path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.integrations.google_ads_client import GoogleAdsWrapper

def list_accessible_accounts():
    """List all accessible Google Ads accounts."""
    wrapper = GoogleAdsWrapper()

    try:
        print("Listing accessible Google Ads accounts...")

        # Query for all accessible customers
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
        WHERE customer.manager = false
        ORDER BY customer.id
        """

        print(f"Executing query: {query.strip()}")

        response = service.search(customer_id="2996835705", query=query)  # Use manager customer ID

        accounts = []
        for row in response:
            accounts.append({
                'id': str(row.customer.id),
                'name': row.customer.descriptive_name,
                'currency': row.customer.currency_code,
                'timezone': row.customer.time_zone,
                'manager': row.customer.manager,
                'test_account': row.customer.test_account
            })

        if accounts:
            print(f"\nFound {len(accounts)} accessible accounts:")
            print("-" * 80)
            for account in accounts:
                print(f"ID: {account['id']}")
                print(f"Name: {account['name']}")
                print(f"Currency: {account['currency']}")
                print(f"Timezone: {account['timezone']}")
                print(f"Manager: {account['manager']}")
                print(f"Test Account: {account['test_account']}")
                print("-" * 80)
        else:
            print("\nNo accessible accounts found.")

        return accounts

    except Exception as e:
        print(f"Error listing accounts: {e}")
        return []

def main():
    print("=" * 60)
    print("GOOGLE ADS ACCESSIBLE ACCOUNTS LIST")
    print("=" * 60)

    accounts = list_accessible_accounts()

    print(f"\nTotal accounts found: {len(accounts)}")

    # Check if One Click SEO is in the list
    one_click_seo_id = "8582877691"
    found = any(acc['id'] == one_click_seo_id for acc in accounts)

    if found:
        print(f"\nOne Click SEO (ID: {one_click_seo_id}) IS accessible!")
    else:
        print(f"\nOne Click SEO (ID: {one_click_seo_id}) is NOT in the accessible accounts list.")
        print("This suggests either:")
        print("  - The account doesn't exist yet")
        print("  - It's not properly linked to your manager account")
        print("  - There was an issue during setup")

    print("=" * 60)

if __name__ == "__main__":
    main()
