#!/usr/bin/env python3
"""
List ALL Google Ads accounts accessible under the manager account.
This will show us exactly what's available so we can pick a dormant account.
"""
import sys
from pathlib import Path

# Ensure project root on path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.integrations.google_ads_client import GoogleAdsWrapper

def list_all_accessible_accounts():
    """List all accessible Google Ads accounts."""
    wrapper = GoogleAdsWrapper()

    try:
        print("Listing ALL accessible Google Ads accounts...")

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
        ORDER BY customer.id
        """

        print(f"Executing query: {query.strip()}")

        response = service.search(customer_id="1877202760", query=query)

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
            print("-" * 100)
            for i, account in enumerate(accounts, 1):
                print(f"{i}. ID: {account['id']}")
                print(f"   Name: {account['name']}")
                print(f"   Currency: {account['currency']}")
                print(f"   Timezone: {account['timezone']}")
                print(f"   Manager: {account['manager']}")
                print(f"   Test Account: {account['test_account']}")
                print("-" * 100)
        else:
            print("\nNo accessible accounts found.")

        return accounts

    except Exception as e:
        print(f"Error listing accounts: {e}")
        return []

def main():
    print("=" * 60)
    print("ALL ACCESSIBLE GOOGLE ADS ACCOUNTS")
    print("=" * 60)
    print("Using manager ID: 1877202760")
    print()

    accounts = list_all_accessible_accounts()

    print(f"\nTotal accounts found: {len(accounts)}")

    if accounts:
        print("\nACCOUNTS TO CHOOSE FROM:")
        print("=" * 40)

        # Highlight potential dormant accounts
        for account in accounts:
            if account['test_account']:
                print(f"ID: {account['id']} - {account['name']} (TEST ACCOUNT)")
            elif "test" in account['name'].lower() or "dormant" in account['name'].lower():
                print(f"ID: {account['id']} - {account['name']} (POTENTIAL DORMANT)")

        print("\nOr pick any account that looks like it's not actively being used.")
        print("Which account ID would you like to use for testing?")

    print("=" * 60)

if __name__ == "__main__":
    main()
