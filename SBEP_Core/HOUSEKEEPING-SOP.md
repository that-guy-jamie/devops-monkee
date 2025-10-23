# Housekeeping Standard Operating Procedure (SOP)

**SBEP v2.0 Protocol**  
**Version:** 1.0  
**Last Updated:** October 18, 2025

---

## Purpose

This document defines the standard operating procedure for maintaining a clean, organized workspace in the Projects directory. Regular housekeeping ensures:
- Completed work is properly archived
- Temporary files don't clutter the workspace
- Active work is easy to find
- SBEP v2.0 compliance is maintained

---

## When to Perform Housekeeping

### Automatic Triggers (AI Agents)
Perform housekeeping when:
- ✅ A workorder is marked complete
- ✅ A major phase is finished (Phase 1, Phase 2, etc.)
- ✅ Testing phase is complete and implementation is verified
- ✅ Before committing major changes to git
- ✅ After creating many temporary output files

### Manual Triggers (Developers)
Run housekeeping when:
- Workspace feels cluttered
- Difficult to find active work
- Before starting a new project
- Monthly maintenance routine

### DO NOT Run Housekeeping When:
- ❌ In the middle of active development
- ❌ Testing is in progress (temp files may be needed)
- ❌ Before debugging failed operations
- ❌ When work status is unclear

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

### Instruction Files (NEVER MOVE)

**Location:** `/` (root only)

**Protected Files:**
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

**Skip Specific Phases:**
```powershell
# Skip workorder archival (just clean temp files)
.\SBEP_Core\Invoke-ProjectHousekeeping.ps1 -SkipWorkorders

# Skip temp file cleanup (just archive workorders)
.\SBEP_Core\Invoke-ProjectHousekeeping.ps1 -SkipTempFiles
```

**Verbose Output:**
```powershell
.\SBEP_Core\Invoke-ProjectHousekeeping.ps1 -Verbose
```

### What the Script Does

1. **Phase 1: Archive Completed Workorders**
   - Scans `/Workorders/` for files with "COMPLETE" or "SUMMARY" in name
   - Checks content for completion markers (✅, Status: Complete)
   - Moves completed workorders to `/Workorders/Archive/`
   - Archives associated CSV/data files
   - Checks project folders for completion documents

2. **Phase 2: Organize Temporary Files**
   - Moves `*.txt` temp files to `.tmp/`
   - Moves test output HTML files
   - Moves command scratch files
   - Preserves important logs (error, session, deploy)

3. **Phase 3: Organize Archive Structure**
   - Creates subdirectories in `/Archive/`
   - Organizes housekeeping zips
   - Organizes project archives
   - Maintains clean structure

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

### After Testing Phase

```markdown
1. Verify all tests passed
2. Confirm test outputs are no longer needed
3. Run housekeeping to move test outputs to .tmp/
4. Keep error logs if any tests failed
```

### Before Major Commits

```markdown
1. Run housekeeping to clean workspace
2. Review git status
3. Ensure only intentional changes are staged
4. Commit with clean workspace
```

### Template for Completion Notes

```markdown
## Housekeeping Performed

**Date:** [Date]
**Script:** Invoke-ProjectHousekeeping.ps1

**Summary:**
- Files archived: [count]
- Temp files organized: [count]
- Workspace status: Clean ✅
```

---

## Manual Housekeeping Checklist

If the script cannot be used, follow this manual checklist:

### Step 1: Archive Workorders
- [ ] Review `/Workorders/` for completed workorders
- [ ] Move completed workorders to `/Workorders/Archive/`
- [ ] Move associated CSV/data files
- [ ] Check project folders for completion documents
- [ ] Move to `{project}/archive/`

### Step 2: Organize Temp Files
- [ ] Review root directory for temp files
- [ ] Move to `.tmp/` folder
- [ ] Preserve error logs and important outputs

### Step 3: Clean Archive
- [ ] Ensure `/Archive/` subdirectories exist
- [ ] Organize housekeeping zips
- [ ] Organize project archives
- [ ] Remove empty legacy folders

### Step 4: Verify
- [ ] Workorders folder clean
- [ ] Root contains only instruction files
- [ ] Temp files organized
- [ ] Archive properly structured

---

## Troubleshooting

### "File is in use" Errors
- Close any editors or tools accessing the file
- Ensure no processes are reading the file
- Try again after closing applications

### Accidentally Moved Important File
- Check `/Archive/` subdirectories
- Check `.tmp/` folder
- Files are never deleted, only moved
- Restore from appropriate location

### Unsure if File is Complete
- Open the file and check for completion markers
- Look for "Status: Complete" or "✅ Complete"
- If unsure, leave in active location
- Better to review later than archive prematurely

### Script Errors
- Run with `-DryRun` first to preview
- Check error messages for specific issues
- Verify paths exist and are accessible
- Ensure no files are locked or in use

---

## Maintenance Schedule

### Weekly (Automated via Task Scheduler - Future)
- Run housekeeping script
- Archive completed workorders from past week
- Clean temporary files

### Monthly (Manual Review)
- Review archive structure
- Verify important docs not accidentally archived
- Clean up old temporary files (>30 days)
- Update this SOP if needed

### Quarterly (Deep Clean)
- Review all archived content
- Compress old archives
- Update documentation
- Audit SBEP compliance

---

## Related Documentation

- **Core Protocol:** `/SBEP-MANIFEST.md`
- **Project Organization:** `/PROJECT-ORGANIZATION-GUIDE.md`
- **Completion Report:** `/PROJECTS-ORGANIZATION-COMPLETE.md`
- **Script Location:** `/SBEP_Core/Invoke-ProjectHousekeeping.ps1`
- **SBEP Core Index:** `/SBEP_Core/SBEP-CORE-INDEX.yaml`

---

## Version History

- **v1.0** (2025-10-18): Initial SOP created
  - Defined housekeeping triggers
  - Created automated script
  - Established file organization rules
  - Set up archive structure

---

## Questions?

**For AI Agents:**
- Read `/SBEP-MANIFEST.md` for core protocol
- Check project-specific `sds/SBEP-MANDATE.md`
- Review this SOP before housekeeping operations

**For Developers:**
- This is an established pattern
- Script is safe and tested
- Always run `-DryRun` first if unsure
- Contact project maintainer with questions

---

**Remember:** Clean workspace = Clear mind = Better code ✨

