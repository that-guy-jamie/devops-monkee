# 🔄 ads_sync - Production-Grade Google Ads Data Sync & Reporting

**Version:** 0.1.0  
**Status:** Scaffolding Complete, Ready for Implementation  
**Created:** October 13, 2025

---

## 📋 Overview

`ads_sync` is a production-hardened CLI tool for syncing and reporting on Google Ads data with an incremental "sync & append" architecture. It features:

- ✅ **Incremental Sync** with watermark-based state management
- ✅ **Idempotent Deduplication** on primary keys
- ✅ **Overlap Strategy** (default 3 days) for healing late-arriving data
- ✅ **Atomic CSV Writes** with file locking
- ✅ **Schema Validation** on every write
- ✅ **Error Recovery** with pre-formatted resume commands
- ✅ **Multi-Source Support** (Google Ads, LSA, Search Terms)
- ✅ **Templated Reporting** with Jinja2

---

## 🏗️ Architecture

### Core Principles

1. **Never Delete Data** - Only append and deduplicate
2. **Idempotent Operations** - Safe to re-run any command
3. **State-Based Sync** - Watermarks track last successful pull
4. **Atomic Writes** - CSVs never in partial/corrupt state
5. **Gap Healing** - Overlap strategy catches late data
6. **Fail-Safe** - Errors logged with recovery commands

### Directory Structure

```
ads_sync/
├── configs/clients/          # Per-client YAML configs
├── data/                     # Master CSV data files
│   └── {slug}/
│       ├── {slug}-master-campaign_data.csv
│       ├── {slug}-master-lsa_data.csv
│       └── {slug}-master-search_terms.csv
├── errors/                   # Error logs with recovery commands
├── imports/                  # CSV import staging (LSA fallback)
├── locks/                    # File locks for concurrency
├── output/                   # Generated reports
│   └── {slug}/{year}/
│       └── {NNN}-{slug}-report-{scope}-{timestamp}.md
├── schemas/                  # JSON Schemas for validation
├── state/                    # Per-client state (watermarks)
├── templates/                # Jinja2 report templates
└── ads_sync_cli.py           # Main CLI tool
```

---

## 🚀 Quick Start

### Installation

```bash
# Install dependencies
pip install poetry
cd ads_sync
poetry install

# Or with pip
pip install -r requirements.txt
```

### Initial Setup

1. **Configure Client**
   ```bash
   # Edit config file
   nano configs/clients/priority-roofing.yaml
   ```

2. **Initialize Historical Data**
   ```bash
   poetry run python ads_sync_cli.py init priority-roofing
   ```

3. **Daily Incremental Sync**
   ```bash
   poetry run python ads_sync_cli.py append priority-roofing
   ```

4. **Generate Report**
   ```bash
   poetry run python ads_sync_cli.py report priority-roofing --scope LIFETIME
   ```

---

## 📖 Command Reference

### `discover` - List All Clients

Discover all clients accessible via MCC account.

```bash
python ads_sync_cli.py discover --mcc-id 1877202760 --export
```

**Outputs:** CSV with customer_id, name, status, timezone, currency, suggested_slug

---

### `init` - Historical Backfill

One-time historical data initialization for a client.

```bash
python ads_sync_cli.py init priority-roofing
```

**Process:**
1. Loads client config
2. Determines lifetime date range
3. Chunks into 90-day windows (API limit)
4. Pulls data for each chunk
5. Validates and writes to master CSVs
6. Sets initial watermarks

**Duration:** Depends on data volume (typically 5-15 minutes)

---

### `append` - Incremental Sync

Daily/weekly incremental append with watermark tracking.

```bash
python ads_sync_cli.py append priority-roofing
```

**Process:**
1. Reads last watermark from state
2. Calculates window (watermark - 3 days to yesterday)
3. Pulls new data from APIs
4. Loads master CSV
5. Appends and deduplicates
6. Atomic write
7. Updates watermark

**Duration:** Typically <30 seconds

**Frequency:** Daily (recommended) or weekly

---

### `report` - Generate Reports

Generate Markdown reports from master data (no API calls).

```bash
# Lifetime report
python ads_sync_cli.py report priority-roofing --scope LIFETIME

# Last 30 days
python ads_sync_cli.py report priority-roofing --scope LAST-30-DAYS

# Specific quarter
python ads_sync_cli.py report priority-roofing --scope 2025-Q3

# Date range
python ads_sync_cli.py report priority-roofing --scope 2025-01..2025-03
```

**Supported Scopes:**
- `LIFETIME` - All available data
- `LAST-7-DAYS` - Last 7 days
- `LAST-30-DAYS` - Last 30 days
- `YYYY-Qn` - Specific quarter (e.g., 2025-Q3)
- `YYYY-MM..YYYY-MM` - Custom date range

**Output:** `output/{slug}/{year}/{NNN}-{slug}-report-{scope}-{timestamp}.md`

---

### `validate` - Configuration Check

Validate client configuration and data integrity.

```bash
python ads_sync_cli.py validate priority-roofing
```

**Checks:**
- ✓ Config file exists and valid
- ✓ State file loaded
- ✓ Master CSV files exist
- ✓ Schema validation on sample data
- ✓ Date gap detection

---

### `repair` - Fix Data Gaps

Re-pull data for a specific date range (idempotent).

```bash
python ads_sync_cli.py repair priority-roofing --start 2025-09-01 --end 2025-09-30
```

**Use Cases:**
- Fill gaps from API failures
- Refresh stale data
- Resume failed init/append operations

---

### `force-unlock` - Manual Lock Removal

Manually remove lock file (use with caution!).

```bash
python ads_sync_cli.py force-unlock priority-roofing
```

**When to Use:**
- Process crashed without releasing lock
- Lock timeout exceeded
- Emergency override needed

---

## 📊 Data Schemas

### Campaign Data (v1)

Primary Key: `(date, campaign_id, data_source)`

| Column | Type | Description |
|--------|------|-------------|
| data_source | string | "google_ads" |
| pull_date | datetime | UTC timestamp |
| date | date | Client local date |
| campaign_id | string | Numeric ID (no dashes) |
| campaign_name | string | Campaign name |
| campaign_status | enum | ENABLED/PAUSED/REMOVED |
| impressions | integer | Impression count |
| clicks | integer | Click count |
| cost | float | Cost in USD |
| conversions | float | Primary conversions |
| conversions_value | float | Conversion value USD |
| all_conversions | float | Incl. view-through |
| view_through_conversions | float | VTC only |
| ctr | float | Computed: clicks/impressions |
| avg_cpc | float | Computed: cost/clicks |
| cpa | float | Computed: cost/conversions |
| conv_rate | float | Computed: conversions/clicks |
| currency_code | string | ISO 4217 (USD) |
| schema_version | integer | 1 |

### LSA Data (v1)

Primary Key: `(date, lead_id, data_source)`

| Column | Type | Description |
|--------|------|-------------|
| data_source | string | "google_lsa" |
| pull_date | datetime | UTC timestamp |
| date | date | Lead received date |
| lead_id | string | Unique lead ID |
| lead_status | enum | BOOKED/MISSED/DISPUTED/OTHER |
| cost | float | Lead cost USD |
| disputed | boolean | Dispute flag |
| call_duration_seconds | integer | Call length |
| needs_survey_response | boolean | Survey needed flag |
| currency_code | string | ISO 4217 (USD) |
| schema_version | integer | 1 |

---

## ⚙️ Configuration

### Client Config (`configs/clients/{slug}.yaml`)

```yaml
customer_id: "4139022884"
slug: "priority-roofing"
client_name: "Priority Roofing"
timezone: "America/Chicago"
currency_code: "USD"
mcc_customer_id: "1877202760"

data_sources:
  google_ads:
    enabled: true
    granularity: "CAMPAIGN"
    channel_types:
      - "SEARCH"
      - "PERFORMANCE_MAX"
  
  google_lsa:
    enabled: true
    import_method: "csv"  # or "api" when available
    csv_path: "imports/priority-roofing/lsa/"
  
  search_terms:
    enabled: false  # Optional

sync:
  overlap_days: 3
  max_window_days: 30
  backfill_chunk_days: 90

lsa:
  needs_survey_response:
    conditions:
      - lead_status: "MISSED"
      - disputed: true
      - call_duration_seconds_lt: 60

reporting:
  default_template: "campaign_report.md.j2"
  timezone: "America/Chicago"

conversions:
  primary_action: "conversions"
  include_view_through: true

validation:
  enforce_schema: true
  log_anomalies: true
```

---

## 🔒 Concurrency & Locking

- **File-Based Locks** prevent concurrent operations on same client
- **Timeout:** 5 minutes (configurable)
- **PID Tracking:** Lock files contain process ID for diagnostics
- **Stale Detection:** Auto-removes locks from dead processes

---

## 🔄 Watermark Strategy

**Overlap Strategy:**
- Always re-pull last 3 days (configurable)
- Handles late-arriving data from API
- Deduplication ensures no duplicates

**Example:**
```
Watermark: 2025-10-10
Overlap: 3 days
Window: 2025-10-07 to 2025-10-12 (yesterday)
```

---

## 🛠️ Development

### Running Tests

```bash
poetry run pytest
```

### Linting & Formatting

```bash
poetry run black .
poetry run ruff check .
```

### Local Development

```bash
# Run in development mode
python ads_sync_cli.py --help

# Test on one client
python ads_sync_cli.py validate priority-roofing
```

---

## 📅 Automation

### Cron Job (Linux/Mac)

```cron
# Daily append at 8:15 AM CT
15 8 * * * cd /path/to/ads_sync && python ads_sync_cli.py append priority-roofing

# Weekly report on Mondays at 9:00 AM CT
0 9 * * 1 cd /path/to/ads_sync && python ads_sync_cli.py report priority-roofing --scope LAST-7-DAYS
```

### Windows Task Scheduler

```powershell
# Daily append
schtasks /create /tn "ads_sync_daily" /tr "python C:\path\to\ads_sync\ads_sync_cli.py append priority-roofing" /sc daily /st 08:15

# Weekly report
schtasks /create /tn "ads_sync_weekly_report" /tr "python C:\path\to\ads_sync\ads_sync_cli.py report priority-roofing --scope LAST-7-DAYS" /sc weekly /d MON /st 09:00
```

---

## 🎯 Roadmap

### v0.1.0 (✓ Complete - Phase 1)
- ✅ Complete directory structure
- ✅ CLI framework with all commands
- ✅ Config and schema files
- ✅ Locking and state management
- ✅ Report templates
- ✅ Google Ads API integration (init command)
- ✅ GAQL query builder
- ✅ Data transformation pipeline
- ✅ CSV append & dedup logic
- ✅ 30 clients onboarded
- ✅ 126,889 rows of historical data pulled

### v0.2.0 (Current - Phase 2: Analysis)
- [ ] Complete `append` command implementation
- [ ] Complete `report` command with Jinja2 templates
- [ ] Complete `repair` command
- [ ] Data validation enhancements
- [ ] Basic reporting for top clients

### v0.3.0 (Implementation Phase 2)
- [ ] LSA CSV importer
- [ ] Search terms support
- [ ] Enhanced reporting
- [ ] Data quality checks
- [ ] Error recovery

### v0.4.0 (Production Hardening)
- [ ] Comprehensive testing
- [ ] Performance optimization
- [ ] Documentation completion
- [ ] Deployment guides

### v1.0.0 (Production Release)
- [ ] All features implemented
- [ ] Production tested with 23 clients
- [ ] CI/CD pipeline
- [ ] Monitoring and alerts

---

## 📞 Support

**Project:** ads_sync  
**Organization:** OneClickSEO PPC Management  
**Contact:** ppcmanager@deanknows.com  
**Version:** 0.1.0

---

## 📄 License

Proprietary - OneClickSEO PPC Management  
All rights reserved.

---

**Built with ❤️ for production-grade Google Ads data management**

