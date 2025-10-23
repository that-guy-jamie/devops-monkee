# SBEP v2.0 - Output Management Plan

**Version:** 1.0  
**Status:** 📋 Awaiting Approval  
**Last Updated:** 2025-10-15

---

## Purpose

This plan establishes **consistent, logical locations** for all generated content (reports, logs, crawls, documentation, etc.) across the workspace. Agents must follow these conventions to maintain organization and prevent clutter.

---

## Guiding Principles

1. **Type-Based Organization** - Different output types go to different locations
2. **Predictable Paths** - Same structure across all projects
3. **Git-Safe** - Transient/sensitive outputs excluded from version control
4. **Self-Documenting** - Clear folder names indicate content type
5. **Archive-Ready** - Easy to identify and archive old outputs

---

## Output Type Taxonomy

### 1. Reports
**Definition:** Analysis, audits, summaries, metrics  
**Examples:** SEO audits, GHL system audits, performance reports

**Location Pattern:**
```
Global:   /projects/reports/{project-name}/{report-type}/
Project:  {project}/reports/{report-type}/

Example:
  astro/reports/ghl/audit-2025-10-15.json
  astro/reports/seo/theastro-audit-2025-10-15.json
```

**Naming Convention:**
- `{report-type}-{ISO-DATE}.{ext}`
- `{report-type}-{ISO-TIMESTAMP}.{ext}` (if multiple per day)

**Git Status:** ⚠️ Excluded (large files, frequent updates)

---

### 2. Logs
**Definition:** Execution logs, error logs, audit trails  
**Examples:** Script execution logs, API call logs, cron job logs

**Location Pattern:**
```
Project:  {project}/logs/{log-type}/

Example:
  astro/logs/ghl/api-calls-2025-10-15.log
  astro/logs/deployment/deploy-2025-10-15T14-30-22.log
  lsa-dashboard/logs/audit/audit-2025-10-15.log
```

**Naming Convention:**
- `{log-type}-{ISO-DATE}.log`
- `{script-name}-{ISO-TIMESTAMP}.log`

**Retention:** Keep last 30 days, archive older

**Git Status:** ❌ Excluded (transient, sensitive)

---

### 3. Data
**Definition:** API responses, database exports, crawled data  
**Examples:** LSA leads, contact exports, crawler results

**Location Pattern:**
```
Project:  {project}/data/{data-source}/

Example:
  lsa-dashboard/data/priority-roofing/priority-roofing-lsa-leads-2025-10-15.json
  astro/data/ghl-exports/contacts-export-2025-10-15.csv
```

**Special Case - Crawler Data:**
```
Tools/SEO-Crawler/output/{domain}/
  theastro.org/
    crawl-2025-10-15.csv
    audit-2025-10-15.json
```

**Git Status:** ⚠️ Excluded (large files, PII risk)

---

### 4. Artifacts
**Definition:** Generated code, compiled assets, optimized files  
**Examples:** Optimized images, bundled scripts, compiled CSS

**Location Pattern:**
```
Project:  {project}/artifacts/{artifact-type}/
Tool:     Tools/{tool-name}/output/{artifact-type}/

Example:
  astro/artifacts/images/optimized/
  astro/artifacts/bundles/app-bundle-v1.2.3.js
  Tools/astro-images/output/optimized/
```

**Git Status:** 🔀 Depends - Optimized images (maybe), bundles (maybe), temp artifacts (no)

---

### 5. Documentation (Generated)
**Definition:** Status updates, handoffs, summaries, work order completions  
**Examples:** Deployment summaries, implementation complete docs, agent handoffs

**Location Pattern:**
```
Project:  {project}/docs/status/
          {project}/docs/summaries/
          {project}/docs/handoffs/

Example:
  astro/docs/status/GHL-REMEDIATION-COMPLETE.md
  astro/docs/summaries/DEPLOYMENT-SUCCESS.md
  astro/docs/handoffs/HANDOFF-NEXT-AGENT-ASTRO-MAKEOVER.md
```

**Naming Convention:**
- UPPERCASE for major milestones
- Include date suffix for time-series: `{NAME}-{YYYY-MM-DD}.md`

**Git Status:** ✅ Included (important project history)

---

### 6. Backups & Snapshots
**Definition:** Rollback data, pre-change state, backup exports  
**Examples:** SBEP rollback files, database backups, pre-deployment snapshots

**Location Pattern:**
```
Project:  {project}/.backups/{backup-type}/
          {project}/.rollback-{timestamp}.json

Example:
  astro/.sbep-rollback-20251015-133522.json
  astro/.backups/ghl-contacts-pre-backfill-2025-10-15.json
```

**Git Status:** ❌ Excluded (sensitive, large, transient)

---

### 7. Archives
**Definition:** Obsolete files, completed work, deprecated code  
**Examples:** Old scripts, superseded docs, completed work orders

**Location Pattern:**
```
Global:   /projects/archive/{project}-{category}-{MMDDYYYY}.zip
Project:  {project}/archive/{category}/

Example:
  /projects/archive/astro-housekeeping-10152025.zip
  /projects/archive/root-housekeeping-10152025.zip
  astro/archive/v1-scripts/
  astro/workorders/Completed Workorders/
```

**Git Status:** ❌ Excluded (historical, zipped archives are binary)

---

### 8. Temporary Files
**Definition:** Work-in-progress, staging, intermediate processing  
**Examples:** Download staging, processing temp, upload prep

**Location Pattern:**
```
Project:  {project}/.tmp/
Global:   /projects/Temp/

Example:
  astro/.tmp/image-processing/
  /projects/Temp/sbep-staging/
```

**Retention:** Clean up after task completion

**Git Status:** ❌ Excluded (transient by definition)

---

## Directory Structure Standards

### Project-Level Structure
```
{project}/
├── sds/                          # SBEP documentation store
├── src/                          # Source code
├── scripts/                      # Automation scripts
├── ops/                          # Operations & deployment
├── docs/                         # Core documentation
│   ├── status/                   # Status updates (generated)
│   ├── summaries/                # Completion summaries (generated)
│   └── handoffs/                 # Agent handoffs (generated)
├── reports/                      # 🆕 Analysis & audits (generated)
│   ├── ghl/
│   ├── seo/
│   └── performance/
├── logs/                         # 🆕 Execution logs (generated)
│   ├── api/
│   ├── deployment/
│   └── errors/
├── data/                         # 🆕 API responses & exports (generated)
│   └── {data-source}/
├── artifacts/                    # 🆕 Generated assets (generated)
│   ├── images/
│   └── bundles/
├── archive/                      # 🆕 Obsolete files (manual move)
├── workorders/                   # Active work orders
│   └── Completed Workorders/     # Archived work orders
├── .backups/                     # 🆕 Rollback data (generated)
├── .tmp/                         # 🆕 Temporary files (generated)
└── .sbep-rollback-*.json         # SBEP rollback snapshots
```

### Global Structure
```
/projects/
├── SBEP-MANIFEST.md              # Global mandate
├── SBEP_Core/                    # Templates & init
├── API-docs/                     # Centralized API docs
├── reports/                      # 🆕 Cross-project reports
│   └── {project-name}/
├── archive/                      # 🆕 Global archives
│   ├── {project}-housekeeping-{date}.zip
│   └── {project}-workorders-{date}.zip
├── Output/                       # 🆕 Domain-based web outputs
│   └── {domain}/
├── Tools/                        # Utilities
│   └── {tool-name}/
│       ├── scripts/
│       └── output/               # 🆕 Tool-specific outputs
├── Workorders/                   # Global work orders
│   └── Completed Workorders/
└── Temp/                         # Global temp (ephemeral)
```

---

## Agent Rules - Where to Put Generated Content

### When generating a report:
```
✅ DO:    {project}/reports/{type}/{name}-{date}.{ext}
❌ DON'T: {project}/docs/ (reserved for human-authored docs)
❌ DON'T: /projects/ root (clutters workspace)
```

### When creating status documentation:
```
✅ DO:    {project}/docs/status/STATUS-UPDATE-{DATE}.md
✅ DO:    {project}/docs/summaries/IMPLEMENTATION-COMPLETE.md
❌ DON'T: {project}/README.md (reserve for project overview)
```

### When logging script execution:
```
✅ DO:    {project}/logs/{script-category}/script-name-{timestamp}.log
❌ DON'T: {project}/scripts/ (source code location, not logs)
❌ DON'T: Console only (logs should be persisted)
```

### When saving API responses:
```
✅ DO:    {project}/data/{api-source}/export-{date}.json
❌ DON'T: {project}/config/ (not configuration)
❌ DON'T: /projects/ root
```

### When creating temporary files:
```
✅ DO:    {project}/.tmp/{task-name}/
✅ DO:    Clean up after task completion
❌ DON'T: {project}/temp/ (use hidden .tmp/)
❌ DON'T: Leave temp files indefinitely
```

### When archiving obsolete files:
```
✅ DO:    {project}/archive/{category}/ (per-project archive)
✅ DO:    /projects/archive/{project}-{category}-{date}.zip (global archive)
❌ DON'T: Delete files (archive instead)
```

### When completing a work order:
```
✅ DO:    Add completion summary to work order
✅ DO:    Move to {project}/workorders/Completed Workorders/
✅ DO:    Reference completion in project CHANGELOG
❌ DON'T: Archive incomplete work orders
❌ DON'T: Delete work orders (move to Completed Workorders/)
```

---

## .gitignore Updates

### Required Exclusions

Add to `/projects/.gitignore`:

```gitignore
# === SBEP v2.0 Output Management ===

# Reports (large, frequent updates)
**/reports/
/reports/

# Logs (transient, may contain sensitive data)
**/logs/
*.log
*.log.*

# Data exports (large files, PII risk)
**/data/
/lsa-data/
/lsa-audit-logs/

# Temporary files
**/.tmp/
**/temp/
/Temp/

# Backups & Rollbacks
**/.backups/
**/.sbep-rollback-*.json

# Archives (binary zips, large)
/archive/
**/archive/*.zip

# Tool outputs
/Tools/**/output/
/Output/

# Artifacts (varies by project)
**/artifacts/
/Tools/astro-images/output/

# Node/Python/Build artifacts
node_modules/
__pycache__/
*.pyc
venv/
.venv/
dist/
build/

# Environment & Credentials
.env
.env.*
!.env.example
*-service-account.json
google-service-account.json

# IDE & OS
.vscode/
.idea/
.DS_Store
Thumbs.db
*.swp
*.swo
*~

# === End SBEP v2.0 ===
```

### Per-Project .gitignore Recommendations

Each project should have a minimal `.gitignore`:

```gitignore
# Project-specific ignores
reports/
logs/
data/
.tmp/
.backups/
.sbep-rollback-*.json
artifacts/generated/  # Keep artifacts/final/ if needed

# Project-specific exceptions (uncomment as needed)
# !artifacts/final/production-bundle.js
# !reports/latest-seo-audit.json
```

---

## Migration Plan

### Phase 1: Create Directories (Non-Breaking)
For each project with active development (ASTRO, LCG, LSA, google-ads-manager):

1. Create new output directories:
   ```powershell
   New-Item -ItemType Directory -Path "{project}/reports" -Force
   New-Item -ItemType Directory -Path "{project}/logs" -Force
   New-Item -ItemType Directory -Path "{project}/data" -Force
   New-Item -ItemType Directory -Path "{project}/artifacts" -Force
   New-Item -ItemType Directory -Path "{project}/.tmp" -Force
   New-Item -ItemType Directory -Path "{project}/.backups" -Force
   New-Item -ItemType Directory -Path "{project}/archive" -Force
   ```

2. Create documentation subdirectories:
   ```powershell
   New-Item -ItemType Directory -Path "{project}/docs/status" -Force
   New-Item -ItemType Directory -Path "{project}/docs/summaries" -Force
   New-Item -ItemType Directory -Path "{project}/docs/handoffs" -Force
   ```

3. Add `.gitkeep` files to empty directories (if needed for Git)

### Phase 2: Update SBEP Documentation

1. Add "Output Management" section to `SBEP-MANIFEST.md`
2. Update project templates (`SBEP-MANDATE-TEMPLATE.md`)
3. Add output location rules to agent instructions

### Phase 3: Migrate Existing Files (Per Project)

For ASTRO (example):
```
Move:
  astro/GHL-REMEDIATION-COMPLETE.md → astro/docs/summaries/
  astro/DEPLOYMENT-SUCCESS.md → astro/docs/summaries/
  astro/HANDOFF-NEXT-AGENT-*.md → astro/docs/handoffs/
  astro/astro-ghl-audit-*.json → astro/reports/ghl/
  astro/AUDIT-SESSION-SNAPSHOT.md → astro/docs/status/ (or archive if obsolete)
```

**Rule:** Only move files that are clearly categorized. When uncertain, leave in place.

### Phase 4: Update .gitignore

1. Update `/projects/.gitignore` with comprehensive exclusions
2. Add project-level `.gitignore` files where missing
3. Test that sensitive files (`.env`, logs, data exports) are excluded
4. Commit .gitignore changes

### Phase 5: Agent Training & Validation

1. Test agent compliance with new output rules
2. Monitor for 1 week to catch violations
3. Refine rules based on observed patterns

---

## Tool-Specific Rules

### SEO-Crawler
```
Output:     Tools/SEO-Crawler/output/{domain}/
Structure:  {domain}/{crawl-date}.{csv|json}
Git:        Excluded
```

### astro-images
```
Output:     Tools/astro-images/output/{original|optimized}/
Structure:  Subdirectories by processing stage
Git:        Excluded (source images in project, not tool)
```

### Future Tools
All tools must have:
- `scripts/` - Tool code
- `output/` - Generated files
- `README.md` - Usage guide

---

## Enforcement

### Agent Responsibilities
1. **Before writing any file:** Check this plan for correct location
2. **After generating output:** Verify file is in correct directory
3. **Before archiving:** Follow workorder completion checklist
4. **Cleanup:** Remove `.tmp/` contents after task completion

### Automatic Checks (Future)
- Pre-commit hook validates output locations
- Scheduled job archives old reports/logs
- Script scans for misplaced files weekly

---

## Open Questions for User Approval

1. **Reports Retention:** How long to keep reports before archiving? (Suggest: 90 days)
2. **Logs Retention:** How long to keep logs? (Suggest: 30 days)
3. **Data Exports:** Should data exports ever be in Git? (Suggest: No, except small reference data)
4. **Status Docs:** Should status docs go in Git? (Suggest: Yes, they're important history)
5. **Artifacts:** Which artifacts should be in Git? (Suggest: Final production builds only)

---

## Summary

**What Changes:**
- 7 new output directory types defined
- Clear rules for what goes where
- Comprehensive .gitignore updates
- Agent training on output locations

**What Doesn't Change:**
- Existing project source code locations
- Core documentation structure
- SBEP mandate and templates (only additions)

**Benefits:**
- Predictable, consistent structure
- No more stray files at project root
- Git-safe (sensitive/large files excluded)
- Easy to find generated content
- Simple to archive old outputs

---

**Status:** 📋 Awaiting user approval  
**Next Step:** User reviews and approves/modifies plan  
**Then:** Implement Phase 1-4, update SBEP documentation

