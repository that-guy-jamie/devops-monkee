# SBEP v2.0 Migration Guide

**Onboarding Existing Projects to SBEP v2.0 Standard**

---

## Overview

This guide walks through migrating an existing project to SBEP v2.0 compliance. The process is automated via `SBEP-INIT.ps1` but understanding the steps helps with customization and troubleshooting.

**Time Required:** 5-15 minutes per project  
**Difficulty:** Easy (mostly automated)  
**Rollback:** Supported via automatic snapshots

---

## Prerequisites

### Before You Begin

✅ **Global infrastructure must be in place:**
- `/projects/SBEP-MANIFEST.md` exists
- `/projects/SBEP_Core/` directory with templates
- `/projects/API-docs/` centralized documentation
- `/projects/archive/` for obsolete files

✅ **Project requirements:**
- Project exists in `/projects/{project-name}/`
- You have write permissions
- Project has a `README.md` (recommended)

✅ **Tools:**
- PowerShell 5.1+ (Windows) or PowerShell Core (cross-platform)

---

## Migration Steps

### Step 1: Backup (Optional but Recommended)

Before migration, create a manual backup if the project is critical:

```powershell
$project = "astro"  # Change to your project name
$date = Get-Date -Format "yyyyMMdd"
Compress-Archive -Path "C:\Users\james\Desktop\Projects\$project" `
                 -DestinationPath "C:\Users\james\Desktop\Projects\archive\$project-pre-sbep-$date.zip"
```

### Step 2: Run SBEP-INIT.ps1

```powershell
cd C:\Users\james\Desktop\Projects\SBEP_Core
.\SBEP-INIT.ps1 -ProjectPath C:\Users\james\Desktop\Projects\{project-name}
```

**Example:**
```powershell
.\SBEP-INIT.ps1 -ProjectPath C:\Users\james\Desktop\Projects\lcg-system-main
```

### Step 3: Review Output

The script will:
1. Create `/sds/` directory
2. Install `SBEP-MANDATE.md` (customized with project name)
3. Generate `SBEP-INDEX.yaml` (scans for markdown files)
4. Identify obsolete files (cheatsheets, .old, .bak)
5. Archive obsolete files to `/projects/archive/{project}-housekeeping-{date}.zip`
6. Create rollback snapshot

**Expected Output:**
```
✅ Created: C:\...\{project}\sds/
✅ Installed: SBEP-MANDATE.md
✅ Generated: SBEP-INDEX.yaml
✅ Archived 2 files
✅ Rollback snapshot: .sbep-rollback-{timestamp}.json
🚀 SBEP v2.0 initialization successful!
```

### Step 4: Customize SBEP-MANDATE.md

Edit `{project}/sds/SBEP-MANDATE.md` to add project-specific details:

```markdown
**Project Name:** {project}
**Primary Language/Stack:** WordPress/PHP + Node.js + React  # ← Fill this in
**Key Integrations:** GoHighLevel v2, Google Ads API  # ← Fill this in
**Current Phase:** Production  # ← Fill this in
```

**Key sections to customize:**
- Technology Stack (languages, frameworks, databases)
- Integration Documentation (which APIs from `/projects/API-docs/`)
- Deployment Method (hosting, CI/CD)
- Project-Specific Anti-Patterns (things to avoid)

### Step 5: Curate SBEP-INDEX.yaml

Review `{project}/sds/SBEP-INDEX.yaml`:

1. **Mark existing files:**
   - Change `exists: false` to `exists: true` for files found
   
2. **Add project-specific docs:**
   ```yaml
   guides:
     - path: "docs/GHL-INTEGRATION-GUIDE.md"
       description: "GoHighLevel integration patterns"
       priority: "high"
       exists: true
   ```

3. **Remove irrelevant entries:**
   - Delete template entries that don't apply to your project

4. **Add cross-project references:**
   ```yaml
   cross_project_patterns:
     - pattern: "GHL v2 API audit system"
       reference_project: "astro"
       location: "astro/scripts/ghl/"
       description: "Reusable audit scripts"
   ```

### Step 6: Update Project README (Recommended)

Add an SBEP compliance notice to the project's main `README.md`:

```markdown
## 📋 SBEP v2.0 Compliance

This project follows the **Source-Bound Execution Protocol (SBEP) v2.0**.

**For AI Agents:**
1. Read `/projects/SBEP-MANIFEST.md` (global mandate)
2. Read `sds/SBEP-MANDATE.md` (project-specific instructions)
3. Consult `sds/SBEP-INDEX.yaml` for documentation inventory
4. Check `/projects/API-docs/` before claiming API unavailability

**Documentation:** All project documentation is indexed in `sds/SBEP-INDEX.yaml`
```

### Step 7: Test Agent Compliance

Start a new agent session and verify:

1. **Agent reads global manifest:**
   - Mentions checking SBEP-MANIFEST.md
   - Understands RTFM mandate

2. **Agent reads project mandate:**
   - References `sds/SBEP-MANDATE.md`
   - Understands project-specific rules

3. **Agent checks documentation:**
   - Consults SBEP-INDEX.yaml before claiming docs don't exist
   - References `/projects/API-docs/` for API questions

### Step 8: Update Project CHANGELOG

Add an entry documenting the SBEP migration:

```markdown
## [Version] - 2025-10-15

### Changed
- **SBEP v2.0 Compliance:** Migrated to Source-Bound Execution Protocol
  - Created `/sds/` directory with agent operating instructions
  - Generated documentation inventory in `sds/SBEP-INDEX.yaml`
  - Archived obsolete cheatsheets to `/projects/archive/`
  - See `sds/SBEP-MANDATE.md` for agent guidelines
```

---

## What Gets Archived

The script automatically identifies and archives:

### Obsolete File Patterns

| Pattern | Example | Reason |
|---------|---------|--------|
| `*cheatsheet*.md` | `api-cheatsheet.md` | Replaced by centralized `/projects/API-docs/` |
| `*deprecated*.md` | `old-deprecated-guide.md` | Explicitly marked as obsolete |
| `*old*.md` | `architecture-old.md` | Old versions of docs |
| `*.old`, `*.bak` | `config.old`, `script.bak` | Backup files |
| `*-old.*` | `deploy-old.sh` | Old versions with suffix |

### What DOESN'T Get Archived

- Active documentation
- Code files (.js, .py, .php, etc.)
- Configuration files (package.json, .env.example)
- `node_modules/`, `vendor/`, `.git/`
- Files already in `/archive/` directories

---

## Rollback

If something goes wrong, rollback the migration:

```powershell
# Find the timestamp from initialization output
$timestamp = "20251015-133522"  # From "Rollback snapshot: .sbep-rollback-{timestamp}.json"

cd C:\Users\james\Desktop\Projects\SBEP_Core
.\SBEP-INIT.ps1 -ProjectPath C:\Path\To\Project -Rollback -Timestamp $timestamp
```

This will:
- Remove `/sds/` directory
- Remove SBEP-MANDATE.md and SBEP-INDEX.yaml
- Leave archived files in `/projects/archive/` (manually restore if needed)

---

## Common Issues & Solutions

### Issue: "SBEP_Core directory not found"

**Solution:** Run script from the correct location:
```powershell
cd C:\Users\james\Desktop\Projects\SBEP_Core
```

### Issue: "/sds/ already exists"

**Cause:** Project was already initialized  
**Solution:** 
- Skip re-initialization, or
- Manually delete `/sds/` first, or
- Use rollback then re-initialize

### Issue: "No obsolete files found"

**Behavior:** Normal for clean projects  
**Result:** No archive created, housekeeping skipped

### Issue: "Too many files archived"

**Cause:** Overly broad obsolete patterns  
**Solution:** 
1. Check `/projects/archive/{project}-housekeeping-{date}.zip`
2. Extract `MANIFEST.json` to see what was archived
3. If incorrect files archived, rollback and add `-SkipHousekeeping` flag:
   ```powershell
   .\SBEP-INIT.ps1 -ProjectPath C:\Path\To\Project -SkipHousekeeping
   ```

---

## Migration Priority Order

Suggested order for migrating existing projects:

### High Priority (Core Infrastructure)

1. **ASTRO** ✅ (Already completed as proof-of-concept)
2. **LCG (Local Call Generator)** - Active production system
3. **LSA (LSA Dashboard)** - Active production system

### Medium Priority (Active Development)

4. **google-ads-manager** - Google Ads integration
5. **ads_sync** - Ad synchronization system
6. **ads_sync_dashboard** - Dashboard for ad sync

### Low Priority (Reference/Archive)

7. **jamie_lcs-system** - Reference implementation
8. Other archived or deprecated projects

---

## Verification Checklist

After migration, verify:

- [ ] `/sds/` directory exists
- [ ] `sds/SBEP-MANDATE.md` exists and is customized
- [ ] `sds/SBEP-INDEX.yaml` exists
- [ ] Obsolete files archived (if any were found)
- [ ] Archive in `/projects/archive/{project}-housekeeping-{date}.zip`
- [ ] Rollback snapshot created: `.sbep-rollback-{timestamp}.json`
- [ ] Project README updated with SBEP notice (optional)
- [ ] Project CHANGELOG updated
- [ ] Agent compliance tested

---

## Next Steps After Migration

1. **Onboard Next Project:** Repeat process for remaining projects
2. **Monitor Agent Behavior:** Observe compliance over 1 week
3. **Refine Mandates:** Update project-specific rules based on agent patterns
4. **Share Knowledge:** Document successful patterns in project indexes

---

## Support

**For Help:**
1. Review `SBEP_Core/README.md` for detailed script usage
2. Check `/projects/SBEP-MANIFEST.md` for protocol details
3. Examine rollback snapshot JSON for troubleshooting
4. Review archived files in `/projects/archive/`

---

**Remember:** SBEP v2.0 is about empowering agents through documentation, not restricting them. The migration enforces structure that enables autonomy.

