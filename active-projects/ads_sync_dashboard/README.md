# ads_sync Dashboard Backend

**Version:** 0.1.0  
**Status:** Production-Ready Backend API (Celery Migration Complete)  
**Created:** October 13, 2025  
**Updated:** October 14, 2025

---

## Overview

FastAPI backend for the ads_sync command center, providing a human-in-the-loop interface for managing Google Ads data sync operations across 30 active Google Ads clients.

### Architecture

This backend implements a decoupled architecture with three key components:

1. **FastAPI Web Server** - Handles API requests, never blocks on long-running operations
2. **Redis Message Queue** - Decouples API from worker, stores job state
3. **Celery Background Worker** - Executes ads_sync CLI commands asynchronously (Windows-compatible)

```
┌─────────────┐      ┌───────────┐      ┌──────────────┐
│   Frontend  │─────▶│  FastAPI  │─────▶│    Redis     │
│   (Future)  │      │    API    │      │  Job Queue   │
└─────────────┘      └───────────┘      └──────────────┘
                                               │
                                               ▼
                                        ┌──────────────┐
                                        │   Celery     │
                                        │   Worker     │
                                        │  (executes   │
                                        │   ads_sync   │
                                        │   CLI)       │
                                        └──────────────┘
```

---

## Prerequisites

- **Python 3.12** (same as ads_sync)
- **Docker** (for Redis)
- **Poetry** (already installed)
- **ads_sync** project (sibling directory)

---

## Quick Start

### 1. Install Dependencies

```powershell
cd C:\Users\james\Desktop\Projects\ads_sync_dashboard
poetry install
```

### 2. Start Redis

```powershell
docker-compose up -d
```

This starts Redis in the background on port 6379.

### 3. Configure Environment

```powershell
# Copy example config
copy env.example .env

# Edit .env if needed (defaults should work)
notepad .env
```

**Default configuration:**
- Redis: `localhost:6379`
- ads_sync path: `../ads_sync`
- API port: `8000`

### 4. Start API Server

```powershell
poetry run uvicorn api.main:app --reload --port 8000
```

The API will be available at:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **Health Check:** http://localhost:8000/health

### 5. Start Celery Worker (Separate Terminal)

```powershell
cd C:\Users\james\Desktop\Projects\ads_sync_dashboard
poetry run celery -A worker.tasks worker --pool=solo --loglevel=info
```

**Important:** Keep this terminal open. The worker must be running to process jobs.

**Note:** The `--pool=solo` flag is required for Windows compatibility.

---

## API Endpoints

### Runbook Execution

**POST /api/runbooks/execute**

Execute an ads_sync CLI command as a background job.

```bash
curl -X POST http://localhost:8000/api/runbooks/execute \
  -H "Content-Type: application/json" \
  -d '{
    "slug": "priority-roofing",
    "command": "validate"
  }'
```

**Response:**
```json
{
  "job_id": "abc123-def456-ghi789",
  "status": "queued"
}
```

**Supported commands:**
- `init` - Historical backfill
- `append` - Incremental sync
- `validate` - Configuration check
- `repair` - Fix data gaps (requires `args: {"start": "YYYY-MM-DD", "end": "YYYY-MM-DD"}`)
- `force-unlock` - Manual lock removal

**GET /api/runbooks/commands**

List all available commands and their descriptions.

---

### Report Generation

**POST /api/reports/generate**

Generate a Markdown report as a background job.

```bash
curl -X POST http://localhost:8000/api/reports/generate \
  -H "Content-Type: application/json" \
  -d '{
    "slug": "priority-roofing",
    "scope": "LAST-30-DAYS"
  }'
```

**Response:**
```json
{
  "job_id": "xyz789-uvw456-rst123",
  "status": "queued"
}
```

**Supported scopes:**
- `LIFETIME` - All data
- `LAST-7-DAYS` - Last 7 days
- `LAST-30-DAYS` - Last 30 days
- `2025-Q3` - Specific quarter
- `2025-01..2025-03` - Custom date range

**GET /api/reports/scopes**

List all available report scopes.

---

### Job Status

**GET /api/jobs/{job_id}/status**

Check the status of a background job.

```bash
curl http://localhost:8000/api/jobs/abc123-def456-ghi789/status
```

**Response (queued):**
```json
{
  "job_id": "abc123-def456-ghi789",
  "status": "queued",
  "result": null,
  "error": null
}
```

**Response (finished):**
```json
{
  "job_id": "abc123-def456-ghi789",
  "status": "finished",
  "result": "Validation complete for 'priority-roofing'",
  "error": null
}
```

**Response (failed):**
```json
{
  "job_id": "abc123-def456-ghi789",
  "status": "failed",
  "result": null,
  "error": "CLI command failed: Config file not found"
}
```

**Status values:**
- `queued` - Waiting to execute
- `started` - Currently running
- `finished` - Completed successfully
- `failed` - Failed with error

**GET /api/jobs/{job_id}/result**

Get the full result of a completed job (includes stdout, stderr, exit code).

---

### Data Status

**GET /api/data/status/{slug}**

Get data freshness status for a client.

```bash
curl http://localhost:8000/api/data/status/priority-roofing
```

**Response:**
```json
{
  "slug": "priority-roofing",
  "last_append_timestamp": "2025-10-13T08:00:00+00:00",
  "last_sync": "2025-10-13T08:00:00+00:00",
  "watermark_date": "2025-10-12"
}
```

**GET /api/data/clients**

List all clients with state files.

```bash
curl http://localhost:8000/api/data/clients
```

---

## Testing the API

### 1. Health Check

```bash
curl http://localhost:8000/health
```

Expected: `{"status": "healthy", ...}`

### 2. Validate a Client

```bash
curl -X POST http://localhost:8000/api/runbooks/execute \
  -H "Content-Type: application/json" \
  -d '{"slug":"priority-roofing","command":"validate"}'
```

Save the `job_id` from response.

### 3. Check Job Status

```bash
curl http://localhost:8000/api/jobs/{job_id}/status
```

Replace `{job_id}` with actual ID. Poll until status is `finished` or `failed`.

### 4. Get Data Status

```bash
curl http://localhost:8000/api/data/status/priority-roofing
```

---

## Project Structure

```
ads_sync_dashboard/
├── api/                          # FastAPI web server
│   ├── __init__.py
│   ├── main.py                   # FastAPI app entry point
│   ├── config.py                 # Settings from .env
│   ├── models/                   # Pydantic models
│   │   ├── __init__.py
│   │   ├── requests.py           # Request validation models
│   │   └── responses.py          # Response models
│   └── routes/                   # API endpoints
│       ├── __init__.py
│       ├── runbooks.py           # POST /api/runbooks/execute
│       ├── reports.py            # POST /api/reports/generate
│       ├── jobs.py               # GET /api/jobs/{id}/status
│       └── data.py               # GET /api/data/status/{slug}
├── worker/                       # RQ background worker
│   ├── __init__.py
│   ├── tasks.py                  # Job execution functions
│   └── cli_executor.py           # Subprocess wrapper
├── docker-compose.yml            # Redis container
├── env.example                   # Configuration template
├── pyproject.toml                # Poetry dependencies
└── README.md                     # This file
```

---

## Configuration

Edit `.env` file to customize:

```env
# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# ads_sync CLI Configuration
ADS_SYNC_PROJECT_PATH=../ads_sync
ADS_SYNC_CLI_COMMAND=poetry run python ads_sync_cli.py

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
```

---

## Development

### Running Tests

```powershell
poetry run pytest
```

### Code Formatting

```powershell
poetry run black .
poetry run ruff check .
```

### Viewing Logs

**API Server:** Logs to console (stdout)

**RQ Worker:** Logs to console

**Redis:** Check with `docker-compose logs redis`

---

## Troubleshooting

### Redis Connection Failed

**Problem:** API can't connect to Redis

**Solution:**
```powershell
# Check if Redis is running
docker ps

# Start Redis if not running
docker-compose up -d

# Check Redis logs
docker-compose logs redis
```

### Job Stuck in "queued" Status

**Problem:** Jobs never start

**Solution:** Make sure Celery worker is running:
```powershell
poetry run celery -A worker.tasks worker --pool=solo --loglevel=info
```

### CLI Command Fails

**Problem:** Jobs fail with "CLI command failed"

**Solution:** Check that:
1. `ads_sync` project exists at `../ads_sync`
2. Poetry is on PATH or full path is configured
3. ads_sync dependencies are installed

Test manually:
```powershell
cd ..\ads_sync
poetry run python ads_sync_cli.py validate priority-roofing
```

### Port Already in Use

**Problem:** `Address already in use` error

**Solution:** Change port in `.env` or kill existing process:
```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Kill process (replace PID)
taskkill /PID {PID} /F
```

---

## Production Deployment

### Security Hardening

1. **Configure CORS:** Edit `api/config.py` to restrict `cors_origins` to your frontend domain
2. **Use HTTPS:** Deploy behind a reverse proxy (nginx, Caddy)
3. **Protect .env:** Never commit `.env` file
4. **Redis Authentication:** Add password in production

### Scaling

- **Multiple Workers:** Run multiple Celery worker processes
- **Load Balancing:** Run multiple API instances behind a load balancer
- **Redis Cluster:** Use Redis Sentinel or Cluster for high availability
- **Worker Pools:** On Linux/Mac, use `--pool=prefork` for better concurrency

---

## Next Steps

1. **Frontend Development:** Build React/Vue.js dashboard that consumes this API
2. **Monitoring:** Add Prometheus metrics and Grafana dashboards
3. **Alerting:** Integrate with notification services (email, Slack)
4. **Scheduling:** Add cron-like scheduled jobs for daily syncs

---

## Support

**Project:** ads_sync_dashboard  
**Organization:** OneClickSEO PPC Management  
**Version:** 0.1.0  
**Contact:** ppcmanager@deanknows.com

---

## License

Proprietary - OneClickSEO PPC Management  
All rights reserved.

---

**Built with ❤️ for production-grade Google Ads data management**

