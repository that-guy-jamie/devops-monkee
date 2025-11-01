from backend.database import sync_engine
from sqlalchemy import text

with sync_engine.connect() as conn:
    # Get one row from source
    result = conn.execute(text("""
        SELECT * FROM google_ads_keywords LIMIT 1
    """))
    row = result.fetchone()
    print(f"Source row: client={row.client_id}, ag={row.ad_group_id}, kw={row.keyword_id}, date={row.date}")
    
    # Try to insert it
    try:
        conn.execute(text("""
            INSERT INTO agg_keyword_daily (
                client_id, campaign_id, campaign_name, ad_group_id, ad_group_name,
                keyword_id, keyword_text, match_type, date,
                impressions, clicks, cost, conversions, conversions_value,
                quality_score, created_at, updated_at
            ) VALUES (
                :client_id, :campaign_id, :campaign_name, :ad_group_id, :ad_group_name,
                :keyword_id, :keyword_text, :match_type, :date,
                :impressions, :clicks, :cost, :conversions, :conversions_value,
                :quality_score, NOW(), NOW()
            )
            ON CONFLICT (client_id, ad_group_id, keyword_id, date) DO UPDATE SET
                impressions = EXCLUDED.impressions
        """), {
            'client_id': row.client_id,
            'campaign_id': row.campaign_id,
            'campaign_name': row.campaign_name,
            'ad_group_id': row.ad_group_id,
            'ad_group_name': row.ad_group_name,
            'keyword_id': row.keyword_id,
            'keyword_text': row.keyword_text,
            'match_type': row.match_type,
            'date': row.date,
            'impressions': row.impressions,
            'clicks': row.clicks,
            'cost': row.cost,
            'conversions': row.conversions,
            'conversions_value': row.conversions_value,
            'quality_score': row.quality_score,
        })
        conn.commit()
        print("Insert successful!")
    except Exception as e:
        print(f"Insert failed: {e}")
        conn.rollback()

