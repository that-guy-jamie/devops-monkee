# Ads Monkee - Data Migration Guide

**Version:** 1.0.0  
**Date:** 2025-10-17  
**Author:** OneClickSEO Development Team

---

## Overview

This guide explains how to migrate all Google Ads data from the legacy `ads_sync` CSV-based system to the new PostgreSQL database for **Ads Monkee**.

### Two-Tier Data Strategy

**Tier 1: Operational Dataset (1 Year)**
- **Purpose:** Active campaign optimization and recommendations
- **Timeframe:** Last 12 months
- **Rationale:** Recent data reflects current market conditions, search trends, and campaign performance
- **Used For:** Daily analysis, AI recommendations, campaign modifications

**Tier 2: Historical Dataset (2-5 Years)**
- **Purpose:** Long-term trend analysis and pattern discovery
- **Timeframe:** 2-5 years ago (excluding last 12 months)
- **Rationale:** Reveals seasonal patterns, "hidden gems," and market shifts over time
- **Used For:** Strategic planning, seasonal forecasting, historical context

---

## Prerequisites

### 1. Database Provisioned ✅
- PostgreSQL 16 database on Render
- Connection strings obtained (Internal + External)
- `.env` file configured in `ads-monkee/`

### 2. Environment Setup
```bash
cd ads-monkee

# Verify Poetry environment
poetry --version

# Install dependencies
poetry install

# Verify database connection
poetry run python -c "from backend.database import engine; print('✅ DB Connected:', engine.url)"
```

### 3. Migrations Applied
```bash
# Generate initial migration
poetry run alembic revision --autogenerate -m "Initial schema - 17 tables"

# Apply migrations
poetry run alembic upgrade head

# Verify tables created
poetry run python -c "from backend.models import Base; print('✅ Models:', len(Base.metadata.tables), 'tables')"
```

### 4. Clients Seeded
```bash
# Seed clients from Google Ads API
poetry run python scripts/seed_clients.py

# Verify
poetry run python -c "from backend.database import SessionLocal; from backend.models import Client; s = SessionLocal(); print('✅ Clients:', s.query(Client).count()); s.close()"
```

**Expected:** ~30 clients in database

---

## Migration Process

### Phase 1: Operational Dataset (1 Year) 🎯

**Script:** `scripts/migrate_all_clients_data.py`

#### What It Does
- Pulls 12 months of comprehensive Google Ads data for all clients
- Fetches 4 data types:
  - **Campaigns** (performance, budgets, bidding strategies)
  - **Ad Groups** (targeting, bids, performance)
  - **Keywords** (quality scores, match types, bids, performance)
  - **Search Terms** (actual user queries, match types, performance)
- Loads data into PostgreSQL with automatic deduplication

#### Usage

**Migrate All Clients (30 clients x 1 year):**
```bash
cd ads-monkee
poetry run python scripts/migrate_all_clients_data.py
```

**Estimated Time:** 30-45 minutes  
**Database Size:** ~50-100 MB

**Dry Run First (Recommended):**
```bash
poetry run python scripts/migrate_all_clients_data.py --dry-run
```

**Migrate Specific Clients:**
```bash
poetry run python scripts/migrate_all_clients_data.py --clients priority-roofing,heather-murphy-group
```

**Override Date Range (e.g., 180 days):**
```bash
poetry run python scripts/migrate_all_clients_data.py --days 180
```

#### Output
```
================================================================================
                      ADS MONKEE - CLIENT DATA MIGRATION                       
================================================================================

ℹ️  Date Range: 365 days (~12.1 months)
ℹ️  Mode: LIVE MIGRATION
ℹ️  Database: oregon-postgres.render.com/ads_monkee_db
✅ Google Ads API client initialized
✅ Found 30 clients in database

================================================================================
Progress: 1/30
================================================================================

================================================================================
                 MIGRATING: Priority Roofing (priority-roofing)                
================================================================================

ℹ️  Date Range: 2024-10-17 to 2025-10-17 (365 days)
ℹ️  Google Ads ID: 1234567890
ℹ️  [CAMPAIGNS] Fetching 2024-10-17 to 2025-10-17...
✅ [CAMPAIGNS] Fetched 156 rows
ℹ️  [AD GROUPS] Fetching 2024-10-17 to 2025-10-17...
✅ [AD GROUPS] Fetched 539 rows
ℹ️  [KEYWORDS] Fetching 2024-10-17 to 2025-10-17...
✅ [KEYWORDS] Fetched 1060 rows
ℹ️  [SEARCH TERMS] Fetching in 30-day chunks...
ℹ️    Chunk: 2024-10-17 to 2024-11-15
ℹ️      → 2841 rows
[... 11 more chunks ...]
✅ [SEARCH TERMS] Fetched 10298 total rows
✅ Total rows fetched: 12,053
ℹ️  [DB] Inserting 156 campaigns...
✅ [DB] Inserted 156 campaigns
ℹ️  [DB] Inserting 539 ad groups...
✅ [DB] Inserted 539 ad groups
ℹ️  [DB] Inserting 1060 keywords...
✅ [DB] Inserted 1060 keywords
ℹ️  [DB] Inserting 10298 search terms...
✅ [DB] Inserted 10298 search terms
✅ ✅ COMPLETED: Priority Roofing - 12,053 records inserted

[... 29 more clients ...]

================================================================================
                            MIGRATION COMPLETE                                 
================================================================================

✅ Successfully migrated: 30 clients
⚠️  No data found: 0 clients
❌ Failed: 0 clients

✅ ALL DONE!
```

#### Verification
```bash
# Check total records
poetry run python -c "
from backend.database import SessionLocal
from backend.models import GoogleAdsCampaign, GoogleAdsKeyword, GoogleAdsSearchTerm
s = SessionLocal()
print(f'Campaigns: {s.query(GoogleAdsCampaign).count():,}')
print(f'Keywords: {s.query(GoogleAdsKeyword).count():,}')
print(f'Search Terms: {s.query(GoogleAdsSearchTerm).count():,}')
s.close()
"
```

**Expected Output:**
```
Campaigns: 4,680
Keywords: 31,800
Search Terms: 308,940
```

---

### Phase 2: Historical Dataset (2-5 Years) 📊

**Script:** `scripts/backfill_historical_data.py`

#### What It Does
- Pulls 2-5 years of historical data (excluding last 12 months)
- Same 4 data types as operational dataset
- Loads into same tables with date-based separation
- Optimized for long-running queries (90-day chunking)

#### When to Run
- **After** operational migration is complete
- During off-hours (3-5 hour process)
- Optional but recommended for strategic insights

#### Usage

**Backfill 2 Years for All Clients:**
```bash
cd ads-monkee
poetry run python scripts/backfill_historical_data.py --years 2
```

**Estimated Time:** ~3-5 hours for 30 clients x 2 years  
**Database Size:** ~200-400 MB additional

**Dry Run First:**
```bash
poetry run python scripts/backfill_historical_data.py --years 2 --dry-run
```

**Backfill Single Client (Test):**
```bash
poetry run python scripts/backfill_historical_data.py --client priority-roofing --years 3
```

**Custom Historical Period:**
```bash
# Exclude last 18 months (instead of default 12)
poetry run python scripts/backfill_historical_data.py --years 5 --exclude-recent 18
```

#### Output
```
================================================================================
                   ADS MONKEE - HISTORICAL DATA BACKFILL                       
================================================================================

ℹ️  Historical Period: 2 years
ℹ️  Excluding Recent: Last 12 months (operational dataset)
ℹ️  Mode: LIVE BACKFILL
⚠️  ⏰ This process may take several hours for 30 clients x multiple years
⚠️  💾 Ensure sufficient database storage for historical data

Proceed with backfill? (yes/no): yes

✅ Google Ads API client initialized
✅ Found 30 clients to backfill
ℹ️  Estimated time: ~420 minutes (7.0 hours)

[... similar output to operational migration ...]

================================================================================
                           BACKFILL COMPLETE                                    
================================================================================

✅ Total historical records: 730,520
✅ Successfully backfilled: 30 clients

Top 10 clients by historical data volume:
   1. Priority Roofing: 48,212 rows
   2. Heather Murphy Group: 45,987 rows
   [...]

✅ HISTORICAL BACKFILL COMPLETE!

================================================================================
                     NEXT STEPS - HISTORICAL ANALYSIS                          
================================================================================

ℹ️  1. Run long-term trend analysis:
   poetry run python scripts/analyze_historical_trends.py --client priority-roofing
ℹ️  2. Discover historical winners:
   poetry run python scripts/find_historical_gems.py --min-roas 3.0
ℹ️  3. Compare seasonal patterns:
   poetry run python scripts/seasonal_analysis.py --years 2
```

---

## Data Structure

### Database Schema

**Core Tables (4):**
- `google_ads_campaigns` - Campaign-level daily performance
- `google_ads_ad_groups` - Ad group-level daily performance  
- `google_ads_keywords` - Keyword-level daily performance + quality scores
- `google_ads_search_terms` - Search term-level daily performance

**Key Fields:**
- `client_id` - Foreign key to `clients` table
- `date` - Daily granularity (YYYY-MM-DD)
- `campaign_id`, `ad_group_id`, `keyword_id` - Google Ads entity IDs
- Performance metrics: `impressions`, `clicks`, `cost`, `conversions`, `conversions_value`
- Derived metrics: `avg_cpc`, `avg_cpm`, quality scores, impression share

**Indexes:**
- Primary key: `(client_id, date, entity_id)` for fast lookups
- Composite indexes on `(client_id, date)` for date-range queries
- Index on `campaign_id`, `ad_group_id` for joins

### Sample Query (Operational Dataset)
```sql
-- Get last 30 days of campaign performance for Priority Roofing
SELECT 
    c.name AS client_name,
    campaign_name,
    SUM(impressions) AS impressions,
    SUM(clicks) AS clicks,
    SUM(cost) AS cost,
    SUM(conversions) AS conversions,
    SUM(conversions_value) AS revenue,
    SUM(conversions_value) / NULLIF(SUM(cost), 0) AS roas
FROM google_ads_campaigns gac
JOIN clients c ON gac.client_id = c.id
WHERE c.slug = 'priority-roofing'
  AND gac.date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY c.name, campaign_name
ORDER BY cost DESC;
```

### Sample Query (Historical Trend)
```sql
-- Compare year-over-year performance
SELECT 
    EXTRACT(YEAR FROM date) AS year,
    EXTRACT(MONTH FROM date) AS month,
    SUM(cost) AS monthly_spend,
    SUM(conversions) AS monthly_conversions,
    SUM(conversions_value) / NULLIF(SUM(cost), 0) AS roas
FROM google_ads_campaigns
WHERE client_id = (SELECT id FROM clients WHERE slug = 'priority-roofing')
  AND date >= CURRENT_DATE - INTERVAL '3 years'
GROUP BY EXTRACT(YEAR FROM date), EXTRACT(MONTH FROM date)
ORDER BY year, month;
```

---

## Troubleshooting

### Issue: "No clients found in database"
**Solution:**
```bash
# Seed clients first
poetry run python scripts/seed_clients.py

# Verify
poetry run python -c "from backend.database import SessionLocal; from backend.models import Client; s = SessionLocal(); print(s.query(Client).count()); s.close()"
```

### Issue: "Google Ads API permission denied"
**Check:**
1. `google-ads.yaml` exists in project root or `~/.google-ads.yaml`
2. Credentials are valid (try `ads_sync` CLI first)
3. Developer token is approved (not test account)

**Test:**
```bash
cd ads_sync
poetry run python scripts/discover_clients.py
```

### Issue: "Database connection refused"
**Check:**
1. `.env` file has correct `DATABASE_URL`
2. Database is "available" status in Render
3. IP allowlist includes your location (if set)

**Test:**
```bash
poetry run python -c "from backend.database import engine; engine.connect(); print('✅ Connected')"
```

### Issue: "Migrations not applied"
**Solution:**
```bash
# Check current migration version
poetry run alembic current

# If no output, run migrations
poetry run alembic upgrade head

# Verify tables exist
poetry run python -c "from sqlalchemy import inspect; from backend.database import engine; print(inspect(engine).get_table_names())"
```

### Issue: "Search term queries timing out"
**Cause:** Very large search term datasets (100k+ rows for 1 year)  
**Solution:** Already handled with 30-day chunking in script. If still timing out:
```bash
# Reduce to 180 days first
poetry run python scripts/migrate_all_clients_data.py --days 180 --clients large-client-slug

# Then backfill remaining 6 months separately
```

---

## Performance Optimization

### Database Tuning
```sql
-- Create additional indexes for common queries
CREATE INDEX idx_campaigns_client_date ON google_ads_campaigns(client_id, date DESC);
CREATE INDEX idx_keywords_quality ON google_ads_keywords(client_id, quality_score) WHERE quality_score IS NOT NULL;
CREATE INDEX idx_search_terms_cost ON google_ads_search_terms(client_id, cost DESC) WHERE cost > 0;
```

### Parallel Migration
For faster migration of 30 clients:
```bash
# Split clients into 3 batches and run in parallel terminals

# Terminal 1 (clients 1-10)
poetry run python scripts/migrate_all_clients_data.py --clients client1,client2,...,client10

# Terminal 2 (clients 11-20)
poetry run python scripts/migrate_all_clients_data.py --clients client11,client12,...,client20

# Terminal 3 (clients 21-30)
poetry run python scripts/migrate_all_clients_data.py --clients client21,client22,...,client30
```

**Reduces time from 45 minutes → 15 minutes**

---

## Migration Checklist

### Pre-Migration ☑️
- [ ] Database provisioned and available
- [ ] `.env` configured with DATABASE_URL
- [ ] Poetry dependencies installed
- [ ] Migrations applied (`alembic upgrade head`)
- [ ] Clients seeded (~30 clients)
- [ ] Google Ads API credentials valid

### Operational Migration (1 Year) ☑️
- [ ] Run dry-run: `--dry-run` flag
- [ ] Review output (check client count, date range)
- [ ] Run full migration: `migrate_all_clients_data.py`
- [ ] Verify record counts match expectations
- [ ] Spot-check Priority Roofing data in database
- [ ] Test sample queries (see "Sample Query" above)

### Historical Backfill (Optional) ☑️
- [ ] Operational migration complete
- [ ] Off-hours scheduled (3-5 hour window)
- [ ] Run dry-run: `--dry-run --years 2`
- [ ] Review storage capacity (200-400 MB additional)
- [ ] Run backfill: `backfill_historical_data.py --years 2`
- [ ] Verify historical date ranges in database
- [ ] Document historical data availability

### Post-Migration ☑️
- [ ] Create database backup/snapshot
- [ ] Run analysis script on 1-2 clients (test)
- [ ] Verify AI recommendations use new database
- [ ] Update dashboards to query PostgreSQL
- [ ] Archive old CSV files to `ads_sync/archive/`
- [ ] Document migration completion date

---

## Next Steps After Migration

### 1. Analysis Scripts
```bash
# Comprehensive PPC analysis (uses new DB)
poetry run python backend/services/ppc_analyzer.py --client priority-roofing

# Multi-client insights
poetry run python scripts/cross_client_analysis.py --top 10
```

### 2. API Endpoints
Start the FastAPI server to access data via REST API:
```bash
poetry run uvicorn backend.main:app --reload

# Test endpoint
curl http://localhost:8000/api/v1/clients/priority-roofing/campaigns?days=30
```

### 3. Dashboard Integration
Point React dashboard to new API:
```javascript
// frontend/src/services/api.ts
const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export async function getCampaignData(clientSlug: string, days: number = 30) {
  const response = await fetch(`${API_BASE}/api/v1/clients/${clientSlug}/campaigns?days=${days}`);
  return response.json();
}
```

### 4. Schedule Automated Syncs
Set up daily data updates:
```bash
# Via Celery Beat (preferred)
# Edit backend/workers/celery_app.py to add schedule

# Or via cron (simple)
# crontab -e
0 8 * * * cd /path/to/ads-monkee && poetry run python scripts/daily_sync.py
```

---

## Success Metrics

After successful migration, you should have:

| Metric | Expected Value |
|--------|----------------|
| **Clients Migrated** | 30 |
| **Operational Data (1Y)** | ~300k-500k rows |
| **Historical Data (2Y)** | ~700k-1M rows |
| **Database Size** | 100-500 MB |
| **Migration Time** | 30-45 min (operational) |
| **API Response Time** | <200ms for 30-day queries |
| **Dashboard Load Time** | <2 seconds |

---

## Support & Troubleshooting

**Documentation:**
- `ads-monkee/sds/SBEP-MANDATE.md` - Project operating principles
- `ads-monkee/docs/DATABASE-REQUIREMENTS.md` - Database setup
- `ads-monkee/CHANGELOG.md` - Recent changes

**Logs:**
- Migration logs: Console output (pipe to file if needed)
- Database logs: Render dashboard → Database → Logs
- API logs: `backend/logs/` directory

**Common Commands:**
```bash
# Verify migration status
poetry run python -c "
from backend.database import SessionLocal
from backend.models import *
s = SessionLocal()
print('Clients:', s.query(Client).count())
print('Campaigns:', s.query(GoogleAdsCampaign).count())
print('Keywords:', s.query(GoogleAdsKeyword).count())
print('Search Terms:', s.query(GoogleAdsSearchTerm).count())
s.close()
"

# Reset and re-migrate (if needed)
poetry run alembic downgrade base
poetry run alembic upgrade head
poetry run python scripts/seed_clients.py
poetry run python scripts/migrate_all_clients_data.py
```

---

## Appendix: Migration Script Reference

### migrate_all_clients_data.py
**Purpose:** Operational dataset (1 year)  
**Data Types:** Campaigns, Ad Groups, Keywords, Search Terms  
**Chunking:** 30-day for search terms  
**Time:** ~45 minutes for 30 clients  

**Arguments:**
- `--days N` - Days of data (default: 365)
- `--clients slug1,slug2` - Specific clients only
- `--dry-run` - Fetch but don't insert

### backfill_historical_data.py
**Purpose:** Historical dataset (2-5 years)  
**Data Types:** Same as operational  
**Chunking:** 30-day for search terms  
**Time:** ~3-5 hours for 30 clients x 2 years  

**Arguments:**
- `--years N` - Years of historical data (default: 2)
- `--client slug` - Single client only
- `--exclude-recent N` - Don't overlap with last N months (default: 12)
- `--dry-run` - Fetch but don't insert

---

**✅ Migration Complete! Your Ads Monkee database is ready for production.**

