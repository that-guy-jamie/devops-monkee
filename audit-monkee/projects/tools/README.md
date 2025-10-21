# Audit Monkee — API & Worker (FastAPI + Celery)

## Quick start (dev, SQLite + local Redis)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
make initdb
make dev  # http://localhost:8000
# in another terminal
make worker
```

### Create an audit
```bash
curl -X POST http://localhost:8000/api/audits -H 'Content-Type: application/json' \  -d '{"contactId":"abc123","locationId":"loc_1","url":"https://example.com","types":["seo","design","stack"]}'
```

### Get audit
```bash
curl http://localhost:8000/api/audits/<AUDIT_ID>
```

### Headcore config
Set `HEADCORE_PRIVATE_KEY` in `.env` (base64url Ed25519), then:
```bash
curl -X POST http://localhost:8000/api/audits/<AUDIT_ID>/headcore
```

> PDF output is a simple `.txt` placeholder to keep deps light. Replace with real PDF rendering later.


## Auth (JWT)
Set `JWT_SECRET` in your `.env`. Send `Authorization: Bearer <jwt>` to call the API.
For local tests you can remove `JWT_SECRET` to keep endpoints open.

## PageSpeed Insights
Set `PSI_API_KEY` in `.env` to fetch live Lighthouse data via PSI.

## Node Lighthouse runner (optional)
Install Node runner if you prefer local audits:
```bash
cd projects/tools/audit/lighthouse_node && npm i
```
The worker will use PSI first (if `PSI_API_KEY` is set), then fallback to the Node runner.

## HighLevel (LeadConnector) calls
Set `GHL_ACCESS_TOKEN` (sub-account token) to enable:
- Create Contact Notes
- Upsert Contact Custom Fields

> File uploads: use Media Storage API to upload a file and store the URL in a file-type custom field later.
