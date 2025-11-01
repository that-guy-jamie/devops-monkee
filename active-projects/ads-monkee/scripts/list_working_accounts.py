#!/usr/bin/env python3
"""
List all Google Ads accounts accessible under the working manager account.
This will help identify dormant accounts we can use for testing.
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

        response = service.search(customer_id="1877202760", query=query)  # Use working manager ID

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
            for i, account in enumerate(accounts, 1):
                print(f"{i}. ID: {account['id']}")
                print(f"   Name: {account['name']}")
                print(f"   Currency: {account['currency']}")
                print(f"   Timezone: {account['timezone']}")
                print(f"   Manager: {account['manager']}")
                print(f"   Test Account: {account['test_account']}")
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
    print("Using working manager ID: 1877202760")
    print()

    accounts = list_accessible_accounts()

    print(f"\nTotal accounts found: {len(accounts)}")

    if accounts:
        print("\nPOTENTIAL DORMANT ACCOUNTS TO USE:")
        print("(Look for accounts that might not be actively managed)")
        print("=" * 40)

        # Suggest some accounts that might be dormant
        for account in accounts:
            if "test" in account['name'].lower() or "dormant" in account['name'].lower():
                print(f"ID: {account['id']} - {account['name']} (Test/Dormant)")
            elif account['test_account']:
                print(f"ID: {account['id']} - {account['name']} (Marked as Test Account)")

        print("\nOr pick any account that looks like it's not actively being used.")
    print("=" * 60)

if __name__ == "__main__":
    main()
