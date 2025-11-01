# Week 1 Implementation Plan - AI Analysis MVP

**Goal**: Wire up the skeleton - Celery/Redis, aggregates, focus views, and core schemas.

**Reference**: `docs/AI-ANALYSIS-ARCHITECTURE.md`

---

## Checklist

### 1. Infrastructure Setup
- [x] Add Celery + Redis dependencies to `pyproject.toml`
- [x] Create Celery configuration (`backend/celery_app.py`)
- [x] Add Redis connection to `backend/config.py` (already present)
- [ ] Test Celery worker startup (pending Redis provisioning)

### 2. Database Schema - Aggregates & Focus Views
- [x] Create `targets` table (client goals: CPA, ROAS, budgets)
- [x] Create aggregate tables:
  - [x] `agg_campaign_daily`
  - [x] `agg_adgroup_daily`
  - [x] `agg_keyword_daily`
  - [x] `agg_search_term_daily`
- [x] Create materialized views:
  - [x] `focus_keywords_30d`
  - [x] `focus_search_terms_30d`
  - [ ] `focus_segments_30d` (deferred to v2)
- [x] Generate Alembic migration
- [x] Apply migration to database

### 3. Analysis Schema
- [x] Create `analysis_runs` table
- [x] Create `analysis_reports` table
- [x] Create `recommendations` table (normalized)
- [x] Create `decisions` table (approve/reject tracking)
- [x] Create `actions_executed` table (audit trail)
- [x] Generate Alembic migration (combined with #2)
- [x] Apply migration

### 4. Pydantic Schemas
- [x] Create `backend/schemas/analysis.py`:
  - [x] `Recommendation` model
  - [x] `Synthesis` model
  - [x] `AnalysisRun` model
  - [x] `AnalysisReport` model
  - [x] `ParallelCampaignProposal` model
  - [x] `AnalysisContext` model (internal)
- [x] Add validation rules
- [ ] Test schema validation (will test in Week 2 with real data)

### 5. Celery Tasks (Skeleton)
- [x] Create `backend/tasks/__init__.py`
- [x] Create `backend/tasks/analysis.py`:
  - [x] `prepare_data_task` (stub)
  - [x] `analyze_keywords_and_queries` (stub)
  - [x] `analyze_bidding` (stub)
  - [x] `synthesize_task` (stub)
  - [x] `persist_task` (stub)
  - [x] `run_full_analysis` (chain)
- [ ] Test task execution with dummy data (pending Redis/Celery worker)

### 6. FastAPI Endpoints (202 Pattern)
- [x] Create `backend/routers/analysis.py`:
  - [x] `POST /api/analysis/clients/{id}/analyze` → 202 + run_id
  - [x] `GET /api/analysis/{run_id}` → status + results
  - [x] `GET /api/analysis/clients/{id}/analyses` → list analyses
- [x] Register router in `backend/main.py`
- [ ] Test endpoints with curl/Postman (pending Redis/Celery worker)

### 7. Testing & Validation
- [ ] Test Celery worker startup (pending Redis provisioning)
- [ ] Test task chain execution (pending Redis/Celery worker)
- [ ] Test 202 API pattern (pending Redis/Celery worker)
- [x] Verify database schema (migration applied successfully)
- [x] Test materialized view refresh (views created successfully)

---

## Implementation Order

### Day 1-2: Infrastructure
1. Add dependencies
2. Configure Celery + Redis
3. Test worker startup

### Day 3-4: Database
1. Create aggregate tables + models
2. Create focus views
3. Create analysis tables
4. Generate and apply migrations
5. Seed `targets` table with Priority Roofing goals

### Day 5-6: Celery + API
1. Create Pydantic schemas
2. Implement stub Celery tasks
3. Create FastAPI endpoints
4. Test end-to-end flow

### Day 7: Testing & Documentation
1. Integration testing
2. Update documentation
3. Prepare for Week 2

---

## Success Criteria

By end of Week 1:
- ✅ Celery worker running and processing tasks
- ✅ Database has all aggregate tables and focus views
- ✅ API returns 202 and creates analysis runs
- ✅ Task chain executes (even with stub implementations)
- ✅ Can query analysis run status
- ✅ All migrations applied successfully

---

## Commands Reference

### Start Celery Worker
```bash
cd ads-monkee
poetry run celery -A backend.celery_app worker --loglevel=info
```

### Test Analysis Endpoint
```bash
curl -X POST http://localhost:8000/api/clients/1/analyze
# Returns: {"run_id": "uuid", "status": "queued"}

curl http://localhost:8000/api/analysis/{run_id}
# Returns: {"status": "running", ...}
```

### Refresh Materialized Views
```sql
REFRESH MATERIALIZED VIEW focus_keywords_30d;
REFRESH MATERIALIZED VIEW focus_search_terms_30d;
```

---

## Notes

- Keep all tasks as **stubs** for Week 1 - just return dummy data
- Focus on **infrastructure and plumbing**
- Week 2 will implement the actual AI logic
- Test with Priority Roofing data (client_id=1)

