# Parallel Campaign Creation & Activation Plan
## Priority Roofing - "Roofing Services 2025 - ECT/OCS v2"

**Created**: 2025-10-19  
**Client**: Priority Roofing (client_id: 1)  
**Source Campaign**: "Roofing Services 2025 - ECT/OCS"  
**Analysis Data**: `C:\Users\james\Desktop\Projects\Output\priorityroofers.com\`

---

## Overview

Create an optimized Google Ads campaign based on AI analysis findings, validate it programmatically, then activate it while pausing the original campaign (direct budget swap, not parallel spend).

**Key Constraint**: Cannot run both campaigns simultaneously due to budget authorization limits.

---

## Implementation Phases

### Phase 1: Dry-Run Campaign Creation

**Script**: `ads-monkee/scripts/create_optimized_campaign.py`

**Functionality**:
1. Load analysis data from CSV files:
   - `pr-roofing_editor_keywords_to_add.csv` (56 exact match keywords)
   - `pr-roofing_editor_negative_keywords.csv` (124 negative keywords)
2. Query database for original campaign details:
   - Campaign ID, name, budget, bidding strategy, targeting settings
3. Build campaign structure:
   - New campaign name: `{original_name} v2`
   - Same ad groups as original
   - Replace keywords with optimized list
   - Add negative keywords at campaign and ad group levels
   - Copy all other settings (location targeting, schedule, etc.)
4. **DRY-RUN MODE**: Output complete campaign plan to JSON file
   - `ads-monkee/.tmp/campaign-plan-{timestamp}.json`
5. Display summary:
   - Campaign name
   - Daily budget (must match original)
   - Keyword count (old vs new)
   - Negative keyword count (old vs new)
   - Ad groups affected
   - Estimated changes

**Command**:
```bash
poetry run python scripts/create_optimized_campaign.py \
  --client-id 1 \
  --source-campaign "Roofing Services 2025 - ECT/OCS" \
  --analysis-dir "C:\Users\james\Desktop\Projects\Output\priorityroofers.com" \
  --dry-run \
  --output ads-monkee/.tmp/campaign-plan.json
```

**Output**: JSON plan file + console summary for user review

---

### Phase 2: Create Campaign (PAUSED State)

**Script**: Same script, without `--dry-run` flag

**Functionality**:
1. Read approved plan from Phase 1 JSON file
2. Authenticate with Google Ads API
3. Create new campaign via API:
   - **Status**: `PAUSED` (critical - not live yet)
   - Name: "Roofing Services 2025 - ECT/OCS v2"
   - Copy budget from original campaign
   - Copy all targeting and settings
4. Create ad groups (PAUSED)
5. Add optimized keywords (exact match)
6. Add negative keywords (phrase match, at appropriate levels)
7. Copy ads from original campaign (or use existing ad copy)
8. Log all API operations to `ads-monkee/logs/campaign-creation-{timestamp}.log`
9. Store campaign creation record in database:
   - New table: `campaign_modifications` 
   - Fields: `source_campaign_id`, `new_campaign_id`, `status`, `created_at`, `analysis_run_id`

**Command**:
```bash
poetry run python scripts/create_optimized_campaign.py \
  --client-id 1 \
  --source-campaign "Roofing Services 2025 - ECT/OCS" \
  --analysis-dir "C:\Users\james\Desktop\Projects\Output\priorityroofers.com" \
  --plan-file ads-monkee/.tmp/campaign-plan.json
```

**Output**: 
- New campaign ID
- Confirmation that campaign is PAUSED
- Log file path

---

### Phase 3: Automated Validation & Comparison

**Script**: `ads-monkee/scripts/validate_campaign.py`

**Functionality**:
1. **Pull created campaign schema from Google Ads API**:
   - Campaign settings (budget, bidding, targeting)
   - All ad groups
   - All keywords (positive and negative)
   - All ads
2. **Compare against original plan**:
   - Verify campaign name matches: `{original} v2`
   - **CRITICAL CHECK**: Verify daily budget matches original campaign exactly
   - Verify keyword count matches plan
   - Verify negative keyword count matches plan
   - Verify ad group structure matches
   - Check for any API errors or disapprovals
3. **Generate validation report**:
   - Green/Red status for each check
   - List any discrepancies
   - Flag any disapproved ads/keywords
   - Budget comparison: `Original: $X.XX | New: $Y.YY | Match: ✓/✗`
4. **Output**:
   - Console summary (color-coded)
   - JSON report: `ads-monkee/.tmp/validation-report-{campaign_id}.json`
   - Overall status: `PASS` or `FAIL`

**Command**:
```bash
poetry run python scripts/validate_campaign.py \
  --client-id 1 \
  --new-campaign-id {campaign_id_from_phase2} \
  --source-campaign "Roofing Services 2025 - ECT/OCS" \
  --plan-file ads-monkee/.tmp/campaign-plan.json
```

**Success Criteria** (all must be TRUE to proceed):
- ✓ Campaign exists and is PAUSED
- ✓ Daily budget matches original exactly
- ✓ Keyword count matches plan (±5% tolerance for API quirks)
- ✓ Negative keyword count matches plan
- ✓ No critical ad disapprovals
- ✓ All ad groups created successfully

**Output**: 
- `VALIDATION: PASS` or `VALIDATION: FAIL`
- If FAIL: detailed error report, halt process

---

### Phase 4: Activation & Budget Swap

**Script**: `ads-monkee/scripts/activate_campaign_swap.py`

**Functionality**:
1. **Pre-activation checks**:
   - Verify validation report exists and shows PASS
   - Confirm new campaign is PAUSED
   - Confirm original campaign is ENABLED
2. **Execute swap** (atomic operation):
   - Enable new campaign (v2)
   - Pause original campaign
   - Log both operations with timestamps
3. **Verify swap**:
   - Query both campaigns from API
   - Confirm new campaign status = ENABLED
   - Confirm old campaign status = PAUSED
4. **Record in database**:
   - Update `campaign_modifications` table: `status = 'active'`, `activated_at = NOW()`
   - Create audit log entry
5. **Send notification to GoHighLevel**:
   - Create note on Priority Roofing contact
   - Message: "Campaign optimization activated: 'Roofing Services 2025 - ECT/OCS v2' is now live. Original campaign paused. Monitoring for 7 days."
   - Tag: `ads-optimization-active`

**Command**:
```bash
poetry run python scripts/activate_campaign_swap.py \
  --client-id 1 \
  --new-campaign-id {campaign_id} \
  --source-campaign "Roofing Services 2025 - ECT/OCS" \
  --validation-report ads-monkee/.tmp/validation-report-{campaign_id}.json
```

**Safety Features**:
- Requires explicit `--confirm` flag to execute
- Dry-run mode available: `--dry-run` shows what would happen
- Rollback script ready: `rollback_campaign_swap.py`

**Output**:
- Activation timestamp
- Both campaign statuses confirmed
- GHL note ID
- Next steps (monitoring instructions)

---

### Phase 5: Monitoring & Reporting

**Script**: `ads-monkee/scripts/monitor_campaign_performance.py`

**Functionality**:
1. **Daily sync** (via Celery task):
   - Pull performance data for both campaigns (old and v2)
   - Store in `google_ads_campaigns` table
2. **Comparison dashboard** (API endpoint):
   - `GET /api/campaigns/compare?old={id}&new={id}&days=7`
   - Returns side-by-side metrics:
     - Impressions, Clicks, CTR
     - Cost, CPC
     - Conversions, CPA
     - ROAS
     - Quality Score trends
3. **Automated alerts** (Celery task, runs daily):
   - If v2 CPA > old CPA by 50% after 3 days → alert
   - If v2 conversions = 0 after 2 days → alert
   - If v2 spend = 0 (campaign paused by Google) → immediate alert
4. **Weekly GHL update**:
   - Day 7: Send summary note to GHL
   - Include performance comparison
   - Recommendation: Keep v2, archive old, or rollback

**Monitoring Period**: 7-14 days

**Decision Criteria** (after 7 days):
- **Keep v2 if**: CPA ≤ old CPA OR ROAS ≥ old ROAS
- **Rollback if**: CPA > old CPA by 30%+ AND conversions < 50% of old
- **Extend monitoring if**: Inconclusive (learning phase)

---

### Phase 6: Rollback Procedure (Emergency Use)

**Script**: `ads-monkee/scripts/rollback_campaign_swap.py`

**Functionality**:
1. Pause new campaign (v2)
2. Re-enable original campaign
3. Log rollback reason
4. Send GHL notification
5. Archive v2 campaign (don't delete)

**Command**:
```bash
poetry run python scripts/rollback_campaign_swap.py \
  --client-id 1 \
  --new-campaign-id {campaign_id} \
  --reason "High CPA, insufficient conversions" \
  --confirm
```

**When to use**:
- New campaign severely underperforming (CPA 2x+ higher)
- Critical ad disapprovals blocking delivery
- Client requests immediate revert
- Budget spent too quickly (pacing issues)

---

## File Structure

```
ads-monkee/
├── scripts/
│   ├── create_optimized_campaign.py    # Phase 1 & 2
│   ├── validate_campaign.py            # Phase 3
│   ├── activate_campaign_swap.py       # Phase 4
│   ├── monitor_campaign_performance.py # Phase 5
│   └── rollback_campaign_swap.py       # Phase 6
├── backend/
│   ├── services/
│   │   ├── campaign_creator.py         # Core campaign creation logic
│   │   ├── campaign_validator.py       # Validation logic
│   │   └── ghl_notifier.py             # GHL integration
│   └── routers/
│       └── campaigns.py                # API endpoints for monitoring
├── .tmp/
│   ├── campaign-plan-{timestamp}.json
│   └── validation-report-{id}.json
├── logs/
│   └── campaign-creation-{timestamp}.log
└── docs/
    ├── PARALLEL-CAMPAIGN-IMPLEMENTATION-PLAN.md  # This file
    └── sop/
        └── CAMPAIGN-OPTIMIZATION-SOP.md          # Step-by-step SOP
```

---

## Database Schema Changes

### New Table: `campaign_modifications`

```sql
CREATE TABLE campaign_modifications (
    id SERIAL PRIMARY KEY,
    client_id INTEGER NOT NULL REFERENCES clients(id),
    source_campaign_id BIGINT NOT NULL,
    source_campaign_name VARCHAR(255) NOT NULL,
    new_campaign_id BIGINT,
    new_campaign_name VARCHAR(255),
    analysis_run_id UUID REFERENCES analysis_runs(run_id),
    status VARCHAR(50) NOT NULL, -- 'planned', 'created', 'validated', 'active', 'rolled_back'
    validation_report JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    activated_at TIMESTAMP,
    rolled_back_at TIMESTAMP,
    rollback_reason TEXT,
    created_by VARCHAR(100), -- User who initiated
    notes TEXT
);

CREATE INDEX idx_campaign_mods_client ON campaign_modifications(client_id);
CREATE INDEX idx_campaign_mods_status ON campaign_modifications(status);
```

---

## Environment Variables Required

```bash
# Google Ads API (already configured)
GOOGLE_ADS_DEVELOPER_TOKEN=...
GOOGLE_ADS_CLIENT_ID=...
GOOGLE_ADS_CLIENT_SECRET=...
GOOGLE_ADS_REFRESH_TOKEN=...
GOOGLE_ADS_LOGIN_CUSTOMER_ID=...

# GoHighLevel API (for notifications)
GHL_API_KEY=...
GHL_LOCATION_ID=...  # Priority Roofing's GHL location
```

---

## Standard Operating Procedure (SOP)

**File**: `ads-monkee/docs/sop/CAMPAIGN-OPTIMIZATION-SOP.md`

### For New Client Campaign Optimizations

1. **Run AI Analysis** (if not already done):
   ```bash
   POST /api/analysis/clients/{id}/analyze
   ```

2. **Review Analysis Output**:
   - Check `pr-{client}_editor_keywords_to_add.csv`
   - Check `pr-{client}_editor_negative_keywords.csv`
   - Verify recommendations make sense

3. **Create Campaign (Dry-Run)**:
   ```bash
   poetry run python scripts/create_optimized_campaign.py \
     --client-id {id} \
     --source-campaign "{name}" \
     --analysis-dir "{path}" \
     --dry-run
   ```
   - Review output JSON
   - Confirm budget matches original
   - Approve to proceed

4. **Create Campaign (Live)**:
   ```bash
   poetry run python scripts/create_optimized_campaign.py \
     --client-id {id} \
     --source-campaign "{name}" \
     --analysis-dir "{path}" \
     --plan-file .tmp/campaign-plan.json
   ```
   - Note new campaign ID

5. **Validate Campaign**:
   ```bash
   poetry run python scripts/validate_campaign.py \
     --client-id {id} \
     --new-campaign-id {new_id} \
     --source-campaign "{name}" \
     --plan-file .tmp/campaign-plan.json
   ```
   - **MUST SHOW "VALIDATION: PASS"**
   - If FAIL, review errors and fix manually in Google Ads, then re-validate

6. **Activate Campaign Swap**:
   ```bash
   poetry run python scripts/activate_campaign_swap.py \
     --client-id {id} \
     --new-campaign-id {new_id} \
     --source-campaign "{name}" \
     --validation-report .tmp/validation-report-{new_id}.json \
     --confirm
   ```
   - Verify GHL note was created
   - Confirm both campaigns show correct status

7. **Monitor for 7 Days**:
   - Check dashboard daily: `/campaigns/compare?old={old_id}&new={new_id}`
   - Review automated alerts
   - Day 7: Review GHL summary note

8. **Make Decision**:
   - **Keep v2**: Archive old campaign (don't delete)
   - **Rollback**: Run `rollback_campaign_swap.py`
   - **Extend**: Continue monitoring 7 more days

9. **Document Outcome**:
   - Update `campaign_modifications` table with final status
   - Add note to client record in GHL
   - If successful, share learnings with team

---

## Success Criteria

- ✓ Dry-run produces accurate campaign plan
- ✓ Campaign created in PAUSED state via API
- ✓ Validation confirms budget matches original exactly
- ✓ Validation confirms all keywords/negatives match plan
- ✓ Activation swaps campaigns atomically
- ✓ GHL notification sent successfully
- ✓ Monitoring dashboard shows side-by-side comparison
- ✓ Rollback script tested and ready
- ✓ SOP documented for future clients

---

## Risk Mitigation

1. **Budget Mismatch**: Validation script blocks activation if budgets don't match
2. **API Errors**: All API calls wrapped in try/except with detailed logging
3. **Disapproved Ads**: Validation script flags disapprovals before activation
4. **Performance Drop**: Automated alerts + rollback script ready
5. **Accidental Deletion**: Never delete campaigns, only pause/archive
6. **Lost Changes**: All operations logged to database and files

---

## Testing Plan

### Unit Tests
- `test_campaign_creator.py`: Test campaign structure building
- `test_campaign_validator.py`: Test validation logic
- `test_ghl_notifier.py`: Test GHL API integration (mocked)

### Integration Tests
- `test_create_campaign_e2e.py`: Full flow with test Google Ads account
- `test_validation_e2e.py`: Validate against real API response
- `test_rollback_e2e.py`: Test rollback procedure

### Manual Testing (Priority Roofing)
1. Run dry-run, review output
2. Create campaign in test mode (if available)
3. Validate with real data
4. Activate on low-budget test campaign first
5. Monitor for 24 hours before full rollout

---

## Timeline Estimate

- **Phase 1 (Dry-Run Script)**: 3-4 hours
- **Phase 2 (Creation Script)**: 4-5 hours
- **Phase 3 (Validation Script)**: 3-4 hours
- **Phase 4 (Activation Script)**: 2-3 hours
- **Phase 5 (Monitoring Dashboard)**: 4-5 hours
- **Phase 6 (Rollback Script)**: 2 hours
- **Database Schema**: 1 hour
- **SOP Documentation**: 2 hours
- **Testing**: 4-5 hours

**Total**: 25-33 hours (3-5 days)

---

## Dependencies

- Google Ads API Python client (already installed)
- GoHighLevel API access (need to verify credentials)
- Database migration for `campaign_modifications` table
- Celery tasks for monitoring (can reuse existing infrastructure)

---

## Next Steps

1. Confirm this plan aligns with your vision
2. Verify Google Ads API credentials are working
3. Verify GHL API credentials and Priority Roofing location ID
4. Begin Phase 1 implementation (dry-run script)
5. Test with Priority Roofing data
6. Execute full workflow
7. Document results
8. Generalize for other clients

---

**Questions or modifications needed before implementation?**

