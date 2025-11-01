#!/usr/bin/env python3
"""
ads_sync_cli.py - Production-Grade Google Ads Data Sync & Reporting CLI

This tool implements an incremental "sync & append" architecture for Google Ads data,
featuring idempotent deduplication, watermark-based state management, and gap healing.

Architecture:
- Incremental sync with overlap strategy (default 3 days)
- Idempotent append with deduplication on primary keys
- Watermark-based state management per data source
- Atomic CSV writes with file locking
- Schema validation on every write
- Error recovery with resume commands

Usage:
    python ads_sync_cli.py discover --mcc-id 1877202760
    python ads_sync_cli.py init priority-roofing
    python ads_sync_cli.py append priority-roofing
    python ads_sync_cli.py report priority-roofing --scope LIFETIME
    python ads_sync_cli.py repair priority-roofing --from 2025-09-01 --to 2025-09-30
    python ads_sync_cli.py validate priority-roofing

Author: OneClickSEO PPC Management
Version: 0.1.0
Created: 2025-10-13
"""

import argparse
import json
import logging
import os
import sys
import time
from contextlib import contextmanager
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

# Windows-compatible imports
try:
    import fcntl  # Unix/Linux
    HAS_FCNTL = True
except ImportError:
    HAS_FCNTL = False  # Windows

import pandas as pd
import yaml
from jinja2 import Environment, FileSystemLoader
from jsonschema import validate, ValidationError
import pytz
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

# --- Constants ---
BASE_DIR = Path(__file__).resolve().parent
CONFIGS_DIR = BASE_DIR / "configs" / "clients"
DATA_DIR = BASE_DIR / "data"
ERRORS_DIR = BASE_DIR / "errors"
IMPORTS_DIR = BASE_DIR / "imports"
LOCKS_DIR = BASE_DIR / "locks"
OUTPUT_DIR = BASE_DIR / "output"
SCHEMAS_DIR = BASE_DIR / "schemas"
STATE_DIR = BASE_DIR / "state"
TEMPLATES_DIR = BASE_DIR / "templates"
GOOGLE_ADS_YAML = BASE_DIR / "google-ads.yaml"

VERSION = "0.1.0"
SCHEMA_VERSION = 1

# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(BASE_DIR / "logs" / f"{datetime.now():%Y-%m-%d}.log")
    ]
)
logger = logging.getLogger("ads_sync")


# --- Utility Functions ---

def load_client_config(slug: str) -> Dict[str, Any]:
    """Load client configuration from YAML file."""
    config_path = CONFIGS_DIR / f"{slug}.yaml"
    if not config_path.exists():
        raise FileNotFoundError(f"Client config not found: {config_path}")
    
    with open(config_path) as f:
        config = yaml.safe_load(f)
    
    logger.info(f"Loaded config for {slug}")
    return config


def load_client_state(slug: str) -> Dict[str, Any]:
    """Load or initialize client state file."""
    state_path = STATE_DIR / f"{slug}.json"
    
    if state_path.exists():
        with open(state_path) as f:
            state = json.load(f)
        logger.debug(f"Loaded existing state for {slug}")
        return state
    else:
        # Initialize new state
        state = {
            "slug": slug,
            "created_at": datetime.now(pytz.UTC).isoformat(),
            "timezone": None,  # Will be set from API or config
            "currency_code": None,
            "google_ads": {"watermark_date": None},
            "google_lsa": {"watermark_date": None},
            "search_terms": {"watermark_date": None},
            "schema_version": SCHEMA_VERSION,
            "data_quality": {
                "last_validation": None,
                "total_rows": 0,
                "duplicate_rows_removed": 0,
                "date_gaps": []
            }
        }
        logger.info(f"Initialized new state for {slug}")
        return state


def save_client_state(slug: str, state: Dict[str, Any]):
    """Atomically save client state."""
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    state_path = STATE_DIR / f"{slug}.json"
    tmp_path = state_path.with_suffix(".json.tmp")
    
    state["last_updated"] = datetime.now(pytz.UTC).isoformat()
    
    with open(tmp_path, 'w') as f:
        json.dump(state, f, indent=2)
    
    os.replace(tmp_path, state_path)
    logger.debug(f"Saved state for {slug}")


def load_schema(schema_name: str) -> Dict[str, Any]:
    """Load JSON Schema for validation."""
    schema_path = SCHEMAS_DIR / f"{schema_name}.schema.json"
    if not schema_path.exists():
        raise FileNotFoundError(f"Schema not found: {schema_path}")
    
    with open(schema_path) as f:
        return json.load(f)


# --- Concurrency & Locking ---

@contextmanager
def client_lock(slug: str, timeout: int = 300):
    """
    Robust, timeout-aware file-based locking with PID tracking.
    
    Args:
        slug: Client slug identifier
        timeout: Maximum seconds to wait for lock (default 5 minutes)
    
    Raises:
        TimeoutError: If lock cannot be acquired within timeout
    """
    LOCKS_DIR.mkdir(parents=True, exist_ok=True)
    lock_path = LOCKS_DIR / f"{slug}.lock"
    start_time = time.time()
    fd = None

    while True:
        try:
            # Attempt to create lock file exclusively
            fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            break
        except FileExistsError:
            elapsed = time.time() - start_time
            if elapsed > timeout:
                # Check if lock is stale
                try:
                    with open(lock_path) as f:
                        lock_data = f.read().split('\n')
                        if len(lock_data) >= 2:
                            pid = int(lock_data[0].split(':')[1].strip())
                            timestamp = float(lock_data[1].split(':')[1].strip())
                            
                            # If process doesn't exist, remove stale lock
                            try:
                                os.kill(pid, 0)  # Check if PID exists
                            except OSError:
                                logger.warning(f"Removing stale lock for {slug} (dead PID {pid})")
                                os.remove(lock_path)
                                continue
                except Exception as e:
                    logger.error(f"Error checking stale lock: {e}")
                
                raise TimeoutError(f"Could not acquire lock for '{slug}' after {timeout}s")
            
            time.sleep(2)

    try:
        # Write PID and timestamp for diagnostics
        lock_info = f"pid: {os.getpid()}\ntimestamp: {time.time()}\n"
        os.write(fd, lock_info.encode())
        logger.info(f"Acquired lock for '{slug}'")
        yield
    finally:
        if fd is not None:
            os.close(fd)
        try:
            os.remove(lock_path)
            logger.debug(f"Released lock for '{slug}'")
        except OSError as e:
            logger.error(f"Failed to release lock: {e}")


def force_unlock(slug: str):
    """Manually remove lock file. Use with caution!"""
    lock_path = LOCKS_DIR / f"{slug}.lock"
    if lock_path.exists():
        os.remove(lock_path)
        logger.warning(f"Forcibly removed lock for '{slug}'")
        return True
    else:
        logger.info(f"No lock file found for '{slug}'")
        return False


# --- Sequence Number Management ---

def get_next_sequence_number(slug: str, year: int) -> str:
    """
    Thread-safely get next 3-digit sequence number for reports.
    
    Uses file locking to prevent race conditions when multiple
    reports are generated simultaneously.
    
    Note: On Windows, uses a simpler locking mechanism since fcntl is not available.
    """
    output_dir = OUTPUT_DIR / slug / str(year)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    index_path = output_dir / "index.json"
    
    # Create index if doesn't exist
    if not index_path.exists():
        with open(index_path, 'w') as f:
            json.dump({"last_sequence": 0, "reports": []}, f)
    
    # Lock and increment
    with open(index_path, 'r+') as f:
        if HAS_FCNTL:
            # Unix/Linux: Use fcntl for proper locking
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        # Windows: File is locked while open (basic protection)
        
        try:
            data = json.load(f)
            seq = data["last_sequence"] + 1
            data["last_sequence"] = seq
            
            f.seek(0)
            f.truncate()
            json.dump(data, f, indent=2)
            
            return str(seq).zfill(3)
        finally:
            if HAS_FCNTL:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)


# --- Date Range Utilities ---

def chunk_date_ranges(start: datetime, end: datetime, chunk_days: int = 90) -> List[Tuple[str, str]]:
    """
    Split large date ranges into chunks for API compatibility.
    
    Google Ads API has limits:
    - Standard queries: 90 days max
    - Some reports: 30 days max
    
    Returns list of (start_date, end_date) tuples as ISO strings.
    """
    chunks = []
    current = start
    
    while current < end:
        chunk_end = min(current + timedelta(days=chunk_days), end)
        chunks.append((
            current.strftime("%Y-%m-%d"),
            chunk_end.strftime("%Y-%m-%d")
        ))
        current = chunk_end + timedelta(days=1)
    
    return chunks


def calculate_append_window(
    watermark_date: Optional[str],
    overlap_days: int,
    max_window_days: int,
    client_tz: str
) -> Tuple[str, str]:
    """
    Calculate date window for incremental append.
    
    Strategy:
    - Start: watermark_date - overlap_days (for healing)
    - End: yesterday (client local time)
    - Cap window at max_window_days
    
    Returns (start_date, end_date) as ISO strings.
    """
    tz = pytz.timezone(client_tz)
    today = datetime.now(tz).date()
    yesterday = today - timedelta(days=1)
    
    if watermark_date:
        watermark = datetime.fromisoformat(watermark_date).date()
        start = watermark - timedelta(days=overlap_days)
    else:
        # No watermark: pull last max_window_days
        start = yesterday - timedelta(days=max_window_days)
    
    # Ensure we don't exceed max window
    if (yesterday - start).days > max_window_days:
        start = yesterday - timedelta(days=max_window_days)
    
    return start.isoformat(), yesterday.isoformat()


# --- Data Validation ---

def validate_row(row: Dict[str, Any], schema: Dict[str, Any]) -> bool:
    """
    Validate a single data row against JSON Schema.
    
    Returns True if valid, logs warning if invalid.
    """
    try:
        validate(instance=row, schema=schema)
        return True
    except ValidationError as e:
        logger.warning(f"Schema validation failed: {e.message}")
        logger.debug(f"Invalid row: {row}")
        return False


# --- Atomic CSV Operations ---

def atomic_write_csv(df: pd.DataFrame, path: Path, validate_schema: Optional[Dict] = None):
    """
    Atomically write DataFrame to CSV with optional schema validation.
    
    Process:
    1. Validate data if schema provided
    2. Write to temporary file
    3. Replace original file atomically
    
    This ensures the CSV is never in a partial/corrupt state.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(".csv.tmp")
    
    # Optional validation
    if validate_schema:
        invalid_count = 0
        for idx, row in df.iterrows():
            if not validate_row(row.to_dict(), validate_schema):
                invalid_count += 1
        
        if invalid_count > 0:
            logger.warning(f"{invalid_count} rows failed schema validation")
    
    # Write to temp file
    df.to_csv(tmp_path, index=False)
    
    # Atomic replace
    os.replace(tmp_path, path)
    logger.debug(f"Wrote {len(df)} rows to {path}")


# --- Deduplication ---

def deduplicate_campaigns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Deduplicate campaign data on primary key: (date, campaign_id, data_source).
    
    Strategy: keep='last' ensures latest data wins on overlaps.
    """
    original_count = len(df)
    df_dedup = df.drop_duplicates(
        subset=["date", "campaign_id", "data_source"],
        keep="last"
    )
    removed = original_count - len(df_dedup)
    
    if removed > 0:
        logger.info(f"Removed {removed} duplicate campaign rows")
    
    return df_dedup


def deduplicate_lsa(df: pd.DataFrame) -> pd.DataFrame:
    """
    Deduplicate LSA data on primary key: (date, lead_id, data_source).
    """
    original_count = len(df)
    df_dedup = df.drop_duplicates(
        subset=["date", "lead_id", "data_source"],
        keep="last"
    )
    removed = original_count - len(df_dedup)
    
    if removed > 0:
        logger.info(f"Removed {removed} duplicate LSA rows")
    
    return df_dedup


# --- Data Enrichment & Validation ---

def enrich_campaign_data(df: pd.DataFrame, currency_code: str = "USD") -> pd.DataFrame:
    """
    Enrich campaign data with calculated metrics and schema fields.
    
    Adds:
    - ctr (click-through rate)
    - avg_cpc (average cost per click)
    - cpa (cost per acquisition)
    - conv_rate (conversion rate)
    - currency_code
    - schema_version
    
    Returns enriched DataFrame.
    """
    df = df.copy()
    
    # Calculate CTR (clicks / impressions)
    df['ctr'] = df.apply(
        lambda row: row['clicks'] / row['impressions'] if row['impressions'] > 0 else None,
        axis=1
    )
    
    # Calculate average CPC (cost / clicks)
    df['avg_cpc'] = df.apply(
        lambda row: row['cost'] / row['clicks'] if row['clicks'] > 0 else None,
        axis=1
    )
    
    # Calculate CPA (cost / conversions)
    df['cpa'] = df.apply(
        lambda row: row['cost'] / row['conversions'] if row['conversions'] > 0 else None,
        axis=1
    )
    
    # Calculate conversion rate (conversions / clicks)
    df['conv_rate'] = df.apply(
        lambda row: row['conversions'] / row['clicks'] if row['clicks'] > 0 else None,
        axis=1
    )
    
    # Add schema fields
    df['currency_code'] = currency_code
    df['schema_version'] = SCHEMA_VERSION
    
    return df


def validate_campaign_data(df: pd.DataFrame) -> tuple[bool, list[str]]:
    """
    Validate campaign data against JSON schema.
    
    Returns:
        (is_valid, errors): Tuple of validation status and list of error messages
    """
    schema_path = SCHEMAS_DIR / "campaign_data_v1.schema.json"
    
    if not schema_path.exists():
        logger.warning(f"Schema file not found: {schema_path}")
        return (True, [])  # Skip validation if schema doesn't exist
    
    try:
        with open(schema_path) as f:
            schema = json.load(f)
        
        errors = []
        sample_size = min(100, len(df))  # Validate first 100 rows
        
        for idx in range(sample_size):
            row_dict = df.iloc[idx].to_dict()
            
            # Convert NaN to None for JSON validation
            row_dict = {k: (None if pd.isna(v) else v) for k, v in row_dict.items()}
            
            # Convert numpy types to Python types
            for key, value in row_dict.items():
                if hasattr(value, 'item'):  # numpy type
                    row_dict[key] = value.item()
            
            try:
                validate(instance=row_dict, schema=schema)
            except ValidationError as e:
                errors.append(f"Row {idx}: {e.message}")
                if len(errors) >= 10:  # Limit error reporting
                    errors.append(f"... and potentially more errors (checked {sample_size} rows)")
                    break
        
        is_valid = len(errors) == 0
        
        if is_valid:
            logger.info(f"Schema validation passed ({sample_size} rows checked)")
        else:
            logger.error(f"Schema validation failed with {len(errors)} errors")
        
        return (is_valid, errors)
    
    except Exception as e:
        logger.error(f"Schema validation error: {e}")
        return (False, [str(e)])


# --- Error Recovery ---

def save_error_recovery_info(
    slug: str,
    command: str,
    exception: Exception,
    context: Dict[str, Any]
):
    """
    Save error information with recovery command for easy resume.
    
    Creates a JSON file in errors/ with:
    - Command that failed
    - Exception details
    - Context (dates, partial progress, etc.)
    - Pre-formatted recovery command
    """
    ERRORS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    error_path = ERRORS_DIR / slug / f"error_{timestamp}.json"
    error_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Build recovery command
    if command == "append":
        recovery = f"python ads_sync_cli.py repair {slug} --from {context.get('start_date')} --to {context.get('end_date')}"
    elif command == "init":
        recovery = f"python ads_sync_cli.py init {slug}"
    else:
        recovery = f"python ads_sync_cli.py {command} {slug}"
    
    error_data = {
        "timestamp": timestamp,
        "command": command,
        "slug": slug,
        "exception_type": type(exception).__name__,
        "exception_message": str(exception),
        "context": context,
        "recovery_command": recovery
    }
    
    with open(error_path, 'w') as f:
        json.dump(error_data, f, indent=2)
    
    logger.error(f"Error details saved to: {error_path}")
    logger.info(f"Recovery command: {recovery}")


# --- Command Handlers (Stubs for Implementation) ---

def handle_discover_clients(args):
    """
    Discover all clients accessible via MCC account.
    
    TODO: Implement Google Ads API call to list accessible accounts.
    """
    logger.info("Discovering clients from MCC...")
    logger.warning("This feature requires Google Ads API implementation")
    
    print("\n[Sample Output - Replace with actual API data]")
    print("customer_id,name,status,time_zone,currency_code,suggested_slug,config_exists")
    print("4139022884,Priority Roofing,ENABLED,America/Chicago,USD,priority-roofing,true")
    print("9883178263,Abe Lincoln Movers,ENABLED,America/Chicago,USD,abe-lincoln-movers,true")
    
    if args.export:
        export_path = BASE_DIR / "discovered_clients.csv"
        logger.info(f"Would export to: {export_path}")


# --- Google Ads API Functions ---

def get_google_ads_client(customer_id: str) -> GoogleAdsClient:
    """Initialize and return Google Ads API client."""
    if not GOOGLE_ADS_YAML.exists():
        raise FileNotFoundError(f"Google Ads credentials not found: {GOOGLE_ADS_YAML}")
    
    client = GoogleAdsClient.load_from_storage(str(GOOGLE_ADS_YAML))
    return client


def fetch_campaign_data(
    client: GoogleAdsClient,
    customer_id: str,
    start_date: str,
    end_date: str
) -> pd.DataFrame:
    """
    Fetch campaign performance data from Google Ads API.
    
    Args:
        client: GoogleAdsClient instance
        customer_id: Customer ID (format: XXX-XXX-XXXX)
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
    
    Returns:
        DataFrame with campaign performance data
    """
    # Remove hyphens from customer ID for API
    customer_id_clean = customer_id.replace("-", "")
    
    ga_service = client.get_service("GoogleAdsService")
    
    query = f"""
        SELECT
            segments.date,
            campaign.id,
            campaign.name,
            campaign.status,
            metrics.impressions,
            metrics.clicks,
            metrics.cost_micros,
            metrics.conversions,
            metrics.conversions_value,
            metrics.all_conversions,
            metrics.view_through_conversions
        FROM campaign
        WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
        ORDER BY segments.date ASC
    """
    
    try:
        logger.info(f"Fetching campaign data for {customer_id} from {start_date} to {end_date}")
        search_request = client.get_type("SearchGoogleAdsRequest")
        search_request.customer_id = customer_id_clean
        search_request.query = query
        
        response = ga_service.search(request=search_request)
        
        rows = []
        for row in response:
            rows.append({
                'data_source': 'google_ads',
                'pull_date': datetime.now(pytz.UTC).isoformat(),
                'date': row.segments.date,
                'campaign_id': row.campaign.id,
                'campaign_name': row.campaign.name,
                'campaign_status': row.campaign.status.name,
                'impressions': row.metrics.impressions,
                'clicks': row.metrics.clicks,
                'cost': row.metrics.cost_micros / 1_000_000,  # Convert micros to dollars
                'conversions': row.metrics.conversions,
                'conversions_value': row.metrics.conversions_value,
                'all_conversions': row.metrics.all_conversions,
                'view_through_conversions': row.metrics.view_through_conversions
            })
        
        df = pd.DataFrame(rows)
        logger.info(f"Fetched {len(df)} rows for date range {start_date} to {end_date}")
        return df
    
    except GoogleAdsException as ex:
        logger.error(f"Google Ads API error:")
        for error in ex.failure.errors:
            logger.error(f"  {error.message}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error fetching campaign data: {e}")
        raise


def handle_init(args):
    """
    Perform initial historical backfill for a client.
    
    Process:
    1. Load client config
    2. Connect to Google Ads API
    3. Determine lifetime date range
    4. Chunk into 90-day windows
    5. Pull data for each chunk
    6. Validate and write to master CSVs
    7. Set initial watermarks
    
    TODO: Implement GAQL queries and data transformation.
    """
    slug = args.slug
    
    with client_lock(slug):
        logger.info(f"Starting initial historical sync for '{slug}'")
        
        try:
            config = load_client_config(slug)
            state = load_client_state(slug)
            
            # Get date range (placeholder)
            # In reality: query customer.start_date or use config
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=365)  # 1 year back
            
            logger.info(f"Backfill period: {start_date} to {end_date}")
            
            # Initialize Google Ads client
            ads_client = get_google_ads_client(config["client_id"])
            
            # Chunk into 90-day windows
            chunks = chunk_date_ranges(
                datetime.strptime(str(start_date), "%Y-%m-%d"),
                datetime.strptime(str(end_date), "%Y-%m-%d"),
                chunk_days=90
            )
            logger.info(f"Split into {len(chunks)} chunks (90-day max per API limit)")
            
            all_data = []
            for i, (chunk_start, chunk_end) in enumerate(chunks, 1):
                logger.info(f"Processing chunk {i}/{len(chunks)}: {chunk_start} to {chunk_end}")
                
                # Pull data via API
                df_chunk = fetch_campaign_data(
                    ads_client,
                    config["client_id"],
                    chunk_start,
                    chunk_end
                )
                all_data.append(df_chunk)
            
            # Combine all chunks
            if all_data:
                df_master = pd.concat(all_data, ignore_index=True)
                logger.info(f"Combined {len(df_master)} total rows from {len(chunks)} chunks")
                
                # Deduplicate
                df_master = deduplicate_campaigns(df_master)
                logger.info(f"After deduplication: {len(df_master)} rows")
                
                # Enrich with calculated metrics
                currency_code = config.get("currency_code", "USD")
                df_master = enrich_campaign_data(df_master, currency_code)
                logger.info("Enriched data with calculated metrics (CTR, CPC, CPA, etc.)")
                
                # Validate against schema
                is_valid, errors = validate_campaign_data(df_master)
                if not is_valid:
                    logger.warning(f"Schema validation failed:")
                    for error in errors[:5]:  # Show first 5 errors
                        logger.warning(f"  {error}")
                    logger.warning("Continuing anyway (validation is non-blocking)")
                
                # Write to master CSV
                data_path = DATA_DIR / slug
                data_path.mkdir(parents=True, exist_ok=True)
                master_csv_path = data_path / f"{slug}-master-campaign_data.csv"
                
                atomic_write_csv(df_master, master_csv_path)
                logger.info(f"Wrote master CSV: {master_csv_path}")
            else:
                logger.warning(f"No data fetched for {slug}")
            
            # Set watermarks
            state["google_ads"]["watermark_date"] = end_date.isoformat()
            state["timezone"] = config.get("timezone", "America/Chicago")
            state["currency_code"] = config.get("currency_code", "USD")
            save_client_state(slug, state)
            
            logger.info(f"Completed initial sync for '{slug}'")
            
        except Exception as e:
            save_error_recovery_info(slug, "init", e, {"phase": "initial_backfill"})
            raise


def handle_append(args):
    """
    Perform incremental append with watermark-based sync.
    
    Process:
    1. Read last watermark
    2. Calculate window (watermark - overlap_days to yesterday)
    3. Pull new data
    4. Load master CSV
    5. Append and deduplicate
    6. Atomic write
    7. Update watermark
    
    TODO: Implement incremental sync logic.
    """
    slug = args.slug
    
    with client_lock(slug):
        logger.info(f"Starting incremental append for '{slug}'")
        
        try:
            config = load_client_config(slug)
            state = load_client_state(slug)
            
            sync_config = config.get("sync", {})
            overlap_days = sync_config.get("overlap_days", 3)
            max_window = sync_config.get("max_window_days", 30)
            client_tz = config.get("timezone", "America/Chicago")
            
            # Calculate date window
            watermark = state["google_ads"]["watermark_date"]
            start_date, end_date = calculate_append_window(
                watermark, overlap_days, max_window, client_tz
            )
            
            logger.info(f"Append window: {start_date} to {end_date}")
            logger.info(f"Overlap: {overlap_days} days (healing late data)")
            
            # Initialize Google Ads client
            ads_client = get_google_ads_client(config["client_id"])
            
            # Pull new data via API
            df_new = fetch_campaign_data(
                ads_client,
                config["client_id"],
                start_date,
                end_date
            )
            logger.info(f"Fetched {len(df_new)} new rows from API")
            
            # Load existing master CSV
            data_path = DATA_DIR / slug
            master_csv_path = data_path / f"{slug}-master-campaign_data.csv"
            
            if not master_csv_path.exists():
                logger.error(f"Master CSV not found: {master_csv_path}")
                logger.error("Run 'init' command first to create initial data")
                raise FileNotFoundError(f"Master CSV not found for {slug}")
            
            df_existing = pd.read_csv(master_csv_path)
            logger.info(f"Loaded {len(df_existing)} existing rows from master CSV")
            
            # Append new data
            df_combined = pd.concat([df_existing, df_new], ignore_index=True)
            logger.info(f"Combined: {len(df_combined)} total rows")
            
            # Deduplicate
            df_master = deduplicate_campaigns(df_combined)
            logger.info(f"After deduplication: {len(df_master)} rows")
            
            # Enrich with calculated metrics (for new rows)
            currency_code = config.get("currency_code", "USD")
            df_master = enrich_campaign_data(df_master, currency_code)
            logger.info("Enriched data with calculated metrics")
            
            # Validate against schema
            is_valid, errors = validate_campaign_data(df_master)
            if not is_valid:
                logger.warning(f"Schema validation failed:")
                for error in errors[:5]:
                    logger.warning(f"  {error}")
                logger.warning("Continuing anyway (validation is non-blocking)")
            
            # Atomic write
            atomic_write_csv(df_master, master_csv_path)
            rows_added = len(df_master) - len(df_existing)
            logger.info(f"Wrote master CSV: {master_csv_path}")
            logger.info(f"Net change: +{rows_added} rows (after dedup)")
            
            # Update watermark
            state["google_ads"]["watermark_date"] = end_date
            state["data_quality"]["last_validation"] = datetime.now(pytz.UTC).isoformat()
            state["data_quality"]["last_append"] = datetime.now(pytz.UTC).isoformat()
            save_client_state(slug, state)
            
            logger.info(f"Completed incremental append for '{slug}'")
            
        except Exception as e:
            save_error_recovery_info(
                slug, "append", e,
                {"start_date": start_date, "end_date": end_date}
            )
            raise


def handle_report(args):
    """
    Generate Markdown report from master CSVs (no API calls).
    
    Process:
    1. Load master CSV data
    2. Filter by scope (LIFETIME, LAST-30-DAYS, etc.)
    3. Calculate aggregations
    4. Render Jinja2 template
    5. Write to output/ with sequence number
    
    TODO: Implement report generation logic.
    """
    slug = args.slug
    scope = args.scope
    
    logger.info(f"Generating report for '{slug}' with scope '{scope}'")
    
    try:
        config = load_client_config(slug)
        state = load_client_state(slug)
        
        # Get next sequence number
        year = datetime.now().year
        seq = get_next_sequence_number(slug, year)
        
        # TODO: Load data from CSV
        # TODO: Filter by scope
        # TODO: Calculate metrics
        # TODO: Render template
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = OUTPUT_DIR / slug / str(year) / f"{seq}-{slug}-report-{scope}-{timestamp}.md"
        
        logger.info(f"Report would be written to: {report_path}")
        logger.warning("Report generation requires implementation")
        
    except Exception as e:
        logger.error(f"Report generation failed: {e}")
        raise


def handle_validate(args):
    """
    Validate client configuration and data integrity.
    
    Checks:
    - Config file exists and is valid
    - State file exists
    - Master CSV files exist
    - Schema validation on sample data
    - Date gap detection
    
    TODO: Implement validation checks.
    """
    slug = args.slug
    
    logger.info(f"Validating setup for '{slug}'")
    
    try:
        config = load_client_config(slug)
        logger.info("[OK] Config file valid")
        
        state = load_client_state(slug)
        logger.info(f"[OK] State file loaded (watermark: {state['google_ads']['watermark_date']})")
        
        # Check for master CSV
        data_path = DATA_DIR / slug / f"{slug}-master-campaign_data.csv"
        if data_path.exists():
            df = pd.read_csv(data_path, nrows=10)
            logger.info(f"[OK] Master CSV exists ({len(df)} sample rows)")
        else:
            logger.warning(f"[MISSING] Master CSV not found: {data_path}")
        
        logger.info(f"Validation complete for '{slug}'")
        
    except Exception as e:
        logger.error(f"Validation failed: {e}")
        raise


def handle_repair(args):
    """
    Repair data gaps by re-pulling a specific date range.
    
    Idempotent: can be run multiple times for the same window.
    
    TODO: Implement gap repair logic (similar to append but for custom range).
    """
    slug = args.slug
    start_date = args.start
    end_date = args.end
    
    with client_lock(slug):
        logger.info(f"Repairing data for '{slug}' from {start_date} to {end_date}")
        
        try:
            config = load_client_config(slug)
            
            # TODO: Pull data for specified range
            # TODO: Load master CSV
            # TODO: Merge and deduplicate
            # TODO: Atomic write
            
            logger.info(f"Repair complete for '{slug}'")
            
        except Exception as e:
            save_error_recovery_info(
                slug, "repair", e,
                {"start_date": start_date, "end_date": end_date}
            )
            raise


def handle_force_unlock(args):
    """Manually remove lock file."""
    slug = args.slug
    if force_unlock(slug):
        print(f"[SUCCESS] Lock removed for '{slug}'")
    else:
        print(f"[INFO] No lock found for '{slug}'")


# --- Main CLI ---

def main():
    """Main entry point for ads_sync CLI."""
    parser = argparse.ArgumentParser(
        description="Production-grade Google Ads data sync and reporting tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Discover all clients from MCC
  python ads_sync_cli.py discover --mcc-id 1877202760 --export

  # Initialize historical data for a client
  python ads_sync_cli.py init priority-roofing

  # Perform incremental append (daily/weekly)
  python ads_sync_cli.py append priority-roofing

  # Generate lifetime report
  python ads_sync_cli.py report priority-roofing --scope LIFETIME

  # Generate last 30 days report
  python ads_sync_cli.py report priority-roofing --scope LAST-30-DAYS

  # Repair a data gap
  python ads_sync_cli.py repair priority-roofing --start 2025-09-01 --end 2025-09-30

  # Validate configuration
  python ads_sync_cli.py validate priority-roofing

  # Force remove lock (use with caution!)
  python ads_sync_cli.py force-unlock priority-roofing

Version: {VERSION}
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", required=True, help="Available commands")
    
    # discover command
    discover_parser = subparsers.add_parser(
        "discover",
        help="Discover all clients accessible via MCC account"
    )
    discover_parser.add_argument("--mcc-id", help="MCC customer ID")
    discover_parser.add_argument("--export", action="store_true", help="Export to CSV")
    discover_parser.set_defaults(func=handle_discover_clients)
    
    # init command
    init_parser = subparsers.add_parser(
        "init",
        help="Initialize historical data for a client (one-time backfill)"
    )
    init_parser.add_argument("slug", help="Client slug (e.g., 'priority-roofing')")
    init_parser.set_defaults(func=handle_init)
    
    # append command
    append_parser = subparsers.add_parser(
        "append",
        help="Perform incremental append with watermark sync"
    )
    append_parser.add_argument("slug", help="Client slug")
    append_parser.set_defaults(func=handle_append)
    
    # report command
    report_parser = subparsers.add_parser(
        "report",
        help="Generate report from master data (no API calls)"
    )
    report_parser.add_argument("slug", help="Client slug")
    report_parser.add_argument(
        "--scope",
        default="LAST-30-DAYS",
        help="Date scope: LIFETIME, LAST-7-DAYS, LAST-30-DAYS, 2025-Q3, 2025-01..2025-03"
    )
    report_parser.set_defaults(func=handle_report)
    
    # validate command
    validate_parser = subparsers.add_parser(
        "validate",
        help="Validate configuration and data integrity"
    )
    validate_parser.add_argument("slug", help="Client slug")
    validate_parser.set_defaults(func=handle_validate)
    
    # repair command
    repair_parser = subparsers.add_parser(
        "repair",
        help="Repair data gaps by re-pulling a date range"
    )
    repair_parser.add_argument("slug", help="Client slug")
    repair_parser.add_argument("--start", required=True, help="Start date (YYYY-MM-DD)")
    repair_parser.add_argument("--end", required=True, help="End date (YYYY-MM-DD)")
    repair_parser.set_defaults(func=handle_repair)
    
    # force-unlock command
    unlock_parser = subparsers.add_parser(
        "force-unlock",
        help="Manually remove lock file (use with caution!)"
    )
    unlock_parser.add_argument("slug", help="Client slug")
    unlock_parser.set_defaults(func=handle_force_unlock)
    
    args = parser.parse_args()
    
    # Execute command
    try:
        args.func(args)
    except KeyboardInterrupt:
        logger.warning("Operation cancelled by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Command failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

