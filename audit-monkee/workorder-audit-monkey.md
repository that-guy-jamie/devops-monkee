# workorder-audit-monkey.md — Cursor Prompt (Enterprise Tool in `/projects/tools`)

**ROLE**: Senior Python/Node engineer building an enterprise-grade audit runner for Audit Monkee.

**MISSION**
Build the production audit service in `/projects/tools` with:
- API (`/api/audits`, `/api/audits/{id}`, `/api/audits/{id}/report`)
- Worker (queue, retries, timeouts)
- Integrations: Lighthouse (headless), PSI API, tech stack detection, SEO checks
- GHL write-back: Contact Note, Custom Fields, PDF attachment

**TECH**
- Python 3.11 + FastAPI + Celery + Redis + Postgres (preferred), or Node + Express + BullMQ
- Packaging: Dockerfile; env via `.env`
- Lint/format: ruff/black or eslint/prettier

**ACCEPTANCE CRITERIA**
1. `POST /api/audits` queues a job and returns `{auditId}`
2. Worker produces scores and findings; stores in Postgres
3. On success, writes Note + fields to GHL
4. Generates a PDF and stores `report_url`
5. All endpoints have OpenAPI docs; basic auth via JWT
6. Makefile: `make dev`, `make worker`, `make migrate`

**ENV VARS**
`DATABASE_URL`, `REDIS_URL`, `GHL_CLIENT_ID`, `GHL_CLIENT_SECRET`, `GHL_REDIRECT_URI`, `JWT_SECRET`

**DEFS**
- Audit types: `seo`, `design`, `stack`
- Status: `queued | running | done | failed`

**NEXT**
Add Headcore config generator endpoint: `POST /api/audits/{id}/headcore` -> signed config JSON (Ed25519).
