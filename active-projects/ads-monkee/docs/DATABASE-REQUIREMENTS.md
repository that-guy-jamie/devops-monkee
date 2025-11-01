# Ads Monkee - Database Requirements & Setup Guide

**Purpose:** This document provides complete requirements for setting up the PostgreSQL database for Ads Monkee on Render.

**Audience:** User (James) working with an AI agent to provision and configure the database.

---

## Overview

Ads Monkee requires a **PostgreSQL 16** database on Render with the following characteristics:

- **Architecture:** Hybrid schema (shared core tables + product-specific namespaces)
- **Size Estimate:** ~30 clients × 10K rows/client/year = ~300K rows/year
- **Performance Tier:** Pro 4GB (room for growth, good performance)
- **Backups:** Daily automatic backups (included in Render Pro tier)
- **Connections:** ~20 concurrent (10 from API, 5 from workers, 5 buffer)

---

## Step 1: Provision Postgres on Render

### Using Render MCP (Recommended)

You have access to Render MCP tools. Ask your agent to run:

```python
mcp_render_create_postgres(
    name="ads-monkee-db",
    plan="pro_4gb",
    region="oregon",  # or your preferred region
    version=16
)
```

**Expected Output:**
- Database ID (e.g., `dpg-xxxxxxxxxxxxx`)
- Internal connection string (for backend/worker)
- External connection string (for local development)
- Hostname, port, database name, username, password

### Manual Setup (If MCP Not Available)

1. Go to https://dashboard.render.com/new/database
2. **Name:** `ads-monkee-db`
3. **Database:** `ads_monkee` (auto-generated, use default)
4. **User:** `ads_monkee_user` (auto-generated, use default)
5. **Region:** Oregon (or closest to your users)
6. **PostgreSQL Version:** 16
7. **Plan:** Pro ($65/month for 4GB RAM, 50GB storage)
8. Click **Create Database**

**Wait 2-3 minutes for provisioning to complete.**

---

## Step 2: Retrieve Connection Strings

After provisioning, you need **two connection strings**:

### Internal Database URL (for Production - Backend & Worker)
- Found in Render Dashboard → Database → "Internal Database URL"
- Format: `postgresql://user:password@internal-host:5432/dbname`
- **Copy this** - you'll add it as `DATABASE_URL` environment variable to your Web Service and Worker

### External Database URL (for Local Development & Migrations)
- Found in Render Dashboard → Database → "External Database URL"
- Format: `postgresql://user:password@external-host:5432/dbname`
- **Copy this** - you'll use it locally in your `.env` file

---

## Step 3: Create Local .env File

Create `.env` in `ads-monkee/` directory:

```bash
# Database (use EXTERNAL URL for local development)
DATABASE_URL=postgresql://ads_monkee_user:your_password@dpg-xxxxx-a.oregon-postgres.render.com:5432/ads_monkee

# Copy from ads_sync or google-ads-manager
GOOGLE_ADS_DEVELOPER_TOKEN=...
GOOGLE_ADS_CLIENT_ID=...
GOOGLE_ADS_CLIENT_SECRET=...
GOOGLE_ADS_REFRESH_TOKEN=...
GOOGLE_ADS_LOGIN_CUSTOMER_ID=...

# JWT Secret (generate random 32+ chars)
JWT_SECRET=your-random-secret-minimum-32-characters-here

# Redis (we'll set this up next)
REDIS_URL=redis://localhost:6379

# Environment
ENVIRONMENT=development
LOG_LEVEL=DEBUG
```

**Questions to Ask Your Agent:**
1. "How do I generate a secure JWT_SECRET?"
2. "Can I test the database connection before proceeding?"
3. "What's the difference between internal and external URLs?"

---

## Step 4: Initialize Database Schema

Once you have the connection string in `.env`, the development agent will run Alembic migrations:

```bash
cd ads-monkee
poetry run alembic upgrade head
```

This will create all tables defined in the schema.

---

## Database Schema Overview

### Shared Core Tables

These tables are used across all products:

#### `clients`
- **Purpose:** All client accounts (30+ clients)
- **Key Fields:** 
  - `id` (primary key)
  - `name` (e.g., "Priority Roofing")
  - `slug` (e.g., "priority-roofing")
  - `google_ads_customer_id` (e.g., "123-456-7890")
  - `ghl_location_id` (for GoHighLevel integration)
  - `ghl_contact_id` (for client portal access)
  - `status` (active, paused, archived)
  - `last_sync_at` (timestamp of last data sync)

#### `users`
- **Purpose:** Staff and client users
- **Key Fields:**
  - `id` (primary key)
  - `email`
  - `role` (admin, analyst, client)
  - `ghl_user_id` (from OAuth)
  - `client_id` (NULL for staff, set for clients)

#### `auth_sessions`
- **Purpose:** JWT session tracking
- **Key Fields:**
  - `token` (JWT token hash)
  - `user_id` (foreign key to users)
  - `expires_at`

#### `audit_log`
- **Purpose:** Track all mutations (SBEP requirement)
- **Key Fields:**
  - `user_id`
  - `action` (e.g., "approve_modification", "execute_campaign_change")
  - `resource_type` (e.g., "campaign_modification")
  - `resource_id`
  - `changes_json` (before/after state)
  - `timestamp`

---

### Google Ads Product Tables

#### `google_ads_campaigns`
- **Purpose:** Campaign performance data (synced daily)
- **Key Fields:**
  - `client_id` (foreign key to clients)
  - `campaign_id` (Google Ads campaign ID)
  - `date` (performance date)
  - `impressions`, `clicks`, `cost`, `conversions`, `conversions_value`
  - Derived: `ctr`, `cpc`, `cpa`, `roas`
- **Index:** `(client_id, campaign_id, date)` - UNIQUE
- **Estimated Size:** 30 clients × 5 campaigns × 365 days = ~55K rows/year

#### `google_ads_ad_groups`
- Similar structure to campaigns but at ad group level
- **Estimated Size:** ~150K rows/year

#### `google_ads_keywords`
- Keyword-level performance data
- Includes `quality_score`, `creative_quality`, `landing_page_quality`
- **Estimated Size:** ~300K rows/year

#### `google_ads_search_terms`
- Actual search queries that triggered ads
- **Purpose:** Identify negative keyword opportunities
- **Estimated Size:** ~1M rows/year (largest table)
- **Note:** May need partitioning by date after 1-2 years

---

### Analysis & Workflow Tables

#### `analyses`
- **Purpose:** Store AI-generated analysis results
- **Key Fields:**
  - `client_id`
  - `date_range_start`, `date_range_end`
  - `analysis_data_json` (executive summary, recommendations)
  - `consensus_similarity_score` (multi-agent agreement level)
  - `created_at`

#### `ai_consensus_sessions`
- **Purpose:** Track multi-agent debate process
- **Key Fields:**
  - `analysis_id`
  - `agent_1_output_json`, `agent_2_output_json`, `agent_3_output_json`
  - `similarity_score`
  - `required_debate` (boolean)

#### `campaign_modifications`
- **Purpose:** Proposed changes from AI analysis
- **Key Fields:**
  - `client_id`
  - `analysis_id`
  - `action_type` (add_negative_keyword, add_keyword, adjust_budget)
  - `target_id` (campaign/ad_group ID)
  - `change_data_json` (details of proposed change)
  - `status` (pending, approved, rejected, applied, failed)
  - `ai_confidence_score`
  - `reviewed_by` (user_id)
  - `reviewed_at`
  - `applied_at`
  - `api_response_json`

#### `reports`
- **Purpose:** Generated PDF/Markdown reports
- **Key Fields:**
  - `client_id`
  - `analysis_id`
  - `report_type` (comprehensive, monthly, executive)
  - `file_url` (if uploaded to GHL)
  - `generated_at`

---

### LSA & Call Tracking Tables (Phase 2+)

#### `lsa_leads` (for future LSA integration)
- Local Services Ads lead tracking

#### `call_tracking_events` (for future LCG integration)
- Call tracking and analytics

---

## Performance Considerations

### Indexes Required

The Alembic migrations will create these automatically, but FYI:

```sql
-- Most common queries: filter by client + date range
CREATE INDEX idx_campaigns_client_date ON google_ads_campaigns(client_id, date DESC);
CREATE INDEX idx_keywords_client_date ON google_ads_keywords(client_id, date DESC);
CREATE INDEX idx_search_terms_client_date ON google_ads_search_terms(client_id, date DESC);

-- Lookup by Google Ads IDs
CREATE INDEX idx_campaigns_campaign_id ON google_ads_campaigns(campaign_id);
CREATE INDEX idx_modifications_status ON campaign_modifications(status, client_id);

-- Audit log queries
CREATE INDEX idx_audit_log_timestamp ON audit_log(timestamp DESC);
CREATE INDEX idx_audit_log_user_id ON audit_log(user_id);
```

### Connection Pooling

- **SQLAlchemy pool size:** 10 connections
- **Max overflow:** 20 connections
- **Total max:** 30 concurrent connections
- **Render Pro 4GB supports:** 97 connections (plenty of headroom)

### Future Optimization (Year 2+)

If `google_ads_search_terms` exceeds 10M rows:

1. **Partitioning by date** (monthly or quarterly)
2. **Archival strategy** (move data older than 2 years to cold storage)
3. **Upgrade to Pro 8GB** ($120/month)

---

## Step 5: Test Database Connection

Once database is provisioned and `.env` is configured:

**Ask your agent to run:**

```python
# Test connection script
import asyncio
from backend.database import async_engine

async def test_connection():
    async with async_engine.connect() as conn:
        result = await conn.execute("SELECT version()")
        print(f"✅ Connected! PostgreSQL version: {result.scalar()}")

asyncio.run(test_connection())
```

**Expected Output:**
```
✅ Connected! PostgreSQL version: PostgreSQL 16.x on x86_64-pc-linux-gnu...
```

---

## Step 6: Run Initial Migration

The development agent will create and run Alembic migrations:

```bash
# Initialize Alembic (one-time)
poetry run alembic init database/migrations

# Generate first migration (auto-detects models)
poetry run alembic revision --autogenerate -m "Initial schema"

# Apply migration
poetry run alembic upgrade head
```

**Expected Output:**
```
INFO  [alembic.runtime.migration] Running upgrade -> abc123, Initial schema
✅ Created tables: clients, users, auth_sessions, audit_log, google_ads_campaigns, ...
```

---

## Step 7: Seed Initial Data

The development agent will create a seed script to populate initial clients:

```bash
poetry run python scripts/seed_clients.py
```

This will:
1. Connect to Google Ads API
2. Discover all client accounts
3. Create `clients` table records
4. Create initial `users` records (staff)

---

## Questions You Might Have

### Q1: "What if I need to change the database plan later?"

**Answer from your agent:** Render allows plan changes without downtime. Go to Dashboard → Database → Settings → Change Plan. Your connection strings remain the same.

### Q2: "How do I see what tables were created?"

**Answer:** Use a database client (like pgAdmin, DBeaver, or even `psql`):

```bash
psql "postgresql://user:pass@host:5432/dbname"
\dt  # List all tables
\d clients  # Describe clients table
```

Or ask your agent to run:
```python
from backend.database import async_engine
# ... query information_schema.tables
```

### Q3: "What happens if migration fails?"

**Answer:** Alembic is transactional - if migration fails, it rolls back. You can re-run `alembic upgrade head` after fixing the issue. The development agent will handle this.

### Q4: "Can I reset the database if something goes wrong?"

**Answer (Development only!):** 

```python
# DANGER: This drops all tables
poetry run python -c "from backend.database import drop_db; import asyncio; asyncio.run(drop_db())"

# Then re-run migrations
poetry run alembic upgrade head
```

### Q5: "How much will this cost?"

**Render Pricing:**
- **Pro 4GB Postgres:** $65/month
- **Includes:** Daily backups, 50GB storage, high availability
- **Alternative:** Start with Basic 1GB ($7/month) for testing, upgrade later

---

## Handoff Checklist

Before proceeding to Phase 2, confirm:

- [ ] PostgreSQL 16 database provisioned on Render
- [ ] Internal connection URL saved (for production env vars)
- [ ] External connection URL saved (for local `.env`)
- [ ] `.env` file created with `DATABASE_URL`
- [ ] Connection test passed (can connect from local machine)
- [ ] Ready for Alembic migrations

**Once these are complete, the development agent can proceed with:**
- Creating SQLAlchemy models
- Generating Alembic migrations
- Running migrations to create tables
- Seeding initial client data
- Building API routes

---

## Support Resources

**Render Documentation:**
- PostgreSQL: https://render.com/docs/databases
- Connection Strings: https://render.com/docs/databases#connecting-to-postgres

**If You Get Stuck:**

Common issues:
1. **"Connection refused"** → Check if using External URL for local, Internal for production
2. **"SSL required"** → Render requires SSL, this is configured automatically in SQLAlchemy
3. **"Too many connections"** → Check pool_size settings in `backend/database.py`

Ask your agent:
- "Show me how to troubleshoot connection issues"
- "What's the difference between sync and async database URLs?"
- "How do I check database disk usage?"

---

## Summary

**What You Need to Provide to Development Agent:**

1. Confirmation that database is provisioned
2. The `DATABASE_URL` connection string (external URL for local dev)

**What Development Agent Will Do:**

1. Create SQLAlchemy models for all tables listed above
2. Set up Alembic migrations
3. Run migrations to create schema
4. Seed initial client data from Google Ads API
5. Continue building API routes and services

**Estimated Time:**
- Database provisioning: 3-5 minutes
- Testing connection: 2 minutes
- Total: ~10 minutes of your time

---

**Ready to Start?** Hand this document to an agent and say:

> "I need to provision a PostgreSQL database on Render for the Ads Monkee project. Walk me through the steps in DATABASE-REQUIREMENTS.md and answer any questions I have. Use the Render MCP tools if available."

Meanwhile, the development agent can continue building the backend services and will be ready to connect once the database is live!

