# 🚀 Ads Monkee - Setup NOW (Database Ready!)

**Database Status:** ✅ Available  
**Time to Migration:** 10 minutes setup + 45 minutes migration

---

## Step 1: Get Database Connection Strings (2 minutes)

### Go to Render Dashboard:
https://dashboard.render.com/d/dpg-d3oplg9r0fns73dom48g-a

### Copy Both URLs:

**Internal URL** (starts with `postgresql://ads_monkee_db_basic_user:...@dpg-...internal...`)
- For Render services (web service, worker)
- Will use this later when deploying

**External URL** (starts with `postgresql://ads_monkee_db_basic_user:...@dpg-...oregon-postgres.render.com...`)
- For local development
- Need this NOW for migration

---

## Step 2: Create .env File (1 minute)

```bash
cd ads-monkee

# Copy example
cp env.example .env

# Edit .env with your favorite editor
notepad .env
# OR
code .env
```

### Required in .env:

```bash
# Database - PASTE EXTERNAL URL HERE
DATABASE_URL=postgresql://ads_monkee_db_basic_user:PASSWORD@dpg-xxx.oregon-postgres.render.com:5432/ads_monkee_db_basic

# Google Ads - Copy from ads_sync/google-ads.yaml or existing .env
GOOGLE_ADS_DEVELOPER_TOKEN=your_dev_token_here
GOOGLE_ADS_CLIENT_ID=your_client_id.apps.googleusercontent.com
GOOGLE_ADS_CLIENT_SECRET=your_client_secret
GOOGLE_ADS_REFRESH_TOKEN=your_refresh_token
GOOGLE_ADS_LOGIN_CUSTOMER_ID=1234567890

# JWT Secret - Generate random 32+ characters
JWT_SECRET=your-super-secret-jwt-key-min-32-chars

# App Config
ENVIRONMENT=development
LOG_LEVEL=DEBUG

# Optional (can set later)
REDIS_URL=
ANTHROPIC_API_KEY=
GHL_API_KEY=
```

**Pro Tip:** Get Google Ads credentials from:
- `C:\Users\james\Desktop\Projects\ads_sync\google-ads.yaml`
- Or `C:\Users\james\Desktop\Projects\.env`

---

## Step 3: Install Dependencies (1 minute)

```bash
cd ads-monkee
poetry install
```

---

## Step 4: Run Migrations (1 minute)

```bash
# Generate initial migration
poetry run alembic revision --autogenerate -m "Initial schema - 17 tables"

# Apply migration
poetry run alembic upgrade head
```

**Expected output:**
```
INFO  [alembic.runtime.migration] Running upgrade -> abc123, Initial schema
✅ Created tables
```

---

## Step 5: Seed Clients (2 minutes)

```bash
poetry run python scripts/seed_clients.py
```

**Expected output:**
```
Connecting to Google Ads API...
✅ Found 30 client accounts
Creating database records...
  ✅ Created 'Priority Roofing' (slug: priority-roofing)
  ✅ Created 'Heather Murphy Group' (slug: heather-murphy-group)
  [... 28 more ...]
SUMMARY: Created: 30, Skipped: 0, Total: 30
```

---

## Step 6: Verify Setup (30 seconds)

```bash
# Check clients in database
poetry run python -c "
from backend.database import SessionLocal
from backend.models import Client
s = SessionLocal()
count = s.query(Client).count()
print(f'✅ Clients in database: {count}')
s.close()
"
```

**Expected:** `✅ Clients in database: 30`

---

## Step 7: Migrate Data! (45 minutes - walk away)

### Dry Run First (Recommended):
```bash
poetry run python scripts/migrate_all_clients_data.py --dry-run
```

### Full Migration:
```bash
poetry run python scripts/migrate_all_clients_data.py
```

**This will:**
- Pull 1 year of data for all 30 clients
- Fetch campaigns, ad groups, keywords, search terms
- Insert ~300k-500k rows into PostgreSQL
- Take ~30-45 minutes (progress shown in real-time)

---

## Step 8: Verify Migration (1 minute)

```bash
poetry run python -c "
from backend.database import SessionLocal
from backend.models import GoogleAdsCampaign, GoogleAdsKeyword, GoogleAdsSearchTerm
s = SessionLocal()
print(f'✅ Campaigns: {s.query(GoogleAdsCampaign).count():,}')
print(f'✅ Keywords: {s.query(GoogleAdsKeyword).count():,}')
print(f'✅ Search Terms: {s.query(GoogleAdsSearchTerm).count():,}')
s.close()
"
```

**Expected:**
```
✅ Campaigns: 4,500-5,000
✅ Keywords: 30,000-40,000
✅ Search Terms: 300,000-400,000
```

---

## Quick Test: Priority Roofing Data

```bash
poetry run python -c "
from backend.database import SessionLocal
from backend.models import GoogleAdsCampaign, Client
from sqlalchemy import func
from datetime import datetime, timedelta

s = SessionLocal()
client = s.query(Client).filter_by(slug='priority-roofing').first()

if client:
    cutoff = datetime.now().date() - timedelta(days=30)
    campaigns = s.query(
        GoogleAdsCampaign.campaign_name,
        func.sum(GoogleAdsCampaign.cost).label('cost'),
        func.sum(GoogleAdsCampaign.conversions).label('conversions')
    ).filter(
        GoogleAdsCampaign.client_id == client.id,
        GoogleAdsCampaign.date >= cutoff
    ).group_by(GoogleAdsCampaign.campaign_name).all()
    
    print(f'Priority Roofing - Last 30 Days:')
    for camp in campaigns:
        print(f'  {camp.campaign_name}: \${camp.cost:.2f}, {camp.conversions:.0f} conv')
else:
    print('Client not found - run seed_clients.py first')

s.close()
"
```

---

## 🎉 SUCCESS!

After migration completes, you'll have:
- ✅ 30 clients in database
- ✅ 1 year of comprehensive data
- ✅ Ready for AI analysis and recommendations
- ✅ Foundation for multi-agent consensus framework

---

## Optional: Historical Backfill (Later)

**After operational migration is done**, optionally run:

```bash
# 2 years of historical data (3-5 hours)
poetry run python scripts/backfill_historical_data.py --years 2
```

This adds 2-5 years of historical data for:
- Seasonal trend analysis
- Pattern discovery
- "Hidden gems" from past campaigns

---

## Troubleshooting

### "Can't connect to database"
- Check `.env` has EXTERNAL database URL
- Verify URL copied correctly (long password string)

### "Google Ads API error"
- Verify `google-ads.yaml` exists in project root or home directory
- Or copy credentials to `.env` as shown above

### "No clients found"
- Make sure `seed_clients.py` ran successfully
- Check output showed "Created: 30"

---

## Next Steps After Migration

1. **Start FastAPI server:**
   ```bash
   poetry run uvicorn backend.main:app --reload
   ```

2. **Test health endpoint:**
   ```bash
   curl http://localhost:8000/health
   ```

3. **Run PPC analysis:**
   ```bash
   poetry run python backend/services/ppc_analyzer.py --client priority-roofing
   ```

4. **Deploy to Render:**
   - Commit changes
   - Push to Git
   - Use render.yaml blueprint in dashboard

---

**Current Status:** Database ready, Redis ready, scripts ready. Just need .env file and you're off! 🚀

