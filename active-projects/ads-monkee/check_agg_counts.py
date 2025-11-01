from backend.database import sync_engine
from sqlalchemy import text

with sync_engine.connect() as conn:
    r1 = conn.execute(text('SELECT COUNT(*) FROM agg_campaign_daily'))
    r2 = conn.execute(text('SELECT COUNT(*) FROM agg_adgroup_daily'))
    r3 = conn.execute(text('SELECT COUNT(*) FROM agg_keyword_daily'))
    r4 = conn.execute(text('SELECT COUNT(*) FROM agg_search_term_daily'))
    
    print(f'Campaigns: {r1.scalar()}')
    print(f'Ad Groups: {r2.scalar()}')
    print(f'Keywords: {r3.scalar()}')
    print(f'Search Terms: {r4.scalar()}')

