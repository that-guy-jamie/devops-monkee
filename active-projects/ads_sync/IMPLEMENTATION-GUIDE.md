# 🛠️ Implementation Guide: ads_sync

**Status:** Scaffolding Complete - Ready for Implementation  
**Created:** October 13, 2025  
**Target:** Production-Ready v1.0.0

---

## 📋 Current Status

### ✅ Complete (Scaffolding)

1. **Directory Structure** - All folders created
2. **Configuration Files** - Sample configs for 2 clients
3. **JSON Schemas** - Campaign, LSA, Search Terms (v1)
4. **Report Template** - Jinja2 template with all sections
5. **CLI Framework** - All commands stubbed with handlers
6. **Utility Functions** - Locking, state, validation, dedup logic
7. **Documentation** - README, this guide, inline docs

### ⏳ Pending Implementation

1. **Google Ads API Integration** - GAQL queries and auth
2. **Data Transformation** - Raw API → CSV format
3. **CSV Operations** - Load, append, write logic
4. **Report Generation** - Template rendering with real data
5. **Testing** - Unit, integration, and golden tests
6. **Deployment** - Automation scripts and CI/CD

---

## 🎯 Implementation Phases

### **Phase 1: API Integration (Week 1-2)**

#### 1.1 Google Ads Client Setup

**File:** Create `src/api/google_ads_client.py`

```python
from google.ads.googleads.client import GoogleAdsClient
from pathlib import Path

def get_client(mcc_id: str) -> GoogleAdsClient:
    """Initialize Google Ads API client."""
    yaml_path = Path("google-ads.yaml")  # or from env
    client = GoogleAdsClient.load_from_storage(str(yaml_path))
    client.login_customer_id = mcc_id.replace('-', '')
    return client
```

#### 1.2 Campaign Data GAQL Query

**File:** Create `src/api/queries.py`

```python
def build_campaign_query(start_date: str, end_date: str) -> str:
    """
    Build GAQL query for campaign-level data.
    
    Includes enhanced conversion metrics per specification.
    """
    return f"""
        SELECT
            customer.currency_code,
            customer.time_zone,
            campaign.id,
            campaign.name,
            campaign.status,
            campaign.advertising_channel_type,
            segments.date,
            metrics.impressions,
            metrics.clicks,
            metrics.cost_micros,
            metrics.conversions,
            metrics.conversions_value,
            metrics.all_conversions,
            metrics.view_through_conversions
        FROM campaign
        WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
          AND campaign.advertising_channel_type IN ('SEARCH', 'PERFORMANCE_MAX')
          AND campaign.status IN ('ENABLED', 'PAUSED')
        ORDER BY segments.date, campaign.id
    """
```

#### 1.3 Data Fetching with Pagination

**File:** Extend `src/api/fetcher.py`

```python
def fetch_campaign_data(
    client: GoogleAdsClient,
    customer_id: str,
    start_date: str,
    end_date: str
) -> List[Dict]:
    """
    Fetch campaign data with pagination and retry logic.
    
    Returns list of dicts with all metrics.
    """
    ga_service = client.get_service("GoogleAdsService")
    query = build_campaign_query(start_date, end_date)
    
    rows = []
    try:
        stream = ga_service.search_stream(
            customer_id=customer_id.replace('-', ''),
            query=query
        )
        
        for batch in stream:
            for row in batch.results:
                rows.append(transform_campaign_row(row))
    
    except GoogleAdsException as ex:
        # Handle rate limits, errors
        logger.error(f"API error: {ex}")
        raise
    
    return rows
```

#### 1.4 Data Transformation

**File:** Create `src/transformers/campaign_transformer.py`

```python
from datetime import datetime
import pytz

def transform_campaign_row(row, pull_timestamp: str, client_tz: str) -> Dict:
    """
    Transform Google Ads API row to our schema format.
    
    Handles:
    - cost_micros → USD
    - Computed metrics (CTR, CPC, CPA, conv_rate)
    - Timezone conversion
    - Schema version tagging
    """
    impressions = row.metrics.impressions
    clicks = row.metrics.clicks
    cost = row.metrics.cost_micros / 1_000_000
    conversions = row.metrics.conversions
    
    # Computed metrics
    ctr = clicks / impressions if impressions > 0 else None
    avg_cpc = cost / clicks if clicks > 0 else None
    cpa = cost / conversions if conversions > 0 else None
    conv_rate = conversions / clicks if clicks > 0 else None
    
    return {
        "data_source": "google_ads",
        "pull_date": pull_timestamp,
        "date": str(row.segments.date),  # Already in client tz
        "campaign_id": str(row.campaign.id),
        "campaign_name": row.campaign.name,
        "campaign_status": row.campaign.status.name,
        "impressions": impressions,
        "clicks": clicks,
        "cost": round(cost, 2),
        "conversions": conversions,
        "conversions_value": row.metrics.conversions_value,
        "all_conversions": row.metrics.all_conversions,
        "view_through_conversions": row.metrics.view_through_conversions,
        "ctr": round(ctr, 4) if ctr else None,
        "avg_cpc": round(avg_cpc, 2) if avg_cpc else None,
        "cpa": round(cpa, 2) if cpa else None,
        "conv_rate": round(conv_rate, 4) if conv_rate else None,
        "currency_code": row.customer.currency_code,
        "schema_version": 1
    }
```

**Integration Point:** Call from `handle_init()` and `handle_append()` in `ads_sync_cli.py`

---

### **Phase 2: CSV Operations (Week 2-3)**

#### 2.1 Load Master CSV

```python
def load_master_csv(slug: str, data_type: str = "campaign_data") -> pd.DataFrame:
    """
    Load master CSV into DataFrame.
    
    Args:
        slug: Client slug
        data_type: "campaign_data", "lsa_data", or "search_terms"
    
    Returns:
        DataFrame or empty DataFrame if file doesn't exist
    """
    csv_path = DATA_DIR / slug / f"{slug}-master-{data_type}.csv"
    
    if csv_path.exists():
        df = pd.read_csv(csv_path, parse_dates=["pull_date", "date"])
        logger.info(f"Loaded {len(df)} rows from {csv_path}")
        return df
    else:
        # Return empty DataFrame with correct schema
        logger.info(f"No existing data, starting fresh: {csv_path}")
        return pd.DataFrame(columns=get_schema_columns(data_type))


def get_schema_columns(data_type: str) -> List[str]:
    """Get column names from schema."""
    schema = load_schema(f"{data_type}_v1")
    return list(schema["properties"].keys())
```

#### 2.2 Append and Deduplicate

```python
def append_and_deduplicate(
    df_master: pd.DataFrame,
    df_new: pd.DataFrame,
    primary_keys: List[str]
) -> pd.DataFrame:
    """
    Append new data and deduplicate on primary keys.
    
    Strategy: keep='last' ensures latest data wins.
    """
    # Concatenate
    df_combined = pd.concat([df_master, df_new], ignore_index=True)
    
    # Deduplicate
    df_dedup = df_combined.drop_duplicates(
        subset=primary_keys,
        keep="last"
    )
    
    removed = len(df_combined) - len(df_dedup)
    if removed > 0:
        logger.info(f"Removed {removed} duplicate rows")
    
    # Sort by date
    df_dedup = df_dedup.sort_values(by=["date", primary_keys[1]])
    
    return df_dedup
```

**Integration Point:** Call from `handle_append()` after fetching new data

---

### **Phase 3: State Management (Week 3)**

#### 3.1 Watermark Update

```python
def update_watermark(
    slug: str,
    data_source: str,
    new_watermark: str,
    rows_added: int
):
    """
    Update watermark in state file after successful sync.
    
    Only updates if operation succeeds to ensure consistency.
    """
    state = load_client_state(slug)
    
    state[data_source]["watermark_date"] = new_watermark
    state[data_source]["last_sync"] = datetime.utcnow().isoformat() + "Z"
    state[data_source]["rows_added_last_sync"] = rows_added
    
    # Update data quality stats
    state["data_quality"]["total_rows"] += rows_added
    state["data_quality"]["last_validation"] = datetime.utcnow().isoformat() + "Z"
    
    save_client_state(slug, state)
    logger.info(f"Updated {data_source} watermark to {new_watermark}")
```

#### 3.2 Gap Detection

```python
def detect_date_gaps(df: pd.DataFrame, expected_days: int = 365) -> List[str]:
    """
    Detect missing dates in data.
    
    Returns list of missing date ranges: ["2025-09-15..2025-09-18", ...]
    """
    if len(df) == 0:
        return []
    
    dates = pd.to_datetime(df["date"]).dt.date.unique()
    dates_sorted = sorted(dates)
    
    gaps = []
    for i in range(len(dates_sorted) - 1):
        current = dates_sorted[i]
        next_date = dates_sorted[i + 1]
        expected_next = current + timedelta(days=1)
        
        if next_date != expected_next:
            gap_days = (next_date - current).days - 1
            if gap_days > 0:
                gaps.append(f"{current + timedelta(days=1)}..{next_date - timedelta(days=1)}")
    
    return gaps
```

**Integration Point:** Call from `handle_validate()` and update state

---

### **Phase 4: Reporting (Week 4)**

#### 4.1 Data Aggregation

```python
def aggregate_campaign_data(df: pd.DataFrame, scope: str) -> Dict:
    """
    Aggregate campaign data for reporting.
    
    Args:
        df: Campaign DataFrame
        scope: LIFETIME, LAST-30-DAYS, etc.
    
    Returns:
        Dict with aggregated metrics
    """
    # Filter by scope
    df_filtered = filter_by_scope(df, scope)
    
    # Overall metrics
    totals = {
        "total_cost": df_filtered["cost"].sum(),
        "total_impressions": df_filtered["impressions"].sum(),
        "total_clicks": df_filtered["clicks"].sum(),
        "total_conversions": df_filtered["conversions"].sum(),
        "total_conversions_value": df_filtered["conversions_value"].sum(),
        "all_conversions": df_filtered["all_conversions"].sum(),
        "view_through_conversions": df_filtered["view_through_conversions"].sum(),
    }
    
    # Computed metrics
    totals["overall_ctr"] = (totals["total_clicks"] / totals["total_impressions"] * 100) if totals["total_impressions"] > 0 else 0
    totals["average_cpc"] = totals["total_cost"] / totals["total_clicks"] if totals["total_clicks"] > 0 else 0
    totals["cpa"] = totals["total_cost"] / totals["total_conversions"] if totals["total_conversions"] > 0 else None
    totals["conv_rate"] = (totals["total_conversions"] / totals["total_clicks"] * 100) if totals["total_clicks"] > 0 else 0
    
    # Per-campaign breakdown
    campaigns = df_filtered.groupby(["campaign_id", "campaign_name", "campaign_status"]).agg({
        "cost": "sum",
        "impressions": "sum",
        "clicks": "sum",
        "conversions": "sum"
    }).reset_index()
    
    # Add computed metrics per campaign
    campaigns["ctr"] = campaigns["clicks"] / campaigns["impressions"]
    campaigns["avg_cpc"] = campaigns["cost"] / campaigns["clicks"]
    campaigns["cpa"] = campaigns["cost"] / campaigns["conversions"]
    
    return {
        **totals,
        "campaigns": campaigns.to_dict("records")
    }


def filter_by_scope(df: pd.DataFrame, scope: str) -> pd.DataFrame:
    """Filter DataFrame by report scope."""
    if scope == "LIFETIME":
        return df
    elif scope == "LAST-7-DAYS":
        cutoff = datetime.now().date() - timedelta(days=7)
        return df[pd.to_datetime(df["date"]).dt.date >= cutoff]
    elif scope == "LAST-30-DAYS":
        cutoff = datetime.now().date() - timedelta(days=30)
        return df[pd.to_datetime(df["date"]).dt.date >= cutoff]
    elif scope.startswith("2025-Q"):
        # Parse quarter
        # TODO: Implement quarter parsing
        pass
    else:
        # Custom range: 2025-01..2025-03
        # TODO: Implement range parsing
        pass
```

#### 4.2 Template Rendering

```python
from jinja2 import Environment, FileSystemLoader

def render_report(
    slug: str,
    config: Dict,
    aggregated_data: Dict,
    scope: str
) -> str:
    """
    Render Jinja2 template with aggregated data.
    
    Returns rendered Markdown string.
    """
    env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))
    template = env.get_template(config["reporting"]["default_template"])
    
    context = {
        "client_name": config["client_name"],
        "customer_id": config["customer_id"],
        "mcc_customer_id": config["mcc_customer_id"],
        "timezone": config["timezone"],
        "currency_code": config["currency_code"],
        "date_scope": scope,
        "generation_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "schema_version": SCHEMA_VERSION,
        "tool_version": VERSION,
        **aggregated_data
    }
    
    return template.render(**context)
```

**Integration Point:** Call from `handle_report()`

---

### **Phase 5: LSA Integration (Week 5)**

#### 5.1 CSV Importer

```python
def import_lsa_csv(slug: str, csv_path: Path) -> pd.DataFrame:
    """
    Import LSA data from CSV export.
    
    Expected columns:
    - lead_id
    - date (or date_received)
    - status (or lead_status)
    - cost (or charge_amount)
    - disputed (boolean or Y/N)
    - call_duration_seconds (optional)
    
    Transforms to our schema format.
    """
    df_raw = pd.read_csv(csv_path)
    
    # Column mapping (adjust based on actual CSV format)
    column_map = {
        "Lead ID": "lead_id",
        "Date": "date",
        "Status": "lead_status",
        "Cost": "cost",
        "Disputed": "disputed"
    }
    
    df_renamed = df_raw.rename(columns=column_map)
    
    # Transform to schema
    df_transformed = df_renamed.apply(transform_lsa_row, axis=1)
    
    return pd.DataFrame(df_transformed.tolist())


def transform_lsa_row(row: pd.Series) -> Dict:
    """Transform LSA row to schema format."""
    # Apply needs_survey_response rule
    needs_survey = (
        row.get("lead_status") == "MISSED" or
        row.get("disputed", False) or
        (row.get("call_duration_seconds", 999) < 60)
    )
    
    return {
        "data_source": "google_lsa",
        "pull_date": datetime.utcnow().isoformat() + "Z",
        "date": row["date"],
        "lead_id": row["lead_id"],
        "lead_status": row["lead_status"],
        "cost": float(row["cost"]),
        "disputed": bool(row["disputed"]),
        "call_duration_seconds": row.get("call_duration_seconds"),
        "needs_survey_response": needs_survey,
        "currency_code": "USD",
        "schema_version": 1
    }
```

**Integration Point:** Call from `handle_append()` if LSA enabled in config

---

### **Phase 6: Testing (Week 6-7)**

#### 6.1 Unit Tests

**File:** Create `tests/test_transformers.py`

```python
import pytest
from src.transformers.campaign_transformer import transform_campaign_row

def test_cost_micros_conversion():
    """Test that cost_micros is correctly converted to USD."""
    row = MockRow(cost_micros=1_500_000)  # $1.50
    result = transform_campaign_row(row)
    assert result["cost"] == 1.50

def test_ctr_calculation():
    """Test CTR computation."""
    row = MockRow(impressions=1000, clicks=50)
    result = transform_campaign_row(row)
    assert result["ctr"] == 0.05  # 5%

def test_division_by_zero():
    """Test that division by zero returns None."""
    row = MockRow(impressions=0, clicks=0)
    result = transform_campaign_row(row)
    assert result["ctr"] is None
    assert result["avg_cpc"] is None
```

#### 6.2 Integration Tests

**File:** Create `tests/test_sync.py`

```python
def test_idempotent_append():
    """Test that appending same data twice results in identical output."""
    slug = "test-client"
    
    # First append
    df1 = append_data(slug, mock_api_data())
    hash1 = hashlib.md5(df1.to_csv().encode()).hexdigest()
    
    # Second append (same data)
    df2 = append_data(slug, mock_api_data())
    hash2 = hashlib.md5(df2.to_csv().encode()).hexdigest()
    
    assert hash1 == hash2, "Idempotency violated: file changed"
```

#### 6.3 Golden Tests

**File:** Create `tests/test_reports.py`

```python
def test_report_golden():
    """Test report output matches golden file."""
    aggregated_data = load_fixture("test_data.json")
    report = render_report("test-client", mock_config(), aggregated_data, "LIFETIME")
    
    golden_path = "tests/golden/lifetime_report.md"
    with open(golden_path) as f:
        expected = f.read()
    
    assert report == expected, "Report output changed from golden file"
```

---

### **Phase 7: Deployment (Week 8)**

#### 7.1 Requirements File

```bash
# Generate from poetry
poetry export -f requirements.txt --output requirements.txt --without-hashes
```

#### 7.2 Automation Script

**File:** Create `scripts/daily_sync.sh`

```bash
#!/bin/bash
# Daily sync script for all clients

CLIENTS=(
    "priority-roofing"
    "abe-lincoln-movers"
    # Add all 23 clients
)

for client in "${CLIENTS[@]}"; do
    echo "Syncing $client..."
    python ads_sync_cli.py append "$client"
    
    if [ $? -eq 0 ]; then
        echo "✓ $client synced successfully"
    else
        echo "✗ $client sync failed"
    fi
done

# Generate weekly reports on Mondays
if [ $(date +%u) -eq 1 ]; then
    for client in "${CLIENTS[@]}"; do
        python ads_sync_cli.py report "$client" --scope LAST-7-DAYS
    done
fi
```

#### 7.3 Monitoring

**File:** Create `scripts/health_check.py`

```python
def check_sync_health():
    """Check if all clients have recent syncs."""
    issues = []
    
    for slug in get_all_clients():
        state = load_client_state(slug)
        last_sync = state["google_ads"].get("last_sync")
        
        if not last_sync:
            issues.append(f"{slug}: Never synced")
            continue
        
        last_sync_dt = datetime.fromisoformat(last_sync.rstrip('Z'))
        age = datetime.utcnow() - last_sync_dt
        
        if age > timedelta(days=2):
            issues.append(f"{slug}: Stale sync ({age.days} days old)")
    
    if issues:
        # Send alert (email, Slack, etc.)
        send_alert("Sync Health Issues", "\n".join(issues))
    
    return len(issues) == 0
```

---

## 🎯 Implementation Checklist

### Week 1-2: API Integration
- [ ] Set up Google Ads API client
- [ ] Implement GAQL query builder
- [ ] Add pagination and error handling
- [ ] Create data transformer
- [ ] Test with Priority Roofing (1 client)

### Week 2-3: CSV Operations
- [ ] Implement CSV load/write functions
- [ ] Add deduplication logic
- [ ] Test atomic writes
- [ ] Verify idempotency
- [ ] Test with Abe Lincoln Movers

### Week 3: State Management
- [ ] Implement watermark updates
- [ ] Add gap detection
- [ ] Test overlap strategy
- [ ] Verify state consistency

### Week 4: Reporting
- [ ] Implement data aggregation
- [ ] Add scope filtering
- [ ] Render Jinja2 templates
- [ ] Test all report scopes
- [ ] Generate sample reports

### Week 5: LSA Integration
- [ ] Create CSV importer
- [ ] Add needs_survey_response logic
- [ ] Test with sample LSA data
- [ ] Document CSV format

### Week 6-7: Testing
- [ ] Write unit tests (80%+ coverage)
- [ ] Write integration tests
- [ ] Create golden test files
- [ ] Test with all 23 clients
- [ ] Load testing

### Week 8: Deployment
- [ ] Create automation scripts
- [ ] Set up monitoring
- [ ] Deploy to production
- [ ] Document operations
- [ ] Training for team

---

## 📊 Success Criteria

### Functional Requirements
- ✓ Can sync all 23 OneClickSEO clients
- ✓ Idempotent operations (safe to re-run)
- ✓ Handles API rate limits gracefully
- ✓ Detects and heals data gaps
- ✓ Generates accurate reports

### Performance Requirements
- ✓ Init completes in <15 minutes per client
- ✓ Append completes in <30 seconds per client
- ✓ Report generation <5 seconds
- ✓ Handles 365+ days of data

### Reliability Requirements
- ✓ No data loss on failures
- ✓ Automatic error recovery
- ✓ Lock timeout prevents deadlocks
- ✓ State always consistent

---

## 📞 Next Steps

1. **Review this guide** - Ensure all requirements captured
2. **Set up development environment** - Install dependencies
3. **Begin Phase 1** - API integration with Priority Roofing
4. **Iterative testing** - Test each phase before moving on
5. **Scale gradually** - 1 client → 2 clients → all 23 clients

---

**Ready to build!** 🚀

This scaffold provides everything needed to implement a production-grade sync system. Follow the phases, test thoroughly, and deploy with confidence.

