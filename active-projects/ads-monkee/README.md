# Ads Monkee 🐵

**Unified Digital Advertising Management Platform**

> A supervisor dashboard for managing Google Ads, LSA monitoring, and call tracking across 30+ clients with AI-powered analysis and approval workflows.

---

## Features

### 🎯 Core Capabilities
- **Multi-Product Integration:** Google Ads, LSA, Local Call Generator unified in one dashboard
- **Multi-Agent AI Analysis:** Python + Claude consensus framework for campaign recommendations
- **Approval Workflows:** Granular review and approval of AI-suggested campaign modifications
- **Role-Based Access:** Separate views for Staff (Admin/Analyst) and Clients
- **GoHighLevel Integration:** OAuth authentication, automated reporting, metrics sync

### 📊 Analysis & Insights
- Comprehensive PPC campaign analysis
- Search term waste identification
- Quality Score optimization recommendations
- Budget reallocation suggestions
- Cross-client performance benchmarking

### ⚙️ Automation
- Daily data synchronization from Google Ads API
- Scheduled analysis runs via Celery
- Automatic report generation and delivery to GHL
- Real-time metrics updates to client portals

---

## Technology Stack

**Backend:**
- Python 3.12 + FastAPI
- PostgreSQL 16
- SQLAlchemy 2.0
- Celery + Redis

**Frontend:**
- React 18 + TypeScript
- Tailwind CSS
- Recharts
- Vite

**Infrastructure:**
- Render (Postgres, Web Service, Worker, Redis, Static Site)
- Google Ads API v21
- GoHighLevel API v2
- Claude API (Anthropic)

---

## Quick Start

### Prerequisites
- Python 3.12+
- Node.js 18+
- Poetry
- PostgreSQL (local) or Render account

### 1. Clone & Setup
```bash
cd ads-monkee
poetry install
cd frontend && npm install && cd ..
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env with your credentials (see Configuration section below)
```

### 3. Initialize Database
```bash
poetry run alembic upgrade head
poetry run python scripts/seed_clients.py
```

### 4. Run Development Servers

**Backend:**
```bash
poetry run uvicorn backend.main:app --reload --port 8000
```

**Celery Worker:**
```bash
poetry run celery -A backend.workers.celery_app worker --pool=solo --loglevel=info
```

**Frontend:**
```bash
cd frontend
npm run dev
```

Visit: `http://localhost:5173`

---

## Configuration

Create `.env` file with the following:

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost/ads_monkee

# Redis
REDIS_URL=redis://localhost:6379

# Google Ads API (from ads_sync project)
GOOGLE_ADS_DEVELOPER_TOKEN=your_dev_token
GOOGLE_ADS_CLIENT_ID=your_client_id.apps.googleusercontent.com
GOOGLE_ADS_CLIENT_SECRET=your_client_secret
GOOGLE_ADS_REFRESH_TOKEN=your_refresh_token
GOOGLE_ADS_LOGIN_CUSTOMER_ID=123-456-7890

# GoHighLevel OAuth
GHL_CLIENT_ID=your_ghl_client_id
GHL_CLIENT_SECRET=your_ghl_client_secret
GHL_REDIRECT_URI=http://localhost:8000/auth/ghl/callback

# Claude API
ANTHROPIC_API_KEY=sk-ant-your-key

# App
JWT_SECRET=your-random-secret-key
ENVIRONMENT=development
LOG_LEVEL=DEBUG
```

---

## Project Structure

```
ads-monkee/
├── backend/              # FastAPI application
│   ├── api/             # API routes
│   ├── models/          # SQLAlchemy models
│   ├── services/        # Business logic
│   ├── integrations/    # External API clients
│   └── workers/         # Celery tasks
├── frontend/            # React application
│   └── src/
│       ├── components/  # React components
│       ├── pages/       # Page components
│       └── services/    # API client
├── database/
│   ├── migrations/      # Alembic migrations
│   └── schema.sql       # Initial schema
├── scripts/             # Utility scripts
├── ops/                 # Deployment scripts
├── docs/                # Documentation
├── tests/               # Test suites
└── sds/                 # SBEP compliance docs
```

---

## Key Workflows

### 1. Data Synchronization
Celery Beat runs daily at 2 AM:
- Pulls last 7 days of Google Ads data for all clients
- Deduplicates and stores in Postgres
- Updates `clients.last_sync_at` timestamp

### 2. Run Analysis
Staff triggers analysis from dashboard:
- Multi-agent AI analyzes campaign data (Python + Claude)
- Generates recommendations with confidence scores
- Creates proposed modifications (status: `pending`)
- Notifies staff for review

### 3. Approval & Execution
Staff reviews proposed modifications:
- Edit keywords, bids, budgets in granular editor
- Approve/reject individual or batch modifications
- Approved changes execute via Google Ads API
- Full audit trail logged

### 4. Client Reporting
Automatic report generation:
- PDF report created from analysis
- Uploaded to GHL client portal
- Email/SMS notification sent
- Custom fields updated with latest metrics

---

## API Documentation

FastAPI auto-generated docs available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

Key endpoints:
- `POST /api/auth/ghl/login` - Initiate GHL OAuth
- `GET /api/clients` - List all clients (staff only)
- `POST /api/analysis` - Trigger analysis for client
- `GET /api/modifications` - List pending modifications
- `POST /api/modifications/{id}/approve` - Approve modification
- `POST /api/modifications/execute` - Execute all approved

Full API reference: [`docs/api-reference.md`](docs/api-reference.md)

---

## Testing

```bash
# Unit tests
poetry run pytest tests/unit -v

# Integration tests
poetry run pytest tests/integration -v

# E2E tests
poetry run pytest tests/e2e -v

# All tests with coverage
poetry run pytest --cov=backend --cov-report=html
```

Test on real client data (small → medium → large):
```bash
poetry run python tests/validate_clients.py
```

---

## Deployment

### Render (Production)

1. **Provision Infrastructure:**
   ```bash
   poetry run python ops/provision_render.py
   ```

2. **Configure Environment Variables** in Render dashboard

3. **Deploy:**
   - Backend & Worker: Auto-deploy from GitLab
   - Frontend: Build and deploy to Static Site
   - Migrations: Run via `Release Command` hook

Detailed guide: [`docs/deployment-guide.md`](docs/deployment-guide.md)

---

## Documentation

- **Architecture:** [`docs/architecture.md`](docs/architecture.md)
- **API Reference:** [`docs/api-reference.md`](docs/api-reference.md)
- **Deployment:** [`docs/deployment-guide.md`](docs/deployment-guide.md)
- **User Guide (Staff):** [`docs/user-guide-staff.md`](docs/user-guide-staff.md)
- **User Guide (Client):** [`docs/user-guide-client.md`](docs/user-guide-client.md)
- **SBEP Mandate:** [`sds/SBEP-MANDATE.md`](sds/SBEP-MANDATE.md)

---

## Contributing

This project follows **SBEP v2.0** (Source-Bound Execution Protocol):

1. Read [`sds/SBEP-MANDATE.md`](sds/SBEP-MANDATE.md) before making changes
2. All changes must be documented in [`CHANGELOG.md`](CHANGELOG.md)
3. Never delete data - archive to `archive/` instead
4. All mutations require audit trail
5. Test on small clients first

---

## Support

**Maintainer:** AI Agent (SBEP v2.0 compliant)  
**User:** James  
**Issues:** Track in `workorders/` folder  
**Documentation:** `docs/` directory

---

## License

Proprietary - One Click Agency

---

## Acknowledgments

Built on:
- [`ads_sync`](../ads_sync/) - Google Ads data synchronization
- [`jamie_lcs-system`](../jamie_lcs-system/) - Call tracking
- LSA Survey Monitor - Local Services Ads monitoring

Integrated with:
- Google Ads API v21
- GoHighLevel API v2
- Anthropic Claude API

