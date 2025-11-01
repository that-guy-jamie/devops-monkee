from backend.database import sync_engine
from sqlalchemy import text

with sync_engine.connect() as conn:
    # Check for duplicate rows
    result = conn.execute(text("""
        SELECT client_id, ad_group_id, keyword_id, date, COUNT(*) as cnt,
               STRING_AGG(DISTINCT campaign_id::text, ', ') as campaign_ids,
               STRING_AGG(DISTINCT keyword_text, ', ') as texts
        FROM google_ads_keywords 
        WHERE date >= CURRENT_DATE - INTERVAL '180 days'
        GROUP BY client_id, ad_group_id, keyword_id, date 
        HAVING COUNT(*) > 1 
        LIMIT 10
    """))
    
    rows = list(result)
    if rows:
        print(f"Found {len(rows)} duplicate groups:")
        for row in rows:
            print(f"  client={row[0]}, ag={row[1]}, kw={row[2]}, date={row[3]}, count={row[4]}")
            print(f"    campaigns: {row[5]}")
            print(f"    texts: {row[6]}")
    else:
        print("No duplicates found!")

