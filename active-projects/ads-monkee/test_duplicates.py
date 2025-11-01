from backend.database import sync_engine
from sqlalchemy import text

with sync_engine.connect() as conn:
    result = conn.execute(text("""
        SELECT client_id, ad_group_id, keyword_id, date, COUNT(*) as cnt 
        FROM google_ads_keywords 
        GROUP BY client_id, ad_group_id, keyword_id, date 
        HAVING COUNT(*) > 1 
        LIMIT 5
    """))
    print("Duplicates in source:")
    for row in result:
        print(f"  {row}")

