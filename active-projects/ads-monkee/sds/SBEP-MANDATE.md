# Ads Monkee - SBEP Project Mandate

**Project:** Ads Monkee  
**Type:** Unified Digital Advertising Platform  
**Status:** Active Development  
**Created:** 2025-10-16  
**SBEP Version:** 2.2

---

## Project Overview

**Ads Monkee** is a unified digital advertising management platform that integrates:
- Google Ads data synchronization and analysis (ads_sync)
- LSA (Local Services Ads) monitoring
- Local Call Generator (LCG) call tracking
- Multi-agent AI consensus analysis
- Campaign modification approval workflows
- GoHighLevel (GHL) client portal integration

**Mission:** Provide a single, powerful supervisor dashboard for staff to manage all digital advertising services across 30+ clients, with role-based access for both staff and clients.

---

## Technology Stack

### Backend
- **Framework:** FastAPI (Python 3.12)
- **Database:** PostgreSQL 16 on Render
- **ORM:** SQLAlchemy 2.0
- **Task Queue:** Celery with Redis broker
- **API Integrations:** Google Ads API v21, GoHighLevel API v2, Claude API (Anthropic)

### Frontend
- **Framework:** React 18 with TypeScript
- **Styling:** Tailwind CSS
- **Charts:** Recharts
- **State Management:** React Query + Zustand
- **Build:** Vite

### Infrastructure
- **Platform:** Render (Web Service, Worker, Postgres, Redis, Static Site)
- **CI/CD:** Render auto-deploy from GitLab
- **Monitoring:** Render metrics + custom logging

---

## Architecture Principles

### 1. Hybrid Database Architecture
- **Shared Tables:** `clients`, `users`, `auth_sessions`, `reports`, `approvals`, `audit_log`
- **Product-Specific:** Separate table namespaces for Google Ads, LSA, Call Tracking
- **AI/Workflow:** Analysis tracking, consensus sessions, campaign modifications

### 2. Service-Oriented Backend
All business logic is encapsulated in service classes:
- `GoogleAdsSync` - Data synchronization
- `PPCAnalyzer` - Campaign analysis
- `MultiAgentAnalyzer` - AI consensus orchestration
- `CampaignStrategist` - Recommendation-to-action conversion
- `CampaignExecutor` - Google Ads API mutations
- `GHLIntegration` - GoHighLevel sync and notifications

### 3. Role-Based Access Control (RBAC)
Three distinct user roles:
- **Staff (Admin):** Full access, approval authority, execution control
- **Staff (Analyst):** Analysis and reporting, no approval/execution
- **Client:** Own data only, simplified dashboard, read-only

### 4. Multi-Agent AI Consensus
```
Analysis Request
    ↓
Analyst 1 (Python) → Analysis A
    ↓
Analyst 2 (Claude) → Analysis B
    ↓
Similarity Check (>85%?)
    ↓ YES              ↓ NO
Synthesize     Analyst 3 (Claude) → Analysis C
    ↓                  ↓
    ↓          Consensus Round (Debate)
    ↓                  ↓
    └──── Strategist (Action Plan) ────┘
```

### 5. Approval-First Execution
- All AI recommendations generate **proposed modifications**
- Modifications enter `pending` state
- Staff reviews in granular dashboard
- Only **approved** modifications execute via API
- Full audit trail with rollback capability

---

## Critical Implementation Rules

### Security & Authentication
- **No hardcoded credentials** - All sensitive data in environment variables
- **GHL OAuth only** - No password auth, leverage existing GHL infrastructure
- **JWT sessions** - Token-based with expiration
- **Row-level security** - Database queries always filter by user permissions

### Data Integrity
- **All writes are atomic** - Use database transactions
- **Idempotent operations** - Safe to retry
- **Audit everything** - `audit_log` table captures all mutations
- **Soft deletes** - Never hard-delete client data

### API Integration
- **Rate limiting** - Respect Google Ads API quotas (10K operations/day)
- **Retry with exponential backoff** - Graceful degradation
- **Webhook validation** - Verify GHL webhook signatures
- **Error recovery** - Store failed operations for manual review

### Testing Requirements (Per SBEP 2.0)
- **Unit tests** for all service classes
- **Integration tests** for API endpoints and Celery tasks
- **E2E tests** for critical workflows (Run Analysis → Approve → Execute)
- **Client size validation** - Test on small (1K rows), medium (6K rows), large (25K rows)

---

## Project Structure

```
ads-monkee/
├── sds/
│   ├── SBEP-MANDATE.md          ← You are here
│   └── SBEP-INDEX.yaml          ← Documentation inventory
├── README.md
├── CHANGELOG.md
├── .env.example
├── pyproject.toml               ← Poetry dependencies
├── backend/
│   ├── __init__.py
│   ├── main.py                  ← FastAPI app entry
│   ├── config.py                ← Environment config
│   ├── database.py              ← SQLAlchemy setup
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── auth.py
│   │   │   ├── clients.py
│   │   │   ├── analysis.py
│   │   │   ├── modifications.py
│   │   │   └── reports.py
│   │   └── deps.py              ← Dependency injection
│   ├── models/
│   │   ├── __init__.py
│   │   ├── client.py
│   │   ├── user.py
│   │   ├── google_ads.py
│   │   ├── lsa.py
│   │   ├── call_tracking.py
│   │   ├── analysis.py
│   │   └── campaign_modification.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── google_ads_sync.py
│   │   ├── ppc_analyzer.py
│   │   ├── ai_consensus.py
│   │   ├── strategist.py
│   │   ├── campaign_executor.py
│   │   ├── lsa_monitor.py
│   │   └── call_tracking.py
│   ├── integrations/
│   │   ├── __init__.py
│   │   ├── google_ads_client.py
│   │   ├── ghl_client.py
│   │   └── claude_client.py
│   └── workers/
│       ├── __init__.py
│       ├── celery_app.py
│       ├── sync_tasks.py
│       ├── analysis_tasks.py
│       └── ghl_tasks.py
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Dashboard/
│   │   │   ├── Analysis/
│   │   │   ├── Modifications/
│   │   │   └── Clients/
│   │   ├── pages/
│   │   ├── hooks/
│   │   ├── services/
│   │   └── App.tsx
│   ├── package.json
│   └── vite.config.ts
├── database/
│   ├── migrations/               ← Alembic migrations
│   └── schema.sql                ← Initial schema
├── scripts/
│   ├── init_db.py
│   ├── migrate_ads_sync_data.py
│   └── seed_clients.py
├── ops/
│   ├── deploy.sh
│   ├── backup.sh
│   └── render.yaml               ← Render configuration
├── docs/
│   ├── architecture.md
│   ├── api-reference.md
│   ├── deployment-guide.md
│   ├── user-guide-staff.md
│   └── user-guide-client.md
└── tests/
    ├── unit/
    ├── integration/
    └── e2e/
```

---

## Environment Variables

Create `.env` (never commit) based on `.env.example`:

```bash
# Database
DATABASE_URL=postgresql://user:pass@postgres.render.com/ads_monkee

# Redis
REDIS_URL=redis://redis.render.com:6379

# Google Ads API
GOOGLE_ADS_DEVELOPER_TOKEN=...
GOOGLE_ADS_CLIENT_ID=...
GOOGLE_ADS_CLIENT_SECRET=...
GOOGLE_ADS_REFRESH_TOKEN=...
GOOGLE_ADS_LOGIN_CUSTOMER_ID=...

# GoHighLevel OAuth
GHL_CLIENT_ID=...
GHL_CLIENT_SECRET=...
GHL_REDIRECT_URI=https://ads-monkee.onrender.com/auth/ghl/callback

# Claude API
ANTHROPIC_API_KEY=sk-ant-...

# App Config
JWT_SECRET=...
ENVIRONMENT=production
LOG_LEVEL=INFO
```

---

## Quick Start (Development)

1. **Setup:**
   ```bash
   cd ads-monkee
   poetry install
   cp .env.example .env
   # Edit .env with real credentials
   ```

2. **Initialize Database:**
   ```bash
   poetry run alembic upgrade head
   poetry run python scripts/seed_clients.py
   ```

3. **Run Backend:**
   ```bash
   poetry run uvicorn backend.main:app --reload
   ```

4. **Run Worker:**
   ```bash
   poetry run celery -A backend.workers.celery_app worker --pool=solo --loglevel=info
   ```

5. **Run Frontend:**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

---

## Deployment (Render)

Use Render MCP tools:

```python
# Provision infrastructure
mcp_render_create_postgres(name="ads-monkee-db", plan="pro_4gb")
mcp_render_create_key_value(name="ads-monkee-redis", plan="starter")
mcp_render_create_web_service(
    name="ads-monkee-api",
    runtime="python",
    build_command="poetry install --no-dev",
    start_command="uvicorn backend.main:app --host 0.0.0.0 --port $PORT"
)
mcp_render_create_web_service(
    name="ads-monkee-worker",
    runtime="python",
    build_command="poetry install --no-dev",
    start_command="celery -A backend.workers.celery_app worker --pool=solo"
)
mcp_render_create_static_site(
    name="ads-monkee-frontend",
    build_command="cd frontend && npm install && npm run build",
    publish_path="frontend/dist"
)
```

---

## Key Workflows

### 1. Data Sync (Automated via Celery Beat)
```
Cron: Daily 2am → sync_google_ads_data()
    ↓
For each client:
    - Pull campaigns, ad_groups, keywords, search_terms (last 7 days)
    - Deduplicate and insert into Postgres
    - Update client.last_sync_at
```

### 2. Analysis Request (Manual or Scheduled)
```
Staff triggers analysis → POST /api/analysis
    ↓
Celery task: run_comprehensive_analysis()
    ↓
Multi-agent consensus (Python + Claude x2)
    ↓
Strategist generates action plan
    ↓
Store analysis + proposed modifications (status=pending)
    ↓
Notify staff via dashboard + email
```

### 3. Approval & Execution
```
Staff reviews in dashboard
    ↓
Edit/Approve/Reject modifications
    ↓
Batch approve → Celery task: execute_approved_modifications()
    ↓
For each approved modification:
    - Call Google Ads API
    - Update status (applied/failed)
    - Log to audit_log
    - Notify staff of results
```

### 4. Client Report Delivery (GHL Integration)
```
Analysis complete → generate_client_report()
    ↓
Convert to PDF (client-friendly version)
    ↓
Upload to GHL contact files
    ↓
Send GHL notification (email + SMS)
    ↓
Update GHL custom fields (spend, conversions, ROAS)
```

---

## Testing Strategy

### Unit Tests (`tests/unit/`)
- Service class methods
- Utility functions
- Data validation
- Similarity scoring

### Integration Tests (`tests/integration/`)
- Database operations
- API endpoint responses
- Celery task execution
- External API mocks (Google Ads, GHL)

### E2E Tests (`tests/e2e/`)
- Full workflow: Login → Run Analysis → Review → Approve → Execute
- Client dashboard access
- GHL webhook processing

### Client Size Validation
Test on real client data:
1. **Small:** donaldson-educational-services (~1K rows)
2. **Medium:** priority-roofing (~6K rows)
3. **Large:** heather-murphy-group (~25K rows)

**Success Criteria:**
- Analysis completes in <60s for large clients
- No memory leaks during multi-agent consensus
- API mutations succeed with proper error handling

---

## Migration Plan (From Existing Systems)

### Phase 1: ads_sync → Ads Monkee
1. Copy `ads_sync/scripts/comprehensive_data_pull.py` → `backend/services/google_ads_sync.py`
2. Refactor CSV writes to Postgres inserts
3. Migrate existing CSV data using `scripts/migrate_ads_sync_data.py`
4. Keep old CSVs in `ads_sync/archive/` for rollback

### Phase 2: LCG Integration
1. Review `jamie_lcs-system/server.js`
2. Extract call tracking logic → Python service
3. Design `call_tracking_events` table
4. Build API endpoints for webhook ingestion

### Phase 3: LSA Integration
1. Identify existing LSA implementation
2. Extract monitoring logic
3. Design `lsa_leads` and `lsa_surveys` tables
4. Build dashboard components

---

## Troubleshooting

### Google Ads API Errors
- **RESOURCE_EXHAUSTED:** Rate limit hit, implement exponential backoff
- **AUTHENTICATION_ERROR:** Refresh OAuth token via refresh_token
- **INVALID_ARGUMENT:** Check GAQL query syntax, validate field compatibility

### Celery Task Failures
- Check Redis connection: `redis-cli ping`
- Review worker logs: `celery -A backend.workers.celery_app inspect active`
- Retry failed tasks: `celery -A backend.workers.celery_app control retry <task_id>`

### Database Performance
- Add indexes on frequently queried columns: `client_id`, `date`, `campaign_id`
- Use `EXPLAIN ANALYZE` to diagnose slow queries
- Consider partitioning `google_ads_*` tables by date for large datasets

---

## Support & Contact

**Primary Maintainer:** AI Agent (following SBEP 2.0)  
**User:** James  
**Documentation:** `docs/` directory  
**Issues:** Track in project `workorders/` folder  

---

**Remember:** This is a production system handling live client data. Follow SBEP 2.0 protocols:
- Never delete data (archive only)
- All mutations require audit trail
- Test on small clients first
- Document all changes in CHANGELOG.md

