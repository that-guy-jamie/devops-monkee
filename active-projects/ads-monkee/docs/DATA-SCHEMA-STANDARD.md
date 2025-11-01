# Ads Monkee Data Schema Standard

**Date:** 2025-10-18  
**Source of Truth:** `ads_sync/comprehensive_data_pull.py`  
**Status:** ✅ Standardized

---

## Overview

All Google Ads data in Ads Monkee follows the **exact same schema** as the proven `ads_sync` comprehensive data pull system. This ensures:

1. **Consistency** - Same fields, same names, same types across all systems
2. **Compatibility** - Can import existing CSV exports directly
3. **Validation** - Proven schema used in production for months
4. **Analysis** - Reports and analysis tools work across both systems

---

## Data Sources

### Primary Template
**Location:** `C:\Users\james\Desktop\Projects\ads_sync\data\priority-roofing\comprehensive\`

**Files:**
- `priority-roofing-campaigns-20251016_043710.csv`
- `priority-roofing-ad_groups-20251016_043710.csv`
- `priority-roofing-keywords-20251016_043710.csv`
- `priority-roofing-search_terms-20251016_043710.csv`

### Query Module
**Location:** `ads-monkee/backend/services/google_ads_queries.py`

Contains:
- Standardized GAQL queries for all data types
- Field mapping (API → CSV → Database)
- Micros-to-currency conversion utilities
- Query registry for easy access

---

## Schema Definitions

### 1. Campaigns

**CSV Columns:**
```
date, campaign_id, campaign_name, campaign_status, channel_type,
bidding_strategy, impressions, clicks, cost, conversions,
conversions_value, all_conversions, view_through_conversions,
avg_cpc, avg_cpm, impression_share, budget_lost_is, rank_lost_is
```

**Data Types:**
- `date`: DATE (YYYY-MM-DD)
- `campaign_id`: BIGINT
- `campaign_name`: VARCHAR(255)
- `campaign_status`: VARCHAR(50) (ENABLED, PAUSED, REMOVED)
- `channel_type`: VARCHAR(50) (SEARCH, DISPLAY, SHOPPING, etc.)
- `bidding_strategy`: VARCHAR(100)
- `impressions`: INTEGER
- `clicks`: INTEGER
- `cost`: DECIMAL(12,2) (USD)
- `conversions`: DECIMAL(10,2)
- `conversions_value`: DECIMAL(12,2)
- `all_conversions`: DECIMAL(10,2)
- `view_through_conversions`: INTEGER
- `avg_cpc`: DECIMAL(10,2)
- `avg_cpm`: DECIMAL(10,2)
- `impression_share`: DECIMAL(5,4) (0.0 to 1.0)
- `budget_lost_is`: DECIMAL(5,4)
- `rank_lost_is`: DECIMAL(5,4)

**Example Row:**
```csv
2025-04-18,22180269024,Roofing Services 2025 - ECT/OCS,ENABLED,SEARCH,MAXIMIZE_CONVERSIONS,195,9,99.15,0.0,0.0,0.0,0,11.02,508.48,0.228,0.0,0.772
```

---

### 2. Ad Groups

**CSV Columns:**
```
date, campaign_id, campaign_name, ad_group_id, ad_group_name,
ad_group_status, ad_group_type, cpc_bid, impressions, clicks,
cost, conversions, conversions_value, avg_cpc
```

**Data Types:**
- `date`: DATE
- `campaign_id`: BIGINT
- `campaign_name`: VARCHAR(255)
- `ad_group_id`: BIGINT
- `ad_group_name`: VARCHAR(255)
- `ad_group_status`: VARCHAR(50)
- `ad_group_type`: VARCHAR(50) (SEARCH_STANDARD, DISPLAY_STANDARD, etc.)
- `cpc_bid`: DECIMAL(10,2)
- `impressions`: INTEGER
- `clicks`: INTEGER
- `cost`: DECIMAL(12,2)
- `conversions`: DECIMAL(10,2)
- `conversions_value`: DECIMAL(12,2)
- `avg_cpc`: DECIMAL(10,2)

**Example Row:**
```csv
2025-04-18,22180269024,Roofing Services 2025 - ECT/OCS,174397650916,Roof Repairs,PAUSED,SEARCH_STANDARD,0.01,47,3,65.24,0.0,0.0,21.75
```

---

### 3. Keywords

**CSV Columns:**
```
date, campaign_id, campaign_name, ad_group_id, ad_group_name,
keyword_id, keyword_text, match_type, keyword_status,
quality_score, creative_quality, landing_page_quality, expected_ctr,
max_cpc_bid, final_url, impressions, clicks, cost,
conversions, conversions_value, avg_cpc
```

**Data Types:**
- `date`: DATE
- `campaign_id`: BIGINT
- `campaign_name`: VARCHAR(255)
- `ad_group_id`: BIGINT
- `ad_group_name`: VARCHAR(255)
- `keyword_id`: BIGINT
- `keyword_text`: VARCHAR(500)
- `match_type`: VARCHAR(20) (EXACT, PHRASE, BROAD)
- `keyword_status`: VARCHAR(50)
- `quality_score`: INTEGER (1-10, NULL if no data)
- `creative_quality`: VARCHAR(50) (ABOVE_AVERAGE, AVERAGE, BELOW_AVERAGE)
- `landing_page_quality`: VARCHAR(50)
- `expected_ctr`: VARCHAR(50)
- `max_cpc_bid`: DECIMAL(10,2) (can be NULL)
- `final_url`: TEXT (can be NULL)
- `impressions`: INTEGER
- `clicks`: INTEGER
- `cost`: DECIMAL(12,2)
- `conversions`: DECIMAL(10,2)
- `conversions_value`: DECIMAL(12,2)
- `avg_cpc`: DECIMAL(10,2) (NULL if no clicks)

**Example Row:**
```csv
2025-04-18,22180269024,Roofing Services 2025 - ECT/OCS,174397650916,Roof Repairs,10619091,roof repair,BROAD,ENABLED,3.0,ABOVE_AVERAGE,BELOW_AVERAGE,BELOW_AVERAGE,,,47,3,65.24,0.0,0.0,21.75
```

---

### 4. Search Terms

**CSV Columns:**
```
date, campaign_id, campaign_name, ad_group_id, ad_group_name,
search_term, search_term_status, match_type_delivered,
impressions, clicks, cost, conversions, conversions_value
```

**Data Types:**
- `date`: DATE
- `campaign_id`: BIGINT
- `campaign_name`: VARCHAR(255)
- `ad_group_id`: BIGINT
- `ad_group_name`: VARCHAR(255)
- `search_term`: VARCHAR(500)
- `search_term_status`: VARCHAR(50) (NONE, ADDED, EXCLUDED)
- `match_type_delivered`: VARCHAR(20) (EXACT, PHRASE, BROAD, NEAR_EXACT, NEAR_PHRASE)
- `impressions`: INTEGER
- `clicks`: INTEGER
- `cost`: DECIMAL(12,2)
- `conversions`: DECIMAL(10,2)
- `conversions_value`: DECIMAL(12,2)

**Example Row:**
```csv
2025-04-18,22180269024,Roofing Services 2025 - ECT/OCS,174397650916,Roof Repairs,roof repair near me,NONE,PHRASE,1,0,0.0,0.0,0.0
```

---

## Important Notes

### Currency Conversion
All `cost` and `bid` fields in the Google Ads API are returned in **micros** (1/1,000,000 of a currency unit).

**Conversion:**
```python
cost_usd = cost_micros / 1_000_000.0
```

**Example:**
- API returns: `99154344` micros
- CSV/Database stores: `99.15` USD

### NULL Handling
- **Quality Score fields**: NULL when Google hasn't calculated them yet (low volume keywords)
- **avg_cpc**: NULL when clicks = 0
- **max_cpc_bid**: NULL for automated bidding strategies
- **final_url**: NULL when using ad group-level URLs

### Enum Values
All enum values (status, match_type, quality ratings) are stored as **strings** matching Google Ads API exactly:
- Campaign Status: `ENABLED`, `PAUSED`, `REMOVED`
- Match Type: `EXACT`, `PHRASE`, `BROAD`
- Quality Rating: `ABOVE_AVERAGE`, `AVERAGE`, `BELOW_AVERAGE`, `UNSPECIFIED`

---

## Migration Path

### From CSV (ads_sync) → Database (ads-monkee)

1. **Read CSV** with pandas
2. **Validate schema** against this document
3. **Convert types** (string dates → DATE, string numbers → DECIMAL)
4. **Add client_id** foreign key
5. **Insert** into PostgreSQL

**No field transformations needed** - column names match database columns exactly!

---

## Query Usage

### In Migration Scripts
```python
from backend.services.google_ads_queries import get_query

# Get standardized query
query = get_query('campaigns', start_date='2024-01-01', end_date='2024-12-31')

# Execute via Google Ads API
response = ga_service.search(customer_id=customer_id, query=query)
```

### In Analysis Scripts
```python
from backend.services.google_ads_queries import FIELD_MAPPINGS

# Get field mapping for campaigns
field_map = FIELD_MAPPINGS['campaigns']

# Convert API response to CSV-compatible dict
row_dict = {
    field_map['campaign.id']: campaign.id,
    field_map['campaign.name']: campaign.name,
    # ... etc
}
```

---

## Validation

### Schema Validation
All data must pass:
1. **Column count** matches schema
2. **Column names** match exactly (case-sensitive)
3. **Data types** are compatible
4. **Required fields** are not NULL (campaign_id, date, etc.)

### Quality Checks
- No duplicate (client_id, campaign_id, date) combinations
- All costs >= 0
- All impressions >= clicks
- All clicks >= conversions
- Quality scores in range 1-10 or NULL

---

## Version History

### v1.0.0 (2025-10-18)
- Initial standardization based on `ads_sync` comprehensive data pull
- Validated against 6 months of Priority Roofing data
- Query module created in `backend/services/google_ads_queries.py`

---

## References

- **Source Script:** `ads_sync/scripts/comprehensive_data_pull.py`
- **Sample Data:** `ads_sync/data/priority-roofing/comprehensive/`
- **Query Module:** `ads-monkee/backend/services/google_ads_queries.py`
- **Database Models:** `ads-monkee/backend/models/google_ads.py`
- **Google Ads API Docs:** https://developers.google.com/google-ads/api/docs/query/overview

---

**Status:** ✅ This schema is the official standard for all Google Ads data in Ads Monkee.

