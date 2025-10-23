# SBEP Housekeeping Standard Operating Procedure

## Overview

This document defines the standard housekeeping practices for SBEP-compliant projects to maintain clean, organized, and efficient workspaces.

---

## Principles
- Prefer **deprecation workflow** over hard bans.
- Optimize for safety, traceability, and repo performance.

## Retention & Archive
- Moves to `/archive` are allowed with an **index entry** (see Archive Index below).
- Default retention windows (override per-project via `housekeeping.config.json`):
  - `/archive/docs`: 180 days
  - `/archive/builds`: 90 days
  - `/archive/artifacts`: 90 days
- After retention, items may be purged by `ops/scripts/sbep-retention-cleaner.py` (dry-run by default).

## Deletion Workflow
Deletion is allowed **only** via deprecation workflow:
1. Ticket with impact note.
2. Backup/export or Git tag cut.
3. Migration applied (if applicable).
4. Reviewer sign-off.
5. Purge via cleaner with `--apply` flag.

## Link Integrity
Before moving/purging any docs, run:
```
node ops/scripts/sbep-verify-links.js --fix
```
CI will block merges if broken internal links remain.

## Instruction Files
Instructional docs may be moved **when** references are auto-updated by the link verifier.
Do not move without running the verifier and committing its changes.

## Work-in-Progress Guard
Housekeeping refuses to run if any `workorders/status.json` item is `"state":"in_progress"`.
Use `--force` to override (logged).

## Archive Index
Maintain `/archive/archive-index.json` entries for moved items:
```json
{ "path": "docs/old.md", "new_path": "archive/docs/old.md", "moved_at": "2025-10-20" }
```

---

## File Organization Rules

### Temporary Files

**Location:** `/.tmp/` (root) or `{project}/.tmp/` (project-specific)

**What Goes Here:**
- Output files from testing: `output.txt`, `test-output.html`
- Directory listings: `dir.txt`, `cortex-dir.txt`
- Scratch/command files: `sftp-commands.txt`
- Temporary logs (non-error logs)
- `.log` files from testing
- Any file ending in `-temp.txt` or `.tmp`

**What STAYS in Root/Project:**
- Error logs (needed for debugging)
- Session summaries
- Deployment logs
- Important output from production runs

### Workorder Archives

**Location:** `/Workorders/Archive/` or `{project}/archive/`

**What Goes Here:**
- Workorders with "COMPLETE" in filename or content
- Completion summary documents (`*-COMPLETE.md`, `*-SUMMARY.md`)
- CSV/data files from completed campaigns
- Status documents showing completed phases

**What STAYS Active:**
- Workorders in progress
- Ready-to-execute workorders (not yet started)
- Reference documents still in use

### Archive Structure

**Location:** `/Archive/`

**Subdirectories:**
```
Archive/
├── workorders/     # Completed global workorder archives
├── projects/       # Old project zips and archives
├── housekeeping/   # Housekeeping operation archives
└── scripts/        # Deprecated/outdated scripts
```

### Protected Files

**Location:** `/` (root only)

**Files requiring deprecation workflow:**
- `SBEP-MANIFEST.md` - Core protocol
- `DOCUMENTATION-INDEX.md` - Doc reference
- `README.md` - Project overview
- `LSA-*.md` - System guides
- `PROJECT-*.md` - Integration notes
- `AGENT-*.md` - Agent instructions
- All `*-COMPLETE.md` status documents
- Configuration files (`.env`, `.cursorrules`, etc.)

---

## Housekeeping Script

### Location
`/SBEP_Core/Invoke-ProjectHousekeeping.ps1`

### Basic Usage

**Dry Run (recommended first):**
```powershell
cd C:\Users\james\Desktop\Projects
.\SBEP_Core\Invoke-ProjectHousekeeping.ps1 -DryRun
```

**Actual Execution:**
```powershell
.\SBEP_Core\Invoke-ProjectHousekeeping.ps1
```

### What the Script Does

1. **Phase 1: Archive Completed Workorders**
   - Scans `/Workorders/` for files with "COMPLETE" or "SUMMARY" in name
   - Checks content for completion markers (✅, Status: Complete)
   - Moves completed workorders to `/Workorders/Archive/`
   - Archives associated CSV/data files

2. **Phase 2: Organize Temporary Files**
   - Moves eligible temp files to `.tmp/`
   - Preserves important logs (error, session, deploy)
   - Respects retention windows

3. **Phase 3: Apply Retention Policy**
   - Reviews archived items against retention windows
   - Flags items eligible for purging (dry-run by default)

---

## AI Agent Protocol

### After Completing a Task

```markdown
1. Mark workorder as complete (add "Status: ✅ Complete" to document)
2. Create completion summary if needed
3. Run housekeeping script with -DryRun first
4. Review what will be moved
5. Run actual housekeeping
6. Verify workspace is clean
7. Document housekeeping in completion notes
```

### Before Deleting Files

```markdown
1. Follow the 5-step deprecation workflow
2. Create ticket with impact assessment
3. Create backup or git tag
4. Apply any necessary migrations
5. Get reviewer sign-off
6. Execute deletion with explicit --apply flag
```

### Template for Completion Notes

```markdown
## Housekeeping Performed

**Date:** [Date]
**Script:** Invoke-ProjectHousekeeping.ps1

**Summary:**
- Files archived: [count]
- Temp files organized: [count] 
- Retention policy applied: [yes/no]
- Workspace status: Clean ✅
```

---

## Troubleshooting

### "File is in use" Errors
- Close any editors or tools accessing the file
- Ensure no processes are reading the file
- Try again after closing applications

### Accidentally Moved Important File
- Check `/Archive/` subdirectories
- Check `.tmp/` folder
- Check `/archive/archive-index.json` for move history
- Files are moved, not deleted - restore from appropriate location

### Link Verification Failures
- Run `node ops/scripts/sbep-verify-links.js --fix`
- Review broken links in CI output
- Update references before completing moves

---

## Version History

- **v2.1** (2025-10-20): Added deprecation workflow, retention windows, link integrity checks
- **v1.0** (2025-10-18): Initial SOP created

---

**Remember:** Structured processes prevent data loss and maintain system integrity ✨