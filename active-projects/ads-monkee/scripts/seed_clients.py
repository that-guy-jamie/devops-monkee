"""
Seed Clients from Google Ads API
=================================

Discovers all client accounts and creates client records.
"""

import asyncio
import sys
from pathlib import Path
import re

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

from backend.database import AsyncSessionLocal
from backend.models import Client, ClientStatus
from backend.config import settings


def slugify(text: str) -> str:
    """Convert text to URL-friendly slug."""
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text.strip('-')


async def fetch_google_ads_clients():
    """Fetch all client accounts from Google Ads API."""
    print("Connecting to Google Ads API...")
    
    # Create Google Ads client from YAML file
    yaml_path = Path(__file__).parent.parent / "google-ads.yaml"
    google_ads_client = GoogleAdsClient.load_from_storage(str(yaml_path))
    
    ga_service = google_ads_client.get_service("GoogleAdsService")
    
    query = """
        SELECT
            customer_client.id,
            customer_client.descriptive_name,
            customer_client.manager,
            customer_client.test_account,
            customer_client.status
        FROM customer_client
        WHERE customer_client.status = 'ENABLED'
    """
    
    try:
        print(f"Querying MCC account: {settings.GOOGLE_ADS_LOGIN_CUSTOMER_ID}")
        response = ga_service.search(
            customer_id=settings.GOOGLE_ADS_LOGIN_CUSTOMER_ID.replace("-", ""),
            query=query
        )
        
        clients = []
        for row in response:
            customer = row.customer_client
            
            # Skip if it's a manager account or test account
            if customer.manager or customer.test_account:
                continue
            
            clients.append({
                'id': customer.id,
                'name': customer.descriptive_name,
                'status': customer.status.name
            })
        
        print(f"✅ Found {len(clients)} client accounts")
        return clients
        
    except GoogleAdsException as ex:
        print(f"❌ Google Ads API error:")
        for error in ex.failure.errors:
            print(f"  {error.message}")
        raise


async def seed_clients():
    """Create client records in database."""
    print("\n" + "="*80)
    print("SEEDING CLIENTS FROM GOOGLE ADS API")
    print("="*80 + "\n")
    
    # Fetch from Google Ads
    google_ads_clients = await fetch_google_ads_clients()
    
    # Create database records
    async with AsyncSessionLocal() as session:
        print(f"\nCreating database records...")
        
        created_count = 0
        updated_count = 0
        skipped_count = 0
        
        for gads_client in google_ads_clients:
            customer_id = str(gads_client['id'])
            name = gads_client['name']
            slug = slugify(name)
            
            # Check if client already exists
            result = await session.execute(
                """
                SELECT id FROM clients 
                WHERE google_ads_customer_id = :customer_id
                """,
                {"customer_id": customer_id}
            )
            existing = result.scalar_one_or_none()
            
            if existing:
                print(f"  ⏭️  Skipping '{name}' (already exists)")
                skipped_count += 1
                continue
            
            # Create new client
            client = Client(
                name=name,
                slug=slug,
                google_ads_customer_id=customer_id,
                google_ads_account_name=name,
                status=ClientStatus.ACTIVE
            )
            
            session.add(client)
            print(f"  ✅ Created '{name}' (slug: {slug})")
            created_count += 1
        
        # Commit all changes
        await session.commit()
        
        print(f"\n" + "="*80)
        print(f"SUMMARY")
        print("="*80)
        print(f"  Created: {created_count}")
        print(f"  Updated: {updated_count}")
        print(f"  Skipped: {skipped_count}")
        print(f"  Total:   {created_count + updated_count + skipped_count}")
        print("="*80 + "\n")


async def main():
    """Main entry point."""
    try:
        await seed_clients()
        print("✅ Client seeding completed successfully!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

