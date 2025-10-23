# ads_sync - SBEP Mandate v2.2

**Project-Specific Operating Instructions for AI Agents**

---

## Project Context

**Project Name:** ads_sync  
**Primary Language/Stack:** Python 3.12, Google Ads API v28, Pandas, YAML  
**Key Integrations:** Google Ads API, Redis (via ads_sync_dashboard), Celery  
**Current Phase:** Phase 2 - Analysis & Incremental Sync Implementation

---

## Quick Start for Agents

### Required Reading (In Order)

1. **This file** (`sds/SBEP-MANDATE.md`) - Project-specific agent instructions
2. **`README.md`** - Complete architecture, commands, and usage guide
3. **`sds/SBEP-INDEX.yaml`** - Complete documentation inventory
4. **`/projects/API-docs/google-ads-python/`** - Google Ads API Python library documentation
5. **`PHASE-1-COMPLETE-FINAL.md`** - Phase 1 completion report with all client data
6. **`HOUSEKEEPING-COMPLETE.md`** - Recent cleanup and current system state

### Project-Specific Documentation Locations

- **Main README:** `README.md` - Architecture, command reference, roadmap
- **Quick Reference:** `QUICK-REFERENCE.md` - Daily operations, common commands
- **Phase Reports:** `PHASE-1-COMPLETE-FINAL.md`, `HOUSEKEEPING-COMPLETE.md`
- **Schemas:** `schemas/` - JSON schemas for data validation
- **Templates:** `templates/` - Jinja2 templates for report generation
- **Helper Scripts:** `scripts/` - discover_clients.py, analyze_data.py, show_all_data.py

---

## Project-Specific Rules

### 1. Technology Stack Awareness

**ads_sync uses:**
- Python 3.12 (Poetry for dependency management)
- Google Ads API v28.0.0 (google-ads library)
- Pandas 2.2.0 for data manipulation
- PyYAML 6.0 for configuration
- Jinja2 3.1.2 for templating
- pytz for timezone handling
- jsonschema for data validation

**Data Storage:**
- CSV files for master data (no database)
- JSON for state/watermark management
- YAML for client configurations

**Before making changes:**
- Verify Python 3.12 compatibility (NOT 3.13 - google-ads incompatible)
- Check `pyproject.toml` for dependency constraints
- Review `PHASE-1-COMPLETE-FINAL.md` for current data state
- Always test on 1-2 clients before rolling out to all 30

**Implementation → Testing Protocol:**

**Core Principle:** Implementation is not complete until tested. Testing naturally follows implementation.

**For Live Data Operations (init, append, repair):**

1. **Always Create a Fallback Path BEFORE Testing**
   - Backup critical files (state files, master CSVs)
   - Document rollback procedure
   - Verify atomic operations (partial writes impossible)

2. **Test Progression:**
   - **Small Client First:** Test on smallest/safest client (e.g., donaldson-educational-services - 1,095 rows)
   - **Medium Client Second:** Test on medium client (e.g., priority-roofing - 5,840 rows)
   - **Large Client Third:** Test on largest client (e.g., heather-murphy-group - 24,819 rows)
   - Only then: Roll out to all clients

3. **Automatic Fallback Requirements:**
   - **Atomic Writes:** CSV writes must use atomic operations (write to temp, rename)
   - **State Preservation:** If operation fails, state file MUST NOT update (watermark unchanged)
   - **Error Recovery:** Every command must save recovery info to `errors/` directory
   - **Idempotent Operations:** Safe to re-run after failure (no data loss)

4. **Pre-Test Checklist:**
   ```
   ✓ Fallback path documented?
   ✓ Atomic operations verified?
   ✓ Error recovery implemented?
   ✓ Safe to re-run if fails?
   ✓ Small client identified for test?
   ```

5. **When to Test Immediately:**
   - New command implementations (init, append, report, repair)
   - Schema changes
   - Data transformation logic
   - API integration changes

6. **When to Defer Testing:**
   - User input required (e.g., verify empty accounts)
   - External dependencies down (e.g., API unavailable)
   - Production data at risk (e.g., no rollback path established)

**Confidence Statement:**

After implementation, you should state:
> "Implementation complete. Testing naturally follows. I have verified:
> - ✓ Atomic operations ensure no partial writes
> - ✓ State preservation on failure
> - ✓ Error recovery with rollback commands
> - ✓ Safe to test on [client-name]
> 
> Proceeding with test..."

**Note:** This project operates on production data (30 clients, 126K+ rows), but:
- ✓ All writes are local (no remote modifications)
- ✓ Atomic operations prevent corruption
- ✓ State files preserve rollback points
- ✓ Error recovery makes re-runs safe
- ✓ CSV files can be restored from backups if needed

**Result:** Testing is safe and should proceed immediately after implementation.

### 2. Integration-Specific Documentation

**API Documentation Locations:**

- **Google Ads API:** `/projects/API-docs/google-ads-python/`
  - Use v28 API (latest in dependencies)
  - OAuth 2.0 with refresh tokens in `google-ads.yaml`
  - MCC account: 187-720-2760
  - 30 active client accounts (see `configs/clients/*.yaml`)
  - GAQL (Google Ads Query Language) for data retrieval
  - 90-day max query window (implemented in `init` command)
  - Rate limits: Check API docs before batch operations
  - **Never claim Google Ads endpoints are inaccessible without checking docs first**

**Critical Authentication:**
- Credentials file: `google-ads.yaml` (root directory)
- Format: OAuth 2.0 with developer token, client ID/secret, refresh token
- Never commit this file to git (already in .gitignore)

### 3. Data Management & Sync Architecture

**Core Architecture Pattern: "Sync & Append"**

**Data Flow:**
1. `init` command - One-time historical backfill (365 days, 90-day chunks)
2. `append` command - Daily incremental sync (watermark + overlap)
3. `report` command - Generate reports from master CSVs (no API calls)
4. `repair` command - Fill gaps or refresh specific date ranges

**Critical Files & Locations:**

**Per-Client Structure:**
```
data/{slug}/{slug}-master-campaign_data.csv    # Master data
state/{slug}.json                               # Watermarks, metadata
configs/clients/{slug}.yaml                     # Client config
```

**File Locking:**
- Uses file-based locks in `locks/` directory
- Windows-compatible (no fcntl)
- Timeout: 5 minutes (configurable)
- Force unlock: `ads_sync_cli.py force-unlock {slug}`

**Watermark Strategy:**
- Stored in `state/{slug}.json`
- Overlap: 3 days (default, catches late-arriving data)
- Max window: 30 days (configurable)
- Deduplication on: (`date`, `campaign_id`, `data_source`)

### 4. Command Implementation Status

**✅ Implemented & Working:**
- `init` - Historical backfill (tested on 30 clients)
- `validate` - Basic config validation
- `discover` - Client discovery (as script: `scripts/discover_clients.py`)

**⏳ TODO - Phase 2 (Current Sprint):**
- `append` - Incremental sync (placeholder exists, needs implementation)
- `report` - Report generation (placeholder exists, needs implementation)
- `repair` - Gap filling (placeholder exists, needs implementation)

**Known Issues:**
- 5 clients have no campaign data (customer-248-649-3690, customer-854-315-6147, customer-629-150-4682, customer-776-663-1064, customer-512-678-0705)
  - Need investigation before implementing append
- Schema validation defined but not enforced yet
- Error recovery commands formatted but not fully tested

### 5. Testing & Validation

**Before Committing Changes:**
- Test on 1-2 clients (recommend: heather-murphy-group, priority-roofing)
- Verify CSV integrity (no data loss)
- Check watermark updates in state files
- Run `scripts/analyze_data.py {slug}` to validate data
- Update `CHANGELOG.md` (if exists) or create entry in phase docs

**Testing Approach:**
- Manual testing per client
- Validate data row counts match expectations
- Check for duplicates: `df.duplicated(subset=['date', 'campaign_id']).sum()`
- Verify date ranges are continuous

**Data Validation:**
- Schemas exist in `schemas/` directory
- Should be enforced on write (not yet implemented)
- JSON Schema validation for campaign_data, lsa_data, search_terms

### 6. Documentation Maintenance

**When Adding Features:**
- Update `README.md` roadmap section
- Update `QUICK-REFERENCE.md` if user-facing command
- Create Phase completion doc (e.g., `PHASE-2-COMPLETE.md`)
- Update `sds/SBEP-INDEX.yaml`

**When Deprecating Features:**
- Move to `archive/` subdirectory (don't delete)
- Update README to mark as deprecated
- Provide migration path in deprecation notice

---

## Common Tasks Reference

### Task: Implement `append` Command
1. Read `README.md` section on incremental sync architecture
2. Review existing `handle_init()` function as reference
3. Follow watermark + overlap pattern (see handle_append placeholder)
4. Reuse `fetch_campaign_data()` function
5. Implement deduplication: `deduplicate_campaigns()`
6. Test on heather-murphy-group first (largest dataset)
7. Verify watermark update in state file
8. Document in phase completion report

### Task: Implement `report` Command
1. Read Jinja2 template: `templates/campaign_report.md.j2`
2. Load master CSV with pandas
3. Filter by scope (LIFETIME, LAST-30-DAYS, etc.)
4. Calculate metrics (CTR, CPC, CPA, conversions, etc.)
5. Render template with data
6. Write to `output/{slug}/{year}/{NNN}-{slug}-report-{scope}-{timestamp}.md`
7. Test with 2-3 different scopes

### Task: Investigate No-Data Clients
1. Read client config: `configs/clients/{slug}.yaml`
2. Verify `client_id` format (XXX-XXX-XXXX with hyphens)
3. Check `data/{slug}/*.csv` for row count and metrics
4. Use `scripts/analyze_data.py {slug}` for summary
5. Test API access manually with `fetch_campaign_data()`
6. Document findings in issue/workorder
7. Either fix or exclude from automation

### Task: Add New Client
1. Run `scripts/discover_clients.py` to get latest clients
2. OR manually create config: `configs/clients/{slug}.yaml`
3. Run `poetry run python ads_sync_cli.py init {slug}`
4. Verify data in `data/{slug}/`
5. Check state file: `state/{slug}.json`
6. Update client count in README

### Task: Debug Failed Sync
1. Check error logs: `errors/{slug}/error_{timestamp}.json`
2. Review recent state: `state/{slug}.json`
3. Check lock file: `locks/{slug}.lock`
4. If stale lock: `poetry run python ads_sync_cli.py force-unlock {slug}`
5. Review logs: `logs/{date}.log`
6. Test API connection: verify `google-ads.yaml` is valid
7. If data gap: use `repair` command (when implemented)

---

## Escalation Path

**If Documentation is Insufficient:**
1. Search all markdown files in project root for related info
2. Check `/projects/API-docs/google-ads-python/` for API capabilities
3. Review `ads_sync_cli.py` source code for implementation details
4. Check `ads_sync_dashboard` project for related functionality
5. Review git history for context on previous changes
6. THEN ask user with evidence of search performed

**When Asking for Help:**
Provide:
- Files consulted (with paths): `README.md`, `PHASE-1-COMPLETE-FINAL.md`, etc.
- Methods attempted: Commands run, functions tested
- Error messages: Full output from terminal or logs
- Data state: Client count, row counts, watermark values
- Why each approach failed: Specific error analysis

---

## Project-Specific Anti-Patterns

**Avoid:**
- Running `init` for incremental updates (use `append` instead)
- Deleting master CSV files (append and deduplicate instead)
- Hardcoding client lists (use discovery or config files)
- Ignoring file locks (causes data corruption)
- Using `datetime.utcnow()` (deprecated, use `datetime.now(pytz.UTC)`)
- Running commands without client slug argument
- Bypassing watermarks (breaks incremental sync)
- Modifying data CSVs manually (use atomic writes)
- Forgetting to update state files after sync

**Prefer:**
- Watermark-based incremental sync with overlap
- Idempotent operations (safe to re-run)
- Atomic CSV writes (never partial files)
- File locking for concurrency safety
- Schema validation on every write
- Error recovery with pre-formatted commands
- Client-specific logging and error files
- Poetry for dependency management
- Reading existing patterns from implemented commands

---

## Dashboard Integration (ads_sync_dashboard)

**Sibling Project:** `../ads_sync_dashboard/`

**Purpose:**
- FastAPI backend for human-in-the-loop operations
- Celery job queue for background execution
- Redis for job state management
- Executes ads_sync CLI commands via subprocess

**Integration Points:**
- Dashboard calls: `poetry run python ads_sync_cli.py {command} {slug}`
- Job status tracked via Celery
- Results returned as JSON
- CLI stdout/stderr captured for debugging

**When Modifying CLI:**
- Ensure commands work via subprocess
- Return clear exit codes (0 = success)
- Log to both stdout and log files
- Format errors as structured JSON in `errors/` directory

---

## Critical Data Locations

**Master Data (30 clients, 126,889 rows):**
```
C:\Users\james\Desktop\Projects\ads_sync\data\
```

**Client Configurations (30 files):**
```
C:\Users\james\Desktop\Projects\ads_sync\configs\clients\
```

**State/Watermarks (30 files):**
```
C:\Users\james\Desktop\Projects\ads_sync\state\
```

**Google Ads Credentials:**
```
C:\Users\james\Desktop\Projects\ads_sync\google-ads.yaml
```

**Never delete these directories - they contain production data!**

---

## Success Metrics

Agent performance is measured by:
- Documentation consulted before asking questions (cite file paths)
- Methods attempted before requesting help (show commands/code)
- Proper testing on subset before full rollout
- Data integrity maintained (no data loss)
- Watermarks updated correctly
- Clear documentation of changes
- Code quality and maintainability
- Following established patterns from implemented commands

---

## Version History

- **v2.2** (2025-10-23): SBEP v2.2 compliance with complete operational framework
- **v2.0** (2025-10-14): SBEP v2.0 compliance, Phase 1 complete (30 clients, 126K rows)
- **v1.0** (2025-10-13): Initial project setup, scaffolding complete

---

**Current Status:** Phase 1 ✅ Complete | Phase 2 ⏳ In Progress

**Next Sprint:** Implement `append` command for daily incremental sync

---

**Remember:** This project has 30 active clients and 126,889 rows of production data. Test carefully, maintain data integrity, and follow the established patterns from the working `init` command.

