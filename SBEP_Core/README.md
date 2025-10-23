# SBEP v2.0 Core Templates & Initialization

**Source-Bound Execution Protocol Implementation Kit**

---

## Purpose

This directory contains the core templates and initialization script for implementing SBEP v2.0 across all projects in the `/projects/` workspace.

**SBEP v2.0** enforces a documentation-first approach that empowers AI agents with autonomy while maintaining accountability, safety, and best practices.

---

## Contents

| File | Purpose |
|------|---------|
| `SBEP-INIT.ps1` | PowerShell initialization script for onboarding projects |
| `SBEP-MANDATE-TEMPLATE.md` | Project-specific agent operating instructions template |
| `SBEP-INDEX-TEMPLATE.yaml` | Documentation inventory structure template |
| `README.md` | This file - usage guide |
| `.backups/original/` | Backup storage for template originals |

---

## Quick Start

### Initialize a New Project

```powershell
cd C:\Users\james\Desktop\Projects\SBEP_Core
.\SBEP-INIT.ps1 -ProjectPath C:\Users\james\Desktop\Projects\{project-name}
```

**Example:**
```powershell
.\SBEP-INIT.ps1 -ProjectPath C:\Users\james\Desktop\Projects\astro
```

### What the Script Does

1. **Creates `/sds/` directory** in the project
2. **Copies and customizes** SBEP-MANDATE.md template
3. **Generates** SBEP-INDEX.yaml by scanning project docs
4. **Identifies obsolete files** (cheatsheets, .old, .bak, etc.)
5. **Archives obsolete files** to `/projects/archive/{project}-housekeeping-{date}.zip`
6. **Creates rollback snapshot** for safety

### Skip Housekeeping (Optional)

If you want to skip the archival step:

```powershell
.\SBEP-INIT.ps1 -ProjectPath C:\Path\To\Project -SkipHousekeeping
```

### Rollback an Initialization

If something goes wrong, rollback using the timestamp from initialization:

```powershell
.\SBEP-INIT.ps1 -ProjectPath C:\Path\To\Project -Rollback -Timestamp 20251015-143022
```

---

## After Initialization

### 1. Customize the Mandate

Edit `{project}/sds/SBEP-MANDATE.md`:

- Fill in project-specific tech stack details
- Add integration-specific documentation locations
- Document project-specific anti-patterns and best practices
- Add any custom rules or escalation paths

### 2. Curate the Index

Edit `{project}/sds/SBEP-INDEX.yaml`:

- Set `exists: true` for files that were found during scan
- Add project-specific documentation not covered by template
- Update descriptions to match actual content
- Add cross-project pattern references

### 3. Test Agent Compliance

Start a new agent session and verify:

- Agent reads `/projects/SBEP-MANIFEST.md` on startup
- Agent reads `{project}/sds/SBEP-MANDATE.md` when working on project
- Agent checks SBEP-INDEX.yaml before claiming docs don't exist
- Agent cites documentation when implementing features

---

## Housekeeping & Archival Policy

### Obsolete File Patterns

The init script automatically identifies and archives:

- `*cheatsheet*.md` - Old API cheatsheets (replaced by `/projects/API-docs/`)
- `*deprecated*.md` - Explicitly deprecated files
- `*old*.md`, `*.old` - Old versions
- `*.bak`, `*.tmp` - Backup and temporary files
- `*-old.*` - Files with -old suffix

### Archive Structure

Archived files are stored as:

```
/projects/archive/{project}-housekeeping-{MMDDYYYY}.zip
  ├── MANIFEST.json (metadata about archived files)
  ├── {original-relative-path}/
  │   └── file1.md
  └── {another-path}/
      └── file2.md
```

### Archive Manifest

Each archive contains a `MANIFEST.json`:

```json
{
  "project": "astro",
  "archive_date": "2025-10-15 14:30:22",
  "archived_by": "SBEP-INIT.ps1",
  "reason": "SBEP v2.0 housekeeping",
  "files": [
    {
      "original_path": "docs/api-cheatsheet.md",
      "size_bytes": 4096,
      "last_modified": "2025-09-12 10:15:00"
    }
  ]
}
```

---

## Project Requirements

### Prerequisites

- **PowerShell** 5.1 or higher (Windows) or PowerShell Core (cross-platform)
- **Write access** to project directory
- **SBEP_Core** must exist at `/projects/SBEP_Core/`
- **Global manifest** must exist at `/projects/SBEP-MANIFEST.md`

### Project Structure Assumptions

The script expects standard project structures:

- `README.md` at project root
- `/docs/` for documentation
- `/ops/` for operations/deployment
- `/workorders/` for task tracking
- `/scripts/` for automation

Non-standard structures will work but may require manual index curation.

---

## Rollback Safety

### Automatic Rollback Files

Every initialization creates a rollback file:

```
{project}/.sbep-rollback-{timestamp}.json
```

This contains:
- Created directories
- Created files
- Archived files (for restoration if needed)

### Manual Rollback

If automated rollback fails:

1. Delete `/sds/` directory
2. Restore files from `/projects/archive/{project}-housekeeping-{date}.zip`
3. Delete `.sbep-rollback-*.json` files

---

## Troubleshooting

### Error: "SBEP_Core directory not found"

**Cause:** Script executed from wrong directory  
**Solution:** `cd C:\Users\james\Desktop\Projects\SBEP_Core` before running

### Error: "Project path does not exist"

**Cause:** Invalid project path  
**Solution:** Verify path with `Test-Path C:\Path\To\Project`

### `/sds/` already exists

**Behavior:** Script skips creation, does not overwrite  
**Solution:** If re-initializing, manually delete `/sds/` first or archive it

### No obsolete files found

**Behavior:** Housekeeping skipped, no archive created  
**Result:** This is normal for clean projects

---

## Version History

- **v2.0** (2025-10-15): Full implementation with housekeeping, archival, rollback
- **v1.0** (Concept): Initial RTFM-first approach

---

## Support

For questions or issues:

1. Review `/projects/SBEP-MANIFEST.md` for protocol
2. Check project-specific `{project}/sds/SBEP-MANDATE.md`
3. Examine `{project}/sds/SBEP-INDEX.yaml` for doc locations
4. Consult `/projects/API-docs/` for API capabilities

---

**Remember:** SBEP v2.0 empowers agents to work autonomously by ensuring documentation is the source of truth.

