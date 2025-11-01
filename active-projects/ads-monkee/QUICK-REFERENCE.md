# Ads Monkee Quick Reference

## 🚀 Quick Start

### Import CSV Data
```bash
cd ads-monkee

# Import single client
poetry run python scripts/import_csv_data.py --client priority-roofing

# Import all clients
poetry run python scripts/import_csv_data.py --all

# Clear existing data first
poetry run python scripts/import_csv_data.py --client priority-roofing --clear
```

### Test Google Ads API
```bash
cd ads-monkee
poetry run python scripts/test_google_ads_api.py
```

### Database Migrations
```bash
cd ads-monkee

# Generate new migration
poetry run alembic revision --autogenerate -m "Description"

# Apply migrations
poetry run alembic upgrade head

# Rollback one migration
poetry run alembic downgrade -1
```

### Run Development Server
```bash
cd ads-monkee
poetry run uvicorn backend.main:app --reload --port 8000
```

---

## 📊 Database

### Connection String
```
postgresql://ads_monkee_user:***@dpg-***-a.oregon-postgres.render.com/ads_monkee?sslmode=require
```

### Tables (17 total)
- `clients` - Client accounts
- `users` - User accounts
- `auth_sessions` - Authentication
- `audit_log` - Audit trail
- `google_ads_campaigns` - Campaign data
- `google_ads_ad_groups` - Ad group data
- `google_ads_keywords` - Keyword data
- `google_ads_search_terms` - Search term data
- `reports` - Analysis reports
- `campaign_modifications` - Proposed changes
- `ai_consensus_sessions` - AI debates
- `lsa_leads` - LSA lead data
- `lsa_metrics` - LSA metrics
- `lsa_survey_attempts` - Survey logs

---

## 🔑 Environment Variables

### Required
```bash
# Database
DATABASE_URL=postgresql://...?sslmode=require

# Google Ads API
GOOGLE_ADS_DEVELOPER_TOKEN=***
GOOGLE_ADS_CLIENT_ID=***
GOOGLE_ADS_CLIENT_SECRET=***
GOOGLE_ADS_REFRESH_TOKEN=***
GOOGLE_ADS_LOGIN_CUSTOMER_ID=1877202760

# Application
SECRET_KEY=***
ENVIRONMENT=development
```

---

## 📁 Project Structure

```
ads-monkee/
├── backend/           # FastAPI application
│   ├── config.py      # Settings
│   ├── database.py    # SQLAlchemy setup
│   ├── main.py        # FastAPI app
│   ├── models/        # Database models
│   └── services/      # Business logic
├── database/
│   └── migrations/    # Alembic migrations
├── scripts/           # Utility scripts
│   ├── import_csv_data.py
│   └── test_google_ads_api.py
├── docs/              # Documentation
│   ├── PARALLEL-CAMPAIGN-STRATEGY.md
│   └── DATABASE-REQUIREMENTS.md
├── tests/             # Test suite
├── pyproject.toml     # Poetry dependencies
└── .env               # Environment variables
```

---

## 🛠️ Common Commands

### Poetry
```bash
# Install dependencies
poetry install

# Add new package
poetry add package-name

# Update package
poetry update package-name

# Show installed packages
poetry show
```

### Database
```bash
# Connect to database (psql)
psql "postgresql://ads_monkee_user:***@dpg-***-a.oregon-postgres.render.com/ads_monkee?sslmode=require"

# List tables
\dt

# Describe table
\d table_name

# Exit
\q
```

---

## 📈 Import Stats

### Priority Roofing (Last Import)
- **Total Records**: 12,053
- **Campaigns**: 156
- **Ad Groups**: 1,599
- **Keywords**: (included in total)
- **Search Terms**: 10,298
- **Import Time**: ~2 minutes

---

## 🔧 Troubleshooting

### Database Connection Issues
1. Check IP is allowlisted: `152.36.150.226/32`
2. Verify SSL mode: `?sslmode=require`
3. Test connection: `psql "connection_string"`

### Google Ads API Issues
1. Check library version: `poetry show google-ads` (should be v28.2.0)
2. Verify credentials in `google-ads.yaml`
3. Run test script: `poetry run python scripts/test_google_ads_api.py`

### Import Errors
1. Check CSV files exist in `ads_sync/data/{client}/comprehensive/`
2. Verify database connection
3. Use `--clear` flag if duplicate key errors

---

## 📚 Documentation

- **SBEP Mandate**: `sds/SBEP-MANDATE.md`
- **Database Schema**: `docs/DATABASE-REQUIREMENTS.md`
- **Parallel Campaign Strategy**: `docs/PARALLEL-CAMPAIGN-STRATEGY.md`
- **Session Summary**: `SESSION-SUMMARY-2025-10-18.md`
- **Changelog**: `CHANGELOG.md`

---

## 🎯 Next Steps

1. Import remaining clients
2. Test live API data pulling
3. Implement GPT analysis engine
4. Build frontend dashboard
5. Set up authentication
6. Configure automated syncing

---

**Last Updated**: 2025-10-18  
**Version**: 0.2.0

