# Ads Monkee - Quick Start: Data Migration

**🎯 Goal:** Migrate all 30 clients' Google Ads data (1 year operational + optional historical) to PostgreSQL

**⏱️ Time:** 30-45 minutes (operational) + 3-5 hours (historical, optional)

---

## Prerequisites Checklist

```bash
# 1. Database is ready (check Render dashboard)
✅ https://dashboard.render.com/d/dpg-d3oouas9c44c738cl2sg-a

# 2. Get connection strings (once status = "available")
# Copy EXTERNAL URL for local development
# Copy INTERNAL URL for Render services

# 3. Configure environment
cd ads-monkee
cp env.example .env
# Edit .env and add DATABASE_URL (EXTERNAL)

# 4. Install dependencies
poetry install

# 5. Run migrations
poetry run alembic upgrade head

# 6. Seed clients
poetry run python scripts/seed_clients.py
# Expected: ~30 clients created
```

---

## Migration: 3 Simple Commands

### 1. Dry Run (Recommended First)
```bash
cd ads-monkee
poetry run python scripts/migrate_all_clients_data.py --dry-run
```

**Look for:**
- ✅ "Found 30 clients in database"
- ✅ Date range: ~365 days
- ✅ "Would insert" messages for each client

### 2. Full Migration (1 Year, All Clients)
```bash
poetry run python scripts/migrate_all_clients_data.py
```

**Estimated:** 30-45 minutes  
**Data:** ~300k-500k rows  
**Size:** ~50-100 MB

### 3. Historical Backfill (Optional, 2-5 Years)
```bash
# Run after operational migration completes
poetry run python scripts/backfill_historical_data.py --years 2
```

**Estimated:** 3-5 hours  
**Data:** ~700k-1M rows  
**Size:** ~200-400 MB

---

## Verify Success

```bash
# Check record counts
poetry run python -c "
from backend.database import SessionLocal
from backend.models import GoogleAdsCampaign, GoogleAdsKeyword, GoogleAdsSearchTerm
s = SessionLocal()
print(f'✅ Campaigns: {s.query(GoogleAdsCampaign).count():,}')
print(f'✅ Keywords: {s.query(GoogleAdsKeyword).count():,}')
print(f'✅ Search Terms: {s.query(GoogleAdsSearchTerm).count():,}')
s.close()
"
```

**Expected (operational only):**
- Campaigns: ~4,500-5,000
- Keywords: ~30,000-40,000
- Search Terms: ~300,000-400,000

---

## Quick Test: Priority Roofing

```bash
# Query last 30 days of campaign data
poetry run python -c "
from backend.database import SessionLocal
from backend.models import GoogleAdsCampaign, Client
from sqlalchemy import func
from datetime import datetime, timedelta

s = SessionLocal()
client = s.query(Client).filter_by(slug='priority-roofing').first()

cutoff = datetime.now().date() - timedelta(days=30)
campaigns = s.query(
    GoogleAdsCampaign.campaign_name,
    func.sum(GoogleAdsCampaign.cost).label('cost'),
    func.sum(GoogleAdsCampaign.conversions).label('conversions')
).filter(
    GoogleAdsCampaign.client_id == client.id,
    GoogleAdsCampaign.date >= cutoff
).group_by(GoogleAdsCampaign.campaign_name).all()

print('Priority Roofing - Last 30 Days:')
for camp in campaigns:
    print(f'  {camp.campaign_name}: ${camp.cost:.2f}, {camp.conversions:.0f} conv')

s.close()
"
```

---

## Troubleshooting

### "No clients found in database"
```bash
poetry run python scripts/seed_clients.py
```

### "Database connection refused"
Check `.env` file has correct `DATABASE_URL` (EXTERNAL URL)

### "Migrations not applied"
```bash
poetry run alembic upgrade head
```

### "Google Ads API error"
Check `google-ads.yaml` exists in project root or `~/.google-ads.yaml`

---

## Next Steps After Migration

### 1. Start API Server
```bash
poetry run uvicorn backend.main:app --reload
# Test: http://localhost:8000/health
```

### 2. Run Analysis
```bash
poetry run python backend/services/ppc_analyzer.py --client priority-roofing
```

### 3. Deploy to Render
```bash
git add .
git commit -m "feat: complete data migration"
git push

# Then in Render dashboard:
# New + → Blueprint → Select repo/branch → Apply
```

---

## Full Documentation

- **Complete Guide:** `docs/DATA-MIGRATION-GUIDE.md`
- **Infrastructure:** `INFRASTRUCTURE-PROVISIONED.md`
- **Database Setup:** `docs/DATABASE-REQUIREMENTS.md`
- **SBEP Protocol:** `sds/SBEP-MANDATE.md`

---

**✅ You're ready to migrate! Start with the dry run, then run the full migration.**

**Estimated total time:** 45 minutes active (monitoring), then walk away for historical backfill.

