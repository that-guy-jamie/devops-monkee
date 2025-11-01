from backend.database import sync_engine
from sqlalchemy import text

print("\n=== CLIENTS IN DATABASE ===\n")

with sync_engine.connect() as conn:
    # Get all clients
    result = conn.execute(text("""
        SELECT id, name, slug, google_ads_customer_id, status, 
               last_sync_at, created_at
        FROM clients 
        ORDER BY id
    """))
    
    clients = list(result)
    
    if not clients:
        print("No clients found!")
    else:
        for row in clients:
            print(f"ID: {row.id}")
            print(f"  Name: {row.name}")
            print(f"  Slug: {row.slug}")
            print(f"  Google Ads ID: {row.google_ads_customer_id}")
            print(f"  Status: {row.status}")
            print(f"  Last Sync: {row.last_sync_at}")
            print(f"  Created: {row.created_at}")
            print()
    
    # Get data counts for each client
    print("\n=== DATA COUNTS BY CLIENT ===\n")
    
    for client in clients:
        print(f"{client.name} (ID: {client.id}):")
        
        # Campaigns
        r1 = conn.execute(text(f"SELECT COUNT(*) FROM google_ads_campaigns WHERE client_id = {client.id}"))
        campaigns = r1.scalar()
        
        # Ad Groups
        r2 = conn.execute(text(f"SELECT COUNT(*) FROM google_ads_ad_groups WHERE client_id = {client.id}"))
        ad_groups = r2.scalar()
        
        # Keywords
        r3 = conn.execute(text(f"SELECT COUNT(*) FROM google_ads_keywords WHERE client_id = {client.id}"))
        keywords = r3.scalar()
        
        # Search Terms
        r4 = conn.execute(text(f"SELECT COUNT(*) FROM google_ads_search_terms WHERE client_id = {client.id}"))
        search_terms = r4.scalar()
        
        # Aggregates
        r5 = conn.execute(text(f"SELECT COUNT(*) FROM agg_campaign_daily WHERE client_id = {client.id}"))
        agg_campaigns = r5.scalar()
        
        r6 = conn.execute(text(f"SELECT COUNT(*) FROM agg_adgroup_daily WHERE client_id = {client.id}"))
        agg_adgroups = r6.scalar()
        
        print(f"  Raw Data:")
        print(f"    Campaigns: {campaigns:,}")
        print(f"    Ad Groups: {ad_groups:,}")
        print(f"    Keywords: {keywords:,}")
        print(f"    Search Terms: {search_terms:,}")
        print(f"  Aggregates:")
        print(f"    Campaign Daily: {agg_campaigns:,}")
        print(f"    Ad Group Daily: {agg_adgroups:,}")
        print()

