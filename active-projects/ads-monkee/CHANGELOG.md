# Ads Monkee Changelog

All notable changes to this project will be documented in this file per SBEP v2.0 protocol.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

## [0.3.0] - 2025-10-18 (Week 1 - AI Analysis MVP Skeleton)

### Added
- **AI Analysis Infrastructure (Week 1 Complete)**
  - Celery + Redis integration for async task processing (`backend/celery_app.py`)
  - Analysis Pydantic schemas (`backend/schemas/analysis.py`)
    - `Recommendation`, `Synthesis`, `ParallelCampaignProposal`
    - `AnalysisContext`, `AnalysisRunResult`, `AnalysisRunStatus`
  - Database models for analysis tracking (`backend/models/analysis_run.py`)
    - `AnalysisRun` - tracks each analysis run with caching support
    - `AnalysisReport` - stores canonical JSON + Markdown output
    - `AnalysisRecommendation` - normalized recommendation storage
    - `RecommendationDecision` - approval/rejection tracking
    - `ActionExecution` - audit trail for executed changes
  - Aggregate tables for efficient analysis (`backend/models/aggregates.py`)
    - `ClientTargets` - stores CPA/ROAS/budget goals
    - `AggCampaignDaily`, `AggAdGroupDaily`, `AggKeywordDaily`, `AggSearchTermDaily`
  - Materialized views for token-capped AI prompts (`database/materialized_views.sql`)
    - `focus_keywords_30d` - identifies problematic keywords (max 200 rows)
    - `focus_search_terms_30d` - identifies negative keyword candidates (max 200 rows)
  - Celery task pipeline (stub implementations) (`backend/tasks/analysis.py`)
    - `prepare_data_task` - builds context from focus views
    - `analyze_keywords_and_queries` - keyword/query analysis module
    - `analyze_bidding` - bidding/budget analysis module
    - `synthesize_task` - merges module outputs into recommendations
    - `persist_task` - saves results to database
    - `run_full_analysis` - chains all tasks together
  - FastAPI endpoints with 202 Accepted pattern (`backend/routers/analysis.py`)
    - `POST /api/analysis/clients/{id}/analyze` - trigger analysis (returns 202 + run_id)
    - `GET /api/analysis/{run_id}` - get status/results
    - `GET /api/analysis/clients/{id}/analyses` - list client analyses
  - Helper scripts
    - `scripts/seed_targets.py` - seed client performance targets
    - `scripts/create_materialized_views.py` - create/refresh materialized views
  - Documentation
    - `docs/AI-ANALYSIS-ARCHITECTURE.md` - complete architecture plan
    - `WEEK-1-IMPLEMENTATION.md` - Week 1 checklist and progress

### Changed
- **Database schema** - Migration `4c84fc4d3e07_add_analysis_aggregates_and_focus_tables.py`
  - Added 10 new tables (analysis_runs, analysis_reports, recommendations, etc.)
  - Added 4 aggregate tables (campaigns, ad groups, keywords, search terms)
  - Added client_targets table
- **Client model** - Added `analysis_runs` relationship
- **Dependencies** - Added `instructor` library for strict JSON validation

### Technical Notes
- Week 1 tasks use **stub implementations** with dummy data
- Week 2 will implement actual AI logic with LLM calls
- All infrastructure is in place for production analysis pipeline
- Materialized views enforce hard row limits (200) to control token costs
- Analysis runs support caching via feature_hash + prompt_version

## [0.2.0] - 2025-10-18

### Added
- **CSV Import System** (`scripts/import_csv_data.py`)
  - Import campaigns, ad groups, keywords, and search terms from ads_sync CSVs
  - Support for single client (`--client`) or all clients (`--all`)
  - Optional data clearing (`--clear`) before import
  - Successfully imported 12,053 records for Priority Roofing
- **Google Ads API Test Script** (`scripts/test_google_ads_api.py`)
  - Connection testing and validation
  - Customer listing functionality
  - Query execution testing
- **Parallel Campaign Strategy Documentation** (`docs/PARALLEL-CAMPAIGN-STRATEGY.md`)
  - Comprehensive strategy guide for parallel campaign optimization
  - Decision criteria and success metrics
  - Budget transition schedules (conservative & aggressive)
  - AI recommendation logic with code examples
  - UI mockups for approval dashboard
- **Session Summary** (`SESSION-SUMMARY-2025-10-18.md`)
  - Complete documentation of development session
  - Technical achievements and metrics
  - Issues resolved and lessons learned

### Changed
- **Upgraded `google-ads` library** from v24.1.0 to v28.2.0
  - Now using current Google Ads API v22 (was v17)
  - Fixed `StatusCode.UNIMPLEMENTED` error
  - All API queries now working successfully
- **Updated keyword unique constraint** in `google_ads_keywords` table
  - Changed from `(client_id, keyword_id, date)` to `(client_id, ad_group_id, keyword_id, date)`
  - Allows same keyword in multiple ad groups
  - Migration: `e5cdde793268_fix_keyword_unique_constraint_to_include_ad_group_id.py`
- **Enhanced `CampaignModification` model** with parallel campaign action types
  - Added `CREATE_PARALLEL_CAMPAIGN` action type
  - Added `TRANSITION_BUDGET` action type
  - Added `PAUSE_OLD_CAMPAIGN` action type

### Fixed
- **Google Ads API deprecation issue**
  - API v17 endpoints were returning `UNIMPLEMENTED`
  - Upgraded to library v28.2.0 which uses API v22
- **Database SSL connection**
  - Added `sslmode=require` to connection string
  - Added `connect_args={"sslmode": "require", "connect_timeout": 10}` to sync engine
- **SQLAlchemy 2.0 type compatibility**
  - Changed `Decimal` imports to `Numeric as SQLDecimal`
  - Updated in `google_ads.py`, `analysis.py`, and `campaign_modification.py`
- **Keyword duplicate key violations**
  - Fixed unique constraint to include `ad_group_id`
  - Same keyword can now exist in multiple ad groups

### Infrastructure
- **PostgreSQL database** fully operational on Render
  - Basic 1GB plan ($7/month)
  - SSL connection configured
  - IP allowlisting configured (152.36.150.226/32)
  - 17 tables created successfully
- **Data import pipeline** operational
  - CSV import: 12,053 records in ~2 minutes
  - API connection: <1 second
  - Query execution: <500ms

## [0.1.0] - 2025-10-17

### Added
- Initial SBEP v2.0 compliant project structure
- Project mandate documentation (sds/SBEP-MANDATE.md)
- Documentation index (sds/SBEP-INDEX.yaml)
- README.md with quick start guide
- CHANGELOG.md for tracking all changes
- Directory structure: backend/, frontend/, database/, scripts/, ops/, docs/, tests/
- Poetry configuration (pyproject.toml) with all dependencies
- Environment configuration (backend/config.py) with Pydantic validation
- FastAPI application (backend/main.py) with CORS, error handling, health checks
- Database setup (backend/database.py) with async/sync SQLAlchemy

### Database Models (Complete - 9 models, 17 tables)
- Base model with timestamps (backend/models/base.py)
- Client model with Google Ads & GHL integration (backend/models/client.py)
- User model with role-based access (backend/models/user.py)
- Auth session model with JWT tracking (backend/models/auth.py)
- Audit log model per SBEP requirements (backend/models/audit_log.py)
- Google Ads models: Campaigns, Ad Groups, Keywords, Search Terms (backend/models/google_ads.py)
- Analysis models: Analysis, AI Consensus Session, Report (backend/models/analysis.py)
- Campaign modification model with approval workflow (backend/models/campaign_modification.py)
- LSA models: LSALead, LSASurveyAttempt, LSAMetrics with dual-flag tracking (backend/models/lsa.py)

### Database Migrations (Ready)
- Alembic configuration (alembic.ini)
- Migration environment (database/migrations/env.py) with async support
- Migration template (database/migrations/script.py.mako)

### Scripts
- Database initialization script (scripts/init_db.py)
- Client seeding script from Google Ads API (scripts/seed_clients.py)
- **Standardized Google Ads query module** (backend/services/google_ads_queries.py)
  - Single source of truth for all GAQL queries
  - Matches exact schema from `ads_sync/comprehensive_data_pull.py`
  - Ensures consistency between CSV exports and database imports
  - Field mappings: API → CSV → Database

### Documentation
- Database requirements guide (docs/DATABASE-REQUIREMENTS.md) for parallel provisioning
- 48-hour launch plan (docs/48-HOUR-LAUNCH-PLAN.md) integrating GPT analysis
- Project status tracker (PROJECT-STATUS.md)
- Handoff summary (HANDOFF-SUMMARY.md)
- **Data migration guide (docs/DATA-MIGRATION-GUIDE.md)** - Complete migration process with troubleshooting
- **Infrastructure provisioning doc (INFRASTRUCTURE-PROVISIONED.md)** - Provisioning details and next steps

### Infrastructure (✅ PROVISIONED via Render MCP)
- PostgreSQL 16 Pro 4GB database (100GB disk, Oregon region) - ID: dpg-d3oouas9c44c738cl2sg-a
- Redis 8.1.4 Starter instance for Celery task queue - ID: red-d3oougmmcj7s739fh2og
- Blueprint ready (render.yaml) for web service + worker deployment

### Data Migration Scripts (✅ COMPLETE)
- **migrate_all_clients_data.py** - Operational dataset (1 year, 4 data types: campaigns, ad groups, keywords, search terms)
- **backfill_historical_data.py** - Historical dataset (2-5 years for trend analysis and pattern discovery)
- Two-tier strategy: 1Y operational for optimization + 2-5Y historical for strategic insights

### In Progress
- Backend service migration from ads_sync (scripts ready, awaiting DB connection)

### Notes
- Integrated GPT analysis recommendations
- LSA models designed with "charged-only" rule + dual-flag tracking
- Migration strategy: parallel writes (don't break existing LSA monitor)
- Total: 9 models, 17 tables, ~3,500 lines of production code

---

## [1.0.0] - TBD

Target: Production-ready platform with 30 clients migrated

### Planned Features

#### Core Platform
- Unified dashboard integrating Google Ads, LSA, and LCG
- Multi-agent AI consensus analysis framework
- Campaign modification approval workflow
- Role-based access control (Staff Admin/Analyst/Client)
- GoHighLevel OAuth integration

#### Data & Analysis
- Google Ads data synchronization (daily automated)
- Comprehensive PPC campaign analysis
- Search term waste identification
- Quality Score optimization
- Budget reallocation recommendations
- Cross-client benchmarking

#### Automation
- Celery Beat scheduled tasks
- Automatic report generation
- GHL portal report delivery
- Real-time metrics sync to GHL custom fields

#### API Integrations
- Google Ads API v21 wrapper
- GoHighLevel API v2 wrapper
- Claude API (Anthropic) for multi-agent analysis

#### Frontend
- React 18 + TypeScript dashboard
- Supervisor view (staff)
- Client view (simplified, scoped)
- Granular modification editor
- Bulk approval actions
- Impact preview calculations

#### Infrastructure
- PostgreSQL 16 on Render
- FastAPI backend on Render Web Service
- Celery worker on Render Background Worker
- Redis on Render Key-Value
- React frontend on Render Static Site

#### Testing
- Unit test suite (services, utilities)
- Integration tests (API, Celery, database)
- E2E tests (full workflows)
- Client size validation (small/medium/large)

#### Documentation
- Architecture documentation
- API reference
- Deployment guide
- Staff user guide
- Client user guide

---

## Migration Notes

### From ads_sync
- CSV data → Postgres tables
- CLI tool → Backend services
- `comprehensive_data_pull.py` → `google_ads_sync.py`
- `analyze_comprehensive_data.py` → `ppc_analyzer.py`
- Legacy CSVs archived in `ads_sync/archive/`

### From jamie_lcs-system
- Call tracking logic → `call_tracking.py` service
- Node.js server → Python FastAPI endpoints
- Event ingestion via webhooks

### From LSA (TBD)
- Monitoring logic → `lsa_monitor.py` service
- Dashboard components → React components
- Survey data → Postgres tables

---

## Development Guidelines

Per SBEP v2.0:
- **Never delete data** - Archive to `archive/` instead
- **All mutations logged** - `audit_log` table captures everything
- **Test incrementally** - Small → Medium → Large clients
- **Document immediately** - Update this file with every change
- **Rollback plans required** - Before any destructive operation

---

## Version History

- **v1.0.0 (Planned):** Full production release
- **v0.1.0 (Current):** Initial structure and foundation

---

**Last Updated:** 2025-10-16  
**Maintained By:** AI Agent (SBEP v2.0)

