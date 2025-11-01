# 🚀 Quick Start Guide - ads_sync Dashboard Backend

**5-Minute Setup** | **Zero Configuration Required**

---

## Step 1: Install Dependencies (2 minutes)

```powershell
cd C:\Users\james\Desktop\Projects\ads_sync_dashboard
poetry install
```

Expected output: `Installing dependencies from lock file... Successfully installed...`

---

## Step 2: Start Redis (30 seconds)

```powershell
docker-compose up -d
```

Expected output: `Creating network... Creating volume... Creating ads_sync_dashboard_redis_1... done`

**Verify Redis is running:**
```powershell
docker ps
```

You should see a container named `ads_sync_dashboard_redis_1` running.

---

## Step 3: Configure Environment (30 seconds)

```powershell
copy env.example .env
```

**No edits needed!** The defaults work out of the box:
- Redis: `localhost:6379` ✅
- ads_sync: `../ads_sync` ✅  
- API: Port `8000` ✅

---

## Step 4: Start Celery Worker (1 minute)

**Open Terminal 1:**
```powershell
cd C:\Users\james\Desktop\Projects\ads_sync_dashboard
poetry run celery -A worker.tasks worker --pool=solo --loglevel=info
```

Expected output:
```
-------------- celery@DEEPTHOUGHT v5.5.3
...
[tasks]
  . execute_append
  . execute_cli_command
  . execute_report_generation
  . execute_validation
  
celery@DEEPTHOUGHT ready.
```

**⚠️ Important:** Use `--pool=solo` for Windows compatibility!

---

## Step 5: Start API Server (1 minute)

**Open Terminal 2:**
```powershell
poetry run uvicorn api.main:app --reload --port 8000
```

Expected output:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Test it:**
Open http://localhost:8000/health in your browser

You should see: `{"status":"healthy",...}`

---

## Step 5: Start Worker (1 minute) - NEW TERMINAL

Open a **second terminal** window:

```powershell
cd C:\Users\james\Desktop\Projects\ads_sync_dashboard
poetry run celery -A worker.tasks worker --pool=solo --loglevel=info
```

Expected output:
```
Worker rq:worker:... started
Listening on default queue...
```

**Keep this terminal open!** The worker needs to run continuously.

---

## ✅ You're Ready!

### Test the Complete Flow

**Terminal 3 (or use Postman/curl):**

```powershell
# Test 1: Health check
curl http://localhost:8000/health

# Test 2: Execute a validation command
curl -X POST http://localhost:8000/api/runbooks/execute -H "Content-Type: application/json" -d '{"slug":"priority-roofing","command":"validate"}'
```

You'll get a response like:
```json
{"job_id":"abc123-def456","status":"queued"}
```

**Save that job_id!** Then check its status:

```powershell
# Test 3: Check job status (replace {job_id})
curl http://localhost:8000/api/jobs/abc123-def456/status
```

After a few seconds, the status will change to `"finished"` and you'll see the result.

---

## 📊 Interactive API Documentation

The best way to explore the API:

**Open in your browser:** http://localhost:8000/docs

This gives you:
- ✅ Interactive API testing (try it now!)
- ✅ Request/response examples
- ✅ Schema documentation
- ✅ No curl commands needed

---

## 🎯 What Each Component Does

| Component | What It Does | Where It Runs |
|-----------|--------------|---------------|
| **FastAPI Server** | Handles HTTP requests, returns job IDs | Port 8000 |
| **Redis** | Message queue, stores job state | Docker, Port 6379 |
| **RQ Worker** | Executes ads_sync CLI commands | Background process |

**The Flow:**
1. Frontend/curl → POST request to API
2. API → Creates job in Redis queue → Returns job_id immediately
3. Worker → Picks up job from Redis → Runs ads_sync CLI → Saves result
4. Frontend/curl → GET /jobs/{id}/status → Retrieves result

---

## 🔧 Common Commands

### Stop Everything
```powershell
# Stop API server: Press CTRL+C in Terminal 1
# Stop worker: Press CTRL+C in Terminal 2
# Stop Redis:
docker-compose down
```

### Restart Everything
```powershell
# Terminal 1: API
poetry run uvicorn api.main:app --reload --port 8000

# Terminal 2: Worker
poetry run celery -A worker.tasks worker --pool=solo --loglevel=info
```

### View Redis Logs
```powershell
docker-compose logs redis
```

### Check What's Running
```powershell
# Check API server
curl http://localhost:8000/health

# Check Redis
docker ps | findstr redis

# Check Worker
# (Look for "Listening on default queue" in Terminal 2)
```

---

## 🐛 Troubleshooting

### "Port 8000 already in use"

Someone else is using port 8000. Change it:

```powershell
# Edit .env
notepad .env

# Change API_PORT=8000 to API_PORT=8001
# Then restart API server on new port
poetry run uvicorn api.main:app --reload --port 8001
```

### "Cannot connect to Redis"

Redis isn't running:

```powershell
# Start it
docker-compose up -d

# Verify it's running
docker ps
```

### "Job stuck in 'queued' status"

Worker isn't running:

```powershell
# Start the worker
poetry run celery -A worker.tasks worker --pool=solo --loglevel=info
```

### "ModuleNotFoundError"

Dependencies not installed:

```powershell
poetry install
```

---

## 📖 Where to Go Next

1. **Test more commands:** Check out README.md for all API endpoints
2. **Explore Swagger UI:** http://localhost:8000/docs
3. **Build a frontend:** Connect React/Vue.js app to this API
4. **Add scheduling:** Set up daily syncs

---

## ✅ Success Criteria

You're ready when:
- [ ] http://localhost:8000/health returns `{"status":"healthy"}`
- [ ] http://localhost:8000/docs shows Swagger UI
- [ ] POST /api/runbooks/execute returns a job_id
- [ ] GET /api/jobs/{job_id}/status shows job completion
- [ ] Worker terminal shows "Listening on default queue"

---

**That's it! You now have a production-grade API backend running.** 🎉

**Questions?** Check the full README.md or IMPLEMENTATION-COMPLETE.md for details.

