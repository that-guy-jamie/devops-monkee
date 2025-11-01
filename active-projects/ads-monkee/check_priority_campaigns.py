from backend.database import sync_engine
from sqlalchemy import text

print("\n=== PRIORITY ROOFING CAMPAIGNS ===\n")

with sync_engine.connect() as conn:
    # Get campaigns for Priority Roofing (client_id = 1)
    result = conn.execute(text("""
        SELECT DISTINCT 
            campaign_id,
            campaign_name,
            campaign_status,
            budget_amount_micros,
            bidding_strategy_type
        FROM google_ads_campaigns 
        WHERE client_id = 1
        ORDER BY campaign_name
    """))
    
    campaigns = list(result)
    
    if not campaigns:
        print("No campaigns found!")
    else:
        for row in campaigns:
            budget_dollars = row.budget_amount_micros / 1_000_000 if row.budget_amount_micros else 0
            print(f"Campaign: {row.campaign_name}")
            print(f"  ID: {row.campaign_id}")
            print(f"  Status: {row.campaign_status}")
            print(f"  Daily Budget: ${budget_dollars:.2f}")
            print(f"  Bidding Strategy: {row.bidding_strategy_type}")
            print()
    
    # Get the specific campaign mentioned in the analysis
    print("\n=== ROOFING SERVICES 2025 - ECT/OCS DETAILS ===\n")
    
    result = conn.execute(text("""
        SELECT 
            campaign_id,
            campaign_name,
            campaign_status,
            budget_amount_micros,
            bidding_strategy_type,
            target_cpa_micros,
            COUNT(*) as row_count
        FROM google_ads_campaigns 
        WHERE client_id = 1 
        AND campaign_name LIKE '%Roofing Services 2025%'
        GROUP BY campaign_id, campaign_name, campaign_status, budget_amount_micros, bidding_strategy_type, target_cpa_micros
    """))
    
    for row in result:
        budget_dollars = row.budget_amount_micros / 1_000_000 if row.budget_amount_micros else 0
        target_cpa = row.target_cpa_micros / 1_000_000 if row.target_cpa_micros else None
        print(f"Campaign: {row.campaign_name}")
        print(f"  ID: {row.campaign_id}")
        print(f"  Status: {row.campaign_status}")
        print(f"  Daily Budget: ${budget_dollars:.2f}")
        print(f"  Bidding Strategy: {row.bidding_strategy_type}")
        print(f"  Target CPA: ${target_cpa:.2f}" if target_cpa else "  Target CPA: Not set")
        print(f"  Data rows: {row.row_count}")
        print()

