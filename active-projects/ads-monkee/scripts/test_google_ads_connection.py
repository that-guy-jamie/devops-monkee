#!/usr/bin/env python3
"""Test Google Ads connection and list campaigns."""

from backend.integrations.google_ads_client import GoogleAdsWrapper

def main():
    print("Testing Google Ads connection...")

    try:
        wrapper = GoogleAdsWrapper()
        print("Google Ads client initialized successfully")

        # First, list accessible customers
        customer_service = wrapper.client.get_service("CustomerService")
        accessible_customers = customer_service.list_accessible_customers()

        print(f"Accessible customers: {len(accessible_customers.resource_names)}")
        for rn in accessible_customers.resource_names:  # Show all
            customer_id = rn.split("/")[-1]
            print(f"  Customer ID: {customer_id}")

        # Test getting campaigns for the specified customer
        service = wrapper._ga_service()
        query = """
        SELECT campaign.id, campaign.name, campaign.status, campaign_budget.amount_micros
        FROM campaign
        LIMIT 10
        """

        # Search for roofing campaigns across all accessible customers
        roofing_campaigns = []

        for rn in accessible_customers.resource_names:
            customer_id = rn.split("/")[-1]
            try:
                response = service.search(customer_id=customer_id, query=query)
                for row in response:
                    if "roofing" in row.campaign.name.lower() or "roof" in row.campaign.name.lower():
                        roofing_campaigns.append({
                            'customer_id': customer_id,
                            'campaign_id': row.campaign.id,
                            'name': row.campaign.name,
                            'status': row.campaign.status.name,
                            'budget_micros': int(row.campaign_budget.amount_micros) if row.campaign_budget else 0
                        })
            except Exception as e:
                print(f"Error accessing customer {customer_id}: {e}")

        if roofing_campaigns:
            print(f"\nFound {len(roofing_campaigns)} roofing-related campaigns:")
            for campaign in roofing_campaigns:
                print(f"  Customer {campaign['customer_id']}: {campaign['campaign_id']} - {campaign['name']} ({campaign['status']}) - Budget: ${campaign['budget_micros'] / 1_000_000:.2f}")

                # Check if this is our target campaign
                if "Roofing Services 2025 - ECT/OCS" in campaign['name']:
                    print(f"\n*** TARGET CAMPAIGN FOUND: {campaign['name']} (ID: {campaign['campaign_id']}) in Customer {campaign['customer_id']} ***")
                    break
        else:
            print("\nNo roofing campaigns found in any accessible customer")

        # Also check the original customer ID specifically
        customer_ids = ['9390713365', '6254262524', '9883178263', '1877202760']

        for customer_id in customer_ids:
            print(f"\nTrying customer ID: {customer_id}")
            try:
                response = service.search(customer_id=customer_id, query=query)
                campaigns = []
                for row in response:
                    campaigns.append({
                        'id': row.campaign.id,
                        'name': row.campaign.name,
                        'status': row.campaign.status.name,
                        'budget_micros': int(row.campaign_budget.amount_micros) if row.campaign_budget else 0
                    })

                print(f"Found {len(campaigns)} campaigns for customer {customer_id}:")
                for campaign in campaigns:
                    print(f"  {campaign['id']}: {campaign['name']} ({campaign['status']}) - Budget: ${campaign['budget_micros'] / 1_000_000:.2f}")

                if campaigns:
                    # Check if our target campaign exists
                    target_campaign = next((c for c in campaigns if "Roofing Services 2025 - ECT/OCS" in c['name']), None)
                    if target_campaign:
                        print(f"\n*** TARGET CAMPAIGN FOUND: {target_campaign['name']} (ID: {target_campaign['id']}) ***")
                        break
            except Exception as e:
                print(f"Error accessing customer {customer_id}: {e}")

        return True

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    main()
