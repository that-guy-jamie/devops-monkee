# Ads Monkee - 48-Hour Launch Plan

**Goal:** Get database live, data flowing, and first API endpoint working  
**Based on:** GPT Analysis + Development Agent Build  
**Status:** Ready to Execute

---

## ✅ Pre-Flight Check (Already Complete)

- [x] SBEP v2.0 compliant structure
- [x] 14 database tables designed (8 models)
- [x] Alembic migrations configured
- [x] Seed scripts ready
- [x] FastAPI app scaffolded
- [x] Documentation complete

**You have ~3,300 lines of production code ready to deploy.**

---

## 🚀 48-Hour Execution Plan

### Hour 0-2: Database Provisioning

**Action:** Provision Postgres on Render with another agent

```bash
# Use docs/DATABASE-REQUIREMENTS.md as guide
# Expected deliverable: DATABASE_URL connection string
```

**Deliverable:**
- Render Postgres 16 (Pro 4GB) provisioned
- `.env` file created with `DATABASE_URL`
- Connection test passes

---

### Hour 2-3: Run Migrations & Seed Clients

**Action:** Create schema and populate clients

```bash
cd ads-monkee

# Generate initial migration
poetry run alembic revision --autogenerate -m "Initial schema - 14 tables"

# Apply migration
poetry run alembic upgrade head

# Seed clients from Google Ads API (~30 clients)
poetry run python scripts/seed_clients.py
```

**Deliverable:**
- 14 tables created in Postgres
- ~30 client records populated
- Verified via SQL query: `SELECT COUNT(*) FROM clients;`

---

### Hour 3-8: Google Ads Sync Service

**Action:** Port ads_sync data pull to Postgres

**Create:** `backend/services/google_ads_sync.py`

```python
class GoogleAdsSync:
    """
    Sync Google Ads data to Postgres.
    Based on ads_sync/scripts/comprehensive_data_pull.py
    """
    
    async def sync_client_data(
        self,
        client_id: int,
        start_date: str,
        end_date: str
    ) -> dict:
        """
        Pull and store Google Ads data for a client.
        
        Writes to:
        - google_ads_campaigns
        - google_ads_ad_groups
        - google_ads_keywords
        - google_ads_search_terms
        
        Returns sync summary.
        """
        pass  # Port from ads_sync
```

**Migration Strategy:**
1. Keep existing CSV writes working
2. Add Postgres inserts alongside
3. Verify data matches
4. Retire CSVs after confirmation

**Test:**
```bash
# Sync one small client (90 days)
poetry run python scripts/test_sync.py --client donaldson-educational-services --days 90
```

**Deliverable:**
- Google Ads sync service working
- Data flowing to Postgres
- One test client fully synced

---

### Hour 8-12: LSA Integration (Careful - Don't Break Existing)

**Action:** Create parallel LSA ingestion to Postgres

**Strategy (Per GPT):**
- **DO NOT** break existing LSA monitor
- Read from current JSON/SQLite
- Write to Postgres **alongside** existing storage
- Honor "charged-only" rule
- Maintain dual-flag survey logic

**Create:** `backend/services/lsa_sync.py`

```python
class LSASync:
    """
    Sync LSA data to Postgres without breaking existing monitor.
    """
    
    async def backfill_from_existing(self):
        """
        One-time: Import existing LSA JSON/SQLite → Postgres
        Filter: charged leads only
        Preserve: dual-flag survey tracking
        """
        pass
    
    async def sync_daily(self):
        """
        Daily: Fetch new LSA leads → Postgres
        Runs alongside existing monitor
        """
        pass
```

**Models Needed (Add to backend/models/):**
```python
# backend/models/lsa.py
class LSALead(BaseModel):
    __tablename__ = "lsa_leads"
    client_id = Column(Integer, ForeignKey("clients.id"))
    lead_id = Column(String, unique=True)  # Google's lead ID
    charged = Column(Boolean, default=False)  # CRITICAL filter
    survey_sent_google = Column(Boolean, default=False)
    survey_sent_internal = Column(Boolean, default=False)
    # ... more fields
```

**Test:**
```bash
# Backfill existing LSA data
poetry run python scripts/backfill_lsa.py

# Verify charged-only filter
psql $DATABASE_URL -c "SELECT COUNT(*) FROM lsa_leads WHERE charged = true"
```

**Deliverable:**
- LSA models added
- Migration generated and applied
- Historical LSA data in Postgres
- Existing LSA monitor still working

---

### Hour 12-16: Unified API Endpoint

**Action:** Implement first API endpoint

**Create:** `backend/api/routes/clients.py`

```python
@router.get("/{client_id}/summary")
async def get_client_summary(
    client_id: int,
    start_date: date,
    end_date: date,
    db: AsyncSession = Depends(get_db)
) -> ClientSummary:
    """
    Unified summary: Google Ads + LSA + Call Tracking
    
    Returns:
    {
        "client": {...},
        "date_range": {"start": "...", "end": "..."},
        "google_ads": {
            "spend": 16418.32,
            "conversions": 257,
            "roas": 2.15
        },
        "lsa": {
            "leads": 45,
            "charged_leads": 42,
            "surveys_sent": 38
        },
        "totals": {
            "total_spend": ...,
            "total_conversions": ...,
            "blended_roas": ...
        }
    }
    """
    pass
```

**Test:**
```bash
# Hit API with curl
curl "http://localhost:8000/api/clients/1/summary?start_date=2025-09-15&end_date=2025-10-15"
```

**Deliverable:**
- API endpoint working
- Returns unified metrics
- CORS enabled for frontend

---

### Hour 16-20: Minimal Dashboard

**Action:** Create basic React dashboard OR extend existing Node dashboard

**Option A: React (New)**
```bash
cd ads-monkee/frontend
npm create vite@latest . -- --template react-ts
npm install
npm install recharts axios @tanstack/react-query
```

**Option B: Extend LSA Monitor Dashboard**
- Add Ads Monkee API client
- Create unified view component
- Keep existing LSA views working

**Components Needed:**
- Client list with last sync times
- Date range picker
- Summary cards (Spend, Conversions, ROAS)
- LSA vs Search tile

**Deliverable:**
- Dashboard running locally
- Shows 7 clients
- Displays unified metrics for one client

---

### Hour 20-24: Celery Task for Daily Sync

**Action:** Automate daily Google Ads sync

**Create:** `backend/workers/sync_tasks.py`

```python
@celery.task
def sync_all_clients_daily():
    """
    Daily sync task (runs at 2 AM)
    - Pull last 7 days of Google Ads data
    - Update all active clients
    - Log results to audit_log
    """
    pass
```

**Configure Celery Beat:**
```python
# backend/workers/celery_app.py
app.conf.beat_schedule = {
    'sync-google-ads-daily': {
        'task': 'backend.workers.sync_tasks.sync_all_clients_daily',
        'schedule': crontab(hour=2, minute=0),
    },
}
```

**Test:**
```bash
# Run worker
poetry run celery -A backend.workers.celery_app worker --pool=solo --loglevel=info

# Run beat (scheduler)
poetry run celery -A backend.workers.celery_app beat --loglevel=info

# Trigger manually
poetry run celery -A backend.workers.celery_app call backend.workers.sync_tasks.sync_all_clients_daily
```

**Deliverable:**
- Celery worker running
- Daily sync task scheduled
- Manual trigger works

---

## 📋 Week-1 Success Criteria (GPT's Deliverables)

After 48 hours, you'll have:

1. ✅ **DB live + migrations applied + seed clients visible**
2. ✅ **Daily Google Ads sync writing to PG** (90-day backfill for one client)
3. ✅ **LSA backfill into PG** (charged-only + dual-flag respected)
4. ✅ **FastAPI `/clients/{id}/summary`** endpoint returning unified metrics
5. ✅ **Tiny dashboard** listing clients + LSA vs Search totals

---

## 🚨 Critical Guardrails (Per GPT Analysis)

### LSA Integration Rules
1. **Charged leads only** - Filter `WHERE charged = true`
2. **Dual-flag tracking** - Both Google boolean AND internal ledger
3. **Write-only survey API** - Can't read back, must track locally
4. **Don't break existing** - Parallel writes, not replacement

### Google Ads Integration Rules
1. **Respect rate limits** - 10K operations/day
2. **Use MCC auth** - For cross-account access
3. **30-day chunks** - For search terms (avoid timeouts)
4. **Idempotent writes** - UPSERT not INSERT (handle re-runs)

### SBEP Requirements
1. **Audit all mutations** - Every write → `audit_log`
2. **Archive, don't delete** - Old CSVs → `archive/`
3. **Rollback plans** - Every migration has `downgrade()`
4. **Documentation first** - Update docs before breaking changes

---

## 🔧 Scripts to Create

### 1. Test Sync Script
```python
# scripts/test_sync.py
"""
Test Google Ads sync on one client.
Usage: poetry run python scripts/test_sync.py --client priority-roofing --days 90
"""
```

### 2. LSA Backfill Script
```python
# scripts/backfill_lsa.py
"""
One-time: Import existing LSA data into Postgres.
Reads from: jamie_lcs-system/ (existing JSON/SQLite)
Writes to: lsa_leads table
Filter: charged = true only
"""
```

### 3. Data Validation Script
```python
# scripts/validate_sync.py
"""
Compare CSV data vs Postgres data.
Ensure migration didn't lose anything.
"""
```

---

## 📊 Success Metrics

**After 48 Hours:**
- [ ] Postgres has ~30 client records
- [ ] At least 1 client has full Google Ads data (90 days)
- [ ] LSA leads table populated (charged only)
- [ ] API endpoint returns valid JSON
- [ ] Dashboard shows at least one client's data
- [ ] Daily sync runs successfully (manual trigger)

**Data Volume Check:**
```sql
-- Expected row counts after 48 hours
SELECT 
    'clients' as table_name, COUNT(*) as rows FROM clients
UNION ALL
SELECT 'google_ads_campaigns', COUNT(*) FROM google_ads_campaigns
UNION ALL
SELECT 'google_ads_keywords', COUNT(*) FROM google_ads_keywords
UNION ALL
SELECT 'lsa_leads', COUNT(*) FROM lsa_leads;

-- Expected:
-- clients: ~30
-- google_ads_campaigns: ~500 (1 client × 5 campaigns × 90 days)
-- google_ads_keywords: ~3000
-- lsa_leads: ~100+
```

---

## 🎯 What NOT to Do (Risk Mitigation)

1. ❌ **Don't break existing LSA monitor** - Parallel writes only
2. ❌ **Don't delete CSV files yet** - Keep until verified in PG
3. ❌ **Don't sync all 30 clients at once** - Start with 1, scale up
4. ❌ **Don't skip the test sync** - Validate on small client first
5. ❌ **Don't push to production** - This is dev/staging only

---

## 🚀 Ready to Launch?

**Prerequisites:**
- [ ] DATABASE_URL obtained from Render
- [ ] `.env` file created
- [ ] Google Ads credentials confirmed working
- [ ] Redis available (local or Render)

**First Command:**
```bash
cd ads-monkee
poetry run alembic upgrade head
```

**If that works, you're off to the races!** 🏎️

---

**Questions Before Starting?**
- Database tier (Pro 4GB confirmed?)
- Redis setup (local or Render?)
- Which client to test sync first?

**Let's go! 🚀**

