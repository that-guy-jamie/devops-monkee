# Source-Bound Execution Protocol (SBEP) v2.0

**Global Operating Mandate for All AI Agents**

---

## Purpose

This manifest establishes the **SBEP v2.0 standard** - a documentation-first operating protocol that empowers AI agents with autonomy while enforcing accountability, safety, and best practices across all projects in this workspace.

**Core Principle:** Read The F***ing Manual (RTFM) before attempting any task.

---

## Agent Operating Protocol

### 1. Initial Orientation (Read This First)

When you begin work in `/projects/` or any subdirectory:

1. **Read this manifest** (you're doing it now - good!)
2. **Identify the project** you're working on
3. **Navigate to** `{project}/sds/SBEP-MANDATE.md` and read the project-specific instructions
4. **Review** `{project}/sds/SBEP-INDEX.yaml` to understand available documentation
5. **ONLY THEN** begin task execution

### 2. Documentation-First Approach (RTFM Mandate)

Before claiming you cannot perform a task or asking the user for help:

**STEP 1: Check Project Documentation**
- Read `{project}/sds/SBEP-INDEX.yaml` for relevant docs
- Review `{project}/README.md`, `{project}/CHANGELOG.md`, `{project}/docs/`
- Check `{project}/ops/` for deployment and operational procedures

**STEP 2: Check Centralized API Documentation**
- **Location:** `C:\Users\james\Desktop\Projects\API-docs/`
- **Contains:** Full, authoritative API documentation for:
  - GoHighLevel (GHL) API v1 & v2
  - Google Ads API v21
  - Beaver Builder
  - JobNimbus
  - And more...
- **Rule:** If functionality is documented in `API-docs/`, you ARE capable of implementing it

**STEP 3: Cross-Project Learning**
- Review similar implementations in other `/projects/` directories
- ASTRO, LCG (Local Call Generator), LSA (LSA Dashboard), google-ads-manager
- Reuse proven patterns and solutions

**STEP 4: Attempt Multiple Approaches**
- Try different tools, commands, or API endpoints
- Use available environmental capabilities (WP-CLI, PowerShell, Node.js, etc.)
- Exhaust alternatives before requesting manual intervention

**STEP 5: Report with Evidence (If Still Stuck)**
When asking for help, you MUST provide:
- Documentation consulted (cite file paths)
- Methods attempted (exact commands/code)
- Error messages received (full output)
- Why each approach failed

### 3. Autonomy with Accountability

**You Have Permission To:**
- Create, modify, and organize files
- Execute scripts and commands
- Install dependencies
- Configure systems
- Make architectural decisions aligned with best practices

**You Must:**
- Document changes in project `CHANGELOG.md`
- Create rollback plans for destructive operations
- Use dry-run modes when available
- Cite sources when implementing patterns from documentation

**You Must NOT:**
- Delete files (archive to `/projects/archive/{project}-housekeeping-{date}.zip` instead)
- Use quick fixes over proper solutions
- Skip reading documentation
- Claim inability without evidence of attempts

### 4. Safety & Rollback Requirements

**All Write Operations Require:**
- Rollback plan documented before execution
- Backup of affected files/data
- Validation step after changes
- Entry in project CHANGELOG

**Housekeeping Policy:**
- Never delete obsolete files
- Move to `/projects/archive/` organized by project
- Compress per-project: `{project}-housekeeping-{MMDDYYYY}.zip`
- Include manifest listing archived files and reasons

### 5. Best Practices Over Quick Fixes

**Always Choose:**
- Standards-compliant approaches
- Refactoring over patching
- Long-term maintainability
- Documented, reproducible solutions

**Avoid:**
- Hardcoded values
- Temporary workarounds
- Undocumented "magic"
- Non-portable solutions

### 6. Terminal Command Execution (CRITICAL)

**The Problem:**
Cursor terminal output is not always captured or visible to the agent, making debugging impossible.

**The Solution (MANDATORY FOR ALL COMMANDS):**

Always redirect terminal commands to a capture file:

```
COMMAND > C:\Users\james\Desktop\Projects\.cursor\.agent-tools\last-output.txt 2>&1 && type C:\Users\james\Desktop\Projects\.cursor\.agent-tools\last-output.txt
```

If `type` fails to display, immediately follow with:
```
read_file("C:/Users/james/Desktop/Projects/.cursor/.agent-tools/last-output.txt")
```

**Key Points:**
- `> file` redirects stdout
- `2>&1` also captures stderr (CRITICAL for errors)
- `&& type file` displays the output
- If display fails, use `read_file` tool as backup
- Use the same file (`last-output.txt`) - it overwrites each time

**Windows Command Prompt "q" Prefix Bug:**
Commands may randomly get prefixed with "q" causing failures:
```cmd
qgit status  # 'qgit' is not recognized
```

**Workaround:**
```cmd
cd .  # Absorb the stray character
git status  # Actual command works
```

**Examples:**

```cmd
# Simple command with buffer
cd . && poetry run python script.py > C:\Users\james\Desktop\Projects\.cursor\.agent-tools\last-output.txt 2>&1 && type C:\Users\james\Desktop\Projects\.cursor\.agent-tools\last-output.txt

# Long-running command (run, then read separately)
cd . && poetry run python long_script.py > C:\Users\james\Desktop\Projects\.cursor\.agent-tools\last-output.txt 2>&1
type C:\Users\james\Desktop\Projects\.cursor\.agent-tools\last-output.txt

# If type fails
read_file("C:/Users/james/Desktop/Projects/.cursor/.agent-tools/last-output.txt")
```

**Consequences of Not Following:**
- Agent cannot see errors
- Debugging becomes impossible
- User must manually copy/paste output
- Wastes time and breaks workflow

**Full Documentation:**
`C:\Users\james\Desktop\Projects\.cursor\AGENT-TERMINAL-GUIDE.md`

### 7. Workorders Management

**Workorders Folder Structure:**
- **Global:** `/projects/Workorders/` - Cross-project work orders and planning
- **Project-Level:** `{project}/workorders/` - Project-specific tasks and tracking

**Workorder Lifecycle:**
1. **Active Workorders** - Stay in main `workorders/` folder
2. **Document Progress** - Update workorder with status, blockers, completion notes
3. **Mark Complete** - Add completion date and summary to workorder
4. **Archive When Complete** - Move to `workorders/Completed Workorders/` or project archive

**Workorder Completion Checklist:**
- [ ] All tasks in workorder completed
- [ ] Relevant code/docs updated
- [ ] CHANGELOG updated (if applicable)
- [ ] Completion summary added to workorder
- [ ] Referenced in related documentation
- [ ] THEN move to archive

**Archive Location:**
- **Project-specific:** `{project}/workorders/Completed Workorders/`
- **Global:** `/projects/Workorders/Completed Workorders/`
- **Long-term:** `/projects/archive/{project}-workorders-{date}.zip` (for old completed work)

**Before Archiving:**
- Verify workorder shows completion date
- Ensure deliverables are documented
- Check that no active references point to the workorder
- Never archive incomplete workorders

### 7. Cross-Project Knowledge Sharing

**Learn From:**
- ASTRO: GHL integration patterns, WordPress deployment automation, SEO plugin architecture
- LCG: API orchestration, webhook handling, lead generation workflows
- LSA: Multi-client dashboard patterns, data quality metrics, scheduled audits
- google-ads-manager: Google Ads API implementation, campaign management

**Document Innovations:**
- Add new patterns to project `/docs/patterns/`
- Update `SBEP-INDEX.yaml` with new reference docs
- Create examples for future reuse

---

## Project Structure Standards

Every SBEP-compliant project contains:

```
{project}/
├── sds/                          # Source Documentation Store
│   ├── SBEP-MANDATE.md          # Project-specific agent instructions
│   └── SBEP-INDEX.yaml          # Documentation inventory
├── README.md                     # Project overview & quick start
├── CHANGELOG.md                  # Change history
├── docs/                         # Architecture, guides, patterns
├── ops/                          # Deployment, scripts, tasks
├── scripts/                      # Automation scripts
└── archive/                      # Deprecated files (local archive)
```

---

## Enforcement

**Violations of SBEP Protocol:**
- Claiming inability without citing documentation consulted
- Deleting files instead of archiving
- Asking for help without showing attempted methods
- Implementing quick fixes instead of proper solutions

**When Violations Occur:**
The user will remind you of this protocol and ask you to retry with compliance.

---

## Version History

- **v2.0** (2025-10-15): Global rollout with housekeeping policy, centralized API docs, cross-project learning
- **v1.0** (Concept): Initial RTFM-first approach

---

## Quick Reference

**Starting Work?**
1. Read `/projects/SBEP-MANIFEST.md` (this file)
2. Read `{project}/sds/SBEP-MANDATE.md`
3. Review `{project}/sds/SBEP-INDEX.yaml`
4. Check `/projects/API-docs/` for API capabilities

**Need Help?**
1. Cite docs consulted
2. Show methods attempted
3. Provide error messages
4. Explain why approaches failed

**Making Changes?**
1. Create rollback plan
2. Update CHANGELOG
3. Archive obsolete files (don't delete)
4. Validate results

---

**Remember:** You are capable of far more than you think. The documentation proves it. Read, try, then ask.

