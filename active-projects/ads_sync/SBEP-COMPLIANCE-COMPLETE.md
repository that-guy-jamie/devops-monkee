# SBEP v2.0 Compliance Complete

**Date:** October 15, 2025  
**Projects:** ads_sync + ads_sync_dashboard  
**Status:** ✅ SBEP v2.0 Compliant

---

## Executive Summary

Successfully implemented SBEP v2.0 (Source-Bound Execution Protocol) compliance for both `ads_sync` and `ads_sync_dashboard` projects. This empowers AI agents with clear documentation-first operating instructions, autonomy guidelines, and project-specific rules.

---

## What is SBEP v2.0?

**Core Principle:** Read The F***ing Manual (RTFM) before attempting any task or asking for help.

SBEP v2.0 is the mandatory operating standard for all AI agents in the `/projects/` workspace. It enforces:

✅ **Documentation-First Approach** - Agents must consult docs before claiming inability  
✅ **Autonomy with Accountability** - Clear permissions and requirements  
✅ **Safety & Rollback** - All changes reversible  
✅ **Cross-Project Learning** - Reuse patterns from other projects  
✅ **Housekeeping Policy** - Archive, never delete

---

## Implementation Actions

### 1. Fixed SBEP-INIT.ps1 Script

**Problem:** Script had PowerShell syntax errors (emoji characters in strings, ampersand in header)

**Fix Applied:**
- Replaced emoji characters with ASCII: `✅` → `[OK]`, `ℹ️` → `[INFO]`, etc.
- Fixed header: `"Phase 4: Housekeeping & Archival"` → `"Phase 4: Housekeeping and Archival"`
- Fixed comment: `"--SkipHousekeeping"` → `"SkipHousekeeping"`
- Removed emoji: `"🚀"` → removed

**Result:** ✅ Script now runs successfully on Windows

### 2. Initialized ads_sync Project

**Command:**
```powershell
.\SBEP-INIT.ps1 -ProjectPath C:\Users\james\Desktop\Projects\ads_sync -SkipHousekeeping
```

**Created:**
- `ads_sync/sds/` - Source Documentation Store directory
- `ads_sync/sds/SBEP-MANDATE.md` - Project-specific agent instructions
- `ads_sync/sds/SBEP-INDEX.yaml` - Documentation inventory
- `.sbep-rollback-20251015-150951.json` - Rollback snapshot

**Skipped Housekeeping:** Project was already cleaned in recent housekeeping session

### 3. Customized ads_sync SBEP-MANDATE.md

**Comprehensive 400+ line mandate including:**

- **Technology Stack:** Python 3.12, Google Ads API v28, Pandas, YAML
- **Architecture:** Sync & Append pattern with watermarks
- **Command Status:** init ✅, append ⏳, report ⏳, repair ⏳, validate ✅
- **Critical Files:** Master CSVs, state JSONs, client YAMLs
- **Data Locations:** 30 clients, 126,889 rows, 1 year historical data
- **Known Issues:** 5 no-data clients flagged for investigation
- **Common Tasks:** How to implement append, generate reports, debug, add clients
- **Anti-Patterns:** What to avoid (datetime.utcnow, hardcoded clients, bypassing locks)
- **Best Practices:** Watermark-based sync, atomic writes, schema validation
- **Dashboard Integration:** How ads_sync_dashboard interacts with CLI

### 4. Initialized ads_sync_dashboard Project

**Command:**
```powershell
.\SBEP-INIT.ps1 -ProjectPath C:\Users\james\Desktop\Projects\ads_sync_dashboard -SkipHousekeeping
```

**Created:**
- `ads_sync_dashboard/sds/` - Source Documentation Store directory
- `ads_sync_dashboard/sds/SBEP-MANDATE.md` - Dashboard-specific instructions
- `ads_sync_dashboard/sds/SBEP-INDEX.yaml` - Documentation inventory
- `.sbep-rollback-20251015-151003.json` - Rollback snapshot

### 5. Customized ads_sync_dashboard SBEP-MANDATE.md

**Comprehensive 300+ line mandate including:**

- **Technology Stack:** FastAPI, Celery, Redis, Docker, Windows-compatible
- **Architecture:** Decoupled API → Redis → Celery Worker → CLI subprocess
- **Critical Constraints:** MUST use Celery `--pool=solo` on Windows (not RQ)
- **Starting the Stack:** Redis (Docker), FastAPI server, Celery worker
- **Integration Points:** How dashboard executes ads_sync CLI via subprocess
- **Common Tasks:** Add endpoints, add Celery tasks, debug failed jobs, set up scheduling
- **Anti-Patterns:** Using RQ, blocking API, not capturing subprocess output
- **Best Practices:** Async endpoints, proper error handling, Redis health checks
- **Sibling Project:** Relationship with ../ads_sync/ and integration points

### 6. Updated Main README

**File:** `C:\Users\james\Desktop\Projects\README.md`

**Changes:**
- Added `ads_sync` and `ads_sync_dashboard` to SBEP-Compliant Projects table
- Both marked ✅ Compliant with initialization date 2025-10-15
- Noted 0 archived files (pre-cleaned/new project)

---

## SBEP-Compliant Projects Status

| Project | Status | Initialized | SDS Files |
|---------|--------|-------------|-----------|
| **ASTRO** | ✅ Compliant | 2025-10-15 | 2 |
| **ads_sync** | ✅ Compliant | 2025-10-15 | 2 |
| **ads_sync_dashboard** | ✅ Compliant | 2025-10-15 | 2 |
| google-ads-manager | 🔄 Pending | - | - |
| LCG | 🔄 Pending | - | - |
| LSA | 🔄 Pending | - | - |

---

## Agent Operating Protocol

### For AI Agents Working in ads_sync:

**Required Reading Sequence:**
1. `/projects/SBEP-MANIFEST.md` - Global mandate
2. `ads_sync/sds/SBEP-MANDATE.md` - Project-specific rules
3. `ads_sync/README.md` - Complete documentation
4. `ads_sync/PHASE-1-COMPLETE-FINAL.md` - Current data state
5. `ads_sync/QUICK-REFERENCE.md` - Common commands

**Key Rules:**
- Test on 1-2 clients before rolling out to all 30
- Never delete master CSVs (append and deduplicate)
- Always use file locks for concurrency
- Check `/projects/API-docs/google-ads-python/` for API capabilities
- Follow watermark-based incremental sync pattern
- Verify Python 3.12 compatibility (NOT 3.13)

### For AI Agents Working in ads_sync_dashboard:

**Required Reading Sequence:**
1. `/projects/SBEP-MANIFEST.md` - Global mandate
2. `ads_sync_dashboard/sds/SBEP-MANDATE.md` - Dashboard-specific rules
3. `ads_sync_dashboard/README.md` - API documentation
4. `../ads_sync/README.md` - CLI tool documentation
5. `../ads_sync/sds/SBEP-MANDATE.md` - CLI project rules

**Key Rules:**
- MUST use Celery `--pool=solo` on Windows
- Never block API endpoints (async operations only)
- Capture subprocess stdout/stderr/exit_code
- Verify Redis is running before operations
- Test both API server and Celery worker after changes
- CLI must be functional for dashboard to work

---

## Documentation Locations

### ads_sync Project

```
ads_sync/
├── sds/
│   ├── SBEP-MANDATE.md          # Project-specific agent instructions
│   └── SBEP-INDEX.yaml          # Documentation inventory
├── README.md                    # Main documentation
├── PHASE-1-COMPLETE-FINAL.md    # Phase 1 summary
├── HOUSEKEEPING-COMPLETE.md     # Cleanup summary
├── QUICK-REFERENCE.md           # Daily operations guide
└── SBEP-COMPLIANCE-COMPLETE.md  # This file
```

### ads_sync_dashboard Project

```
ads_sync_dashboard/
├── sds/
│   ├── SBEP-MANDATE.md          # Dashboard-specific instructions
│   └── SBEP-INDEX.yaml          # Documentation inventory
└── README.md                    # API documentation
```

---

## Rollback Capability

Both projects have rollback snapshots:

**ads_sync:**
```powershell
cd C:\Users\james\Desktop\Projects\SBEP_Core
.\SBEP-INIT.ps1 -ProjectPath C:\Users\james\Desktop\Projects\ads_sync -Rollback -Timestamp 20251015-150951
```

**ads_sync_dashboard:**
```powershell
cd C:\Users\james\Desktop\Projects\SBEP_Core
.\SBEP-INIT.ps1 -ProjectPath C:\Users\james\Desktop\Projects\ads_sync_dashboard -Rollback -Timestamp 20251015-151003
```

---

## Benefits Realized

### 1. **Clear Authority**
Agents now have explicit permission to:
- Execute commands and scripts
- Create/modify files
- Install dependencies
- Make architectural decisions

### 2. **Documentation-First**
Agents must:
- Consult project docs before claiming inability
- Check `/projects/API-docs/` for API capabilities
- Review similar patterns in other projects
- Provide evidence of attempts before asking for help

### 3. **Safety & Reversibility**
- All changes have rollback plans
- Rollback snapshots automatically created
- Housekeeping archives instead of deletes
- Changes documented in CHANGELOG

### 4. **Cross-Project Learning**
- Agents can reference ASTRO patterns
- Reuse proven solutions
- Learn from other project implementations
- Share best practices

### 5. **Accountability**
- Success metrics defined
- Documentation consultation required
- Methods attempted must be shown
- Error messages must be provided

---

## Next Steps

### Immediate (Already Addressed)

✅ Fix SBEP-INIT.ps1 script  
✅ Initialize ads_sync with SBEP v2.0  
✅ Initialize ads_sync_dashboard with SBEP v2.0  
✅ Customize both SBEP-MANDATE.md files  
✅ Update main Projects README

### Phase 2 Sprint (Now Ready to Begin)

With SBEP v2.0 in place, agents now have clear guidelines to:

**Priority 1: Critical Blockers**
1. Investigate 5 no-data clients (guided by SBEP mandate)
2. Implement schema validation (patterns documented)
3. Enhance `validate` command (task reference provided)

**Priority 2: Core Features**
4. Implement `append` command (complete task guide in mandate)
5. Test append on 2-3 clients (testing approach defined)
6. Implement `report` command (template already exists)

**Priority 3: Automation**
7. Set up Celery Beat scheduling (example in dashboard mandate)
8. Implement `repair` command (similar to append)

---

## Success Metrics

SBEP compliance measured by:

✅ **Documentation exists** - sds/ directory with mandate and index  
✅ **Agents read docs first** - Before claiming inability  
✅ **Clear task guidance** - Common tasks documented  
✅ **Anti-patterns defined** - What to avoid explicitly stated  
✅ **Best practices shared** - Proven patterns documented  
✅ **Rollback capability** - Changes are reversible  
✅ **Cross-project awareness** - References to sibling projects

---

## Sign-Off

**SBEP Compliance Status:** ✅ Complete  
**Script Fixes:** ✅ Tested and Working  
**Documentation:** ✅ Comprehensive and Customized  
**Rollback Snapshots:** ✅ Created  
**Main README:** ✅ Updated  
**Ready for Phase 2:** ✅ Yes

---

**Completed:** October 15, 2025  
**Projects:** ads_sync v0.1.0 + ads_sync_dashboard v0.1.0  
**Protocol:** SBEP v2.0  
**Organization:** OneClickSEO PPC Management

---

**AI Agents:** You now have clear authority and documentation to proceed with Phase 2 implementation. Read the mandate, follow the patterns, consult the docs, and get shit done.

