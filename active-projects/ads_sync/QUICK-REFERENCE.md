# Quick Reference Guide - ads_sync

**Project:** ads_sync v0.1.0  
**Organization:** OneClickSEO PPC Management  
**Last Updated:** October 14, 2025

---

## 📍 Quick Links

- **Data Location:** `C:\Users\james\Desktop\Projects\ads_sync\data`
- **Config Files:** `C:\Users\james\Desktop\Projects\ads_sync\configs\clients`
- **Dashboard API:** http://localhost:8000/docs (when running)
- **API Health Check:** http://localhost:8000/health

---

## 🚀 Common Commands

### Check a Client's Data

```powershell
cd C:\Users\james\Desktop\Projects\ads_sync
poetry run python ads_sync_cli.py validate priority-roofing
```

### View Client Data Summary

```powershell
cd C:\Users\james\Desktop\Projects\ads_sync
poetry run python scripts/analyze_data.py heather-murphy-group
```

### Pull Fresh Data (when implemented)

```powershell
cd C:\Users\james\Desktop\Projects\ads_sync
poetry run python ads_sync_cli.py append priority-roofing
```

### Generate Report (when implemented)

```powershell
cd C:\Users\james\Desktop\Projects\ads_sync
poetry run python ads_sync_cli.py report priority-roofing --scope LAST-30-DAYS
```

### View All Clients Data

```powershell
cd C:\Users\james\Desktop\Projects\ads_sync
poetry run python scripts/show_all_data.py
```

### Discover New Clients

```powershell
cd C:\Users\james\Desktop\Projects\ads_sync
poetry run python scripts/discover_clients.py
```

---

## 🎛️ Dashboard Commands

### Start Redis (Docker)

```powershell
cd C:\Users\james\Desktop\Projects\ads_sync_dashboard
docker-compose up -d
```

### Stop Redis

```powershell
cd C:\Users\james\Desktop\Projects\ads_sync_dashboard
docker-compose down
```

### Start API Server

```powershell
cd C:\Users\james\Desktop\Projects\ads_sync_dashboard
poetry run uvicorn api.main:app --port 8000
```

### Start Celery Worker (separate terminal)

```powershell
cd C:\Users\james\Desktop\Projects\ads_sync_dashboard
poetry run celery -A worker.tasks worker --pool=solo --loglevel=info
```

### Check API Health

```powershell
curl http://localhost:8000/health
```

### Run Validation on All Clients (via API)

```powershell
cd C:\Users\james\Desktop\Projects\ads_sync_dashboard
poetry run python run_all_clients.py
```

---

## 📊 Client Reference

### Top 10 Clients by Data Volume

1. Heather Murphy Group - 24,819 rows
2. 1% Lists Buy/Sell Realty - 11,386 rows
3. 1% Lists Greater Charlotte - 9,125 rows
4. 1% Lists Tacoma Chad Nolan - 8,395 rows
5. 1% Lists Tacoma LSA Related - 8,395 rows
6. Grant 1% Lists - 7,665 rows
7. 1% Lists Scenic City - 6,570 rows
8. Priority Roofing - 5,840 rows
9. 1% Lists Hub LSA Related - 5,110 rows
10. WJ Blanchard Law - 4,015 rows

### Clients to Investigate (No Data)

- customer-248-649-3690
- customer-854-315-6147
- customer-629-150-4682
- customer-776-663-1064
- customer-512-678-0705

---

## 📁 File Locations

### Client Data CSV
```
data/{client-slug}/{client-slug}-master-campaign_data.csv
```

### Client Config
```
configs/clients/{client-slug}.yaml
```

### Client State (Watermark)
```
state/{client-slug}.json
```

### Generated Reports (when implemented)
```
output/{client-slug}/{year}/{NNN}-{slug}-report-{scope}-{timestamp}.md
```

### Error Logs
```
errors/{client-slug}/error_{timestamp}.json
```

---

## 🔍 Troubleshooting

### "Lock file exists" Error

```powershell
poetry run python ads_sync_cli.py force-unlock {client-slug}
```

### Check for API Connection Issues

```powershell
# Test API credentials
poetry run python -c "from google.ads.googleads.client import GoogleAdsClient; client = GoogleAdsClient.load_from_storage('google-ads.yaml'); print('✓ Connected')"
```

### View Recent Errors for a Client

```powershell
dir errors\{client-slug}\
```

### Check Celery Worker Status

```powershell
# In dashboard directory
poetry run celery -A worker.tasks inspect active
```

### Check Redis Connection

```powershell
docker exec -it ads_sync_dashboard-redis-1 redis-cli ping
# Should return: PONG
```

---

## 📝 Environment Variables

Located in `.env` files:

### ads_sync (if needed)
- `GOOGLE_ADS_DEVELOPER_TOKEN`
- `GOOGLE_ADS_CLIENT_ID`
- `GOOGLE_ADS_CLIENT_SECRET`
- `GOOGLE_ADS_REFRESH_TOKEN`

### ads_sync_dashboard
- `REDIS_HOST=localhost`
- `REDIS_PORT=6379`
- `ADS_SYNC_PATH=../ads_sync`
- `API_PORT=8000`

---

## 🎯 Current Phase Status

### Phase 1: Data Pull ✅ Complete
- 30 clients onboarded
- 126,889 rows of historical data
- 365 days of data per client

### Phase 2: Analysis ⏳ In Progress
- [ ] Implement `append` command
- [ ] Implement `report` command
- [ ] Test incremental sync
- [ ] Generate sample reports

---

## 🆘 Emergency Contacts

**Project Owner:** OneClickSEO PPC Management  
**Email:** ppcmanager@deanknows.com  
**MCC Account ID:** 187-720-2760

---

## 📚 Documentation Index

- `README.md` - Full documentation
- `PHASE-1-COMPLETE-FINAL.md` - Phase 1 summary
- `HOUSEKEEPING-COMPLETE.md` - Cleanup summary
- `QUICK-REFERENCE.md` - This file
- `IMPLEMENTATION-GUIDE.md` - Technical implementation details

---

**Quick Reference Version:** 1.0  
**Last Updated:** October 14, 2025

