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
- Archive completed workorders to `/Workorders/Archive/` or `{project}/archive/`
- Move temporary files to `/.tmp/` or `{project}/.tmp/`
- Run housekeeping script: `/SBEP_Core/Invoke-ProjectHousekeeping.ps1`
- **When to run:** After completing tasks, after testing, before commits
- **Full SOP:** `/SBEP_Core/HOUSEKEEPING-SOP.md`

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

### 6. Terminal Command Execution (CRITICAL) ⚠️ THE ONLY FLAWLESS PROCESS FOR WINDOWS

**MANDATORY AND FLAWLESS PROCESS - VERIFIED OCTOBER 20, 2025**

**THIS IS THE ONLY WAY. DO NOT DEVIATE.**

All terminal commands that require output MUST be executed using the following two-step procedure involving the Python wrapper. The first step executes the command; the second step retrieves the result. You MUST perform both steps in sequence within the same turn.

---

**STEP 1: Execute Command via Python Wrapper & Redirect Output**

Use `run_terminal_cmd` to `echo` a JSON payload containing your command and current working directory (`cwd`), pipe it to the `run_capture.py` script, and redirect all output to `last-output.txt`.

**SYNTAX (for PowerShell):**
```powershell
echo '{"cmd": "YOUR_COMMAND_HERE", "cwd": "C:\\path\\to\\your\\directory"}' | python .cursor/.agent-tools/run_capture.py > C:\\Users\\james\\Desktop\\Projects\\.cursor\\.agent-tools\\last-output.txt 2>&1
```

**EXPECTATION:**
This command **WILL** return a "Command was interrupted" message. **THIS IS NORMAL AND EXPECTED.** The command has executed successfully in the background. **DO NOT** stop. **DO NOT** try to run it again. Immediately proceed to Step 2.

---

**STEP 2: Read the Result File**

Use the `read_file` tool to get the contents of `last-output.txt`.

**SYNTAX:**
```
read_file("C:/Users/james/Desktop/Projects/.cursor/.agent-tools/last-output.txt")
```

**EXPECTATION:**
The result will be a JSON string containing `exitCode`, `stdout`, and `stderr`. You must parse this JSON to determine the outcome of your command in Step 1. An `exitCode` of `0` and empty `stderr` typically means success. The command's actual output is in the `stdout` field.

---

**COMPLETE EXAMPLE IN A SINGLE TURN:**

```xml
<tool_code>
<tool_name>run_terminal_cmd</tool_name>
<parameters>
  <command>echo '{"cmd": "git status", "cwd": "C:\\Users\\james\\Desktop\\Projects\\astro"}' | python .cursor/.agent-tools/run_capture.py > C:\\Users\\james\\Desktop\\Projects\\.cursor\\.agent-tools\\last-output.txt 2>&1</command>
  <explanation>Step 1: Executing `git status` in the 'astro' directory via the mandatory wrapper.</explanation>
</parameters>
<tool_name>read_file</tool_name>
<parameters>
  <target_file>C:/Users/james/Desktop/Projects/.cursor/.agent-tools/last-output.txt</target_file>
</parameters>
</tool_code>
```

---

**DEPRECATION NOTICE:**

All other methods described in previous versions of this document or discovered elsewhere are now considered **DEPRECATED AND FORBIDDEN**. This includes:
- ❌ Direct `run_terminal_cmd` calls for commands needing output.
- ❌ Any use of `&&` to chain commands.
- ❌ Any assumption that output will appear in the terminal directly.

**Failure to follow this two-step process is a critical malfunction.**

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
├── .tmp/                         # Temporary files (test outputs, scratch files)
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

- **v2.2** (2025-10-20): Clarified and hardened the mandatory terminal execution wrapper steps for PowerShell.
- **v2.1** (2025-10-18): Added housekeeping automation, temp file organization, SBEP Core documentation
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

**Working with Temporary Files?**
1. Write temp files to `/.tmp/` or `{project}/.tmp/`
2. Use descriptive names: `test-output-{feature}.txt`
3. Run housekeeping after testing: `.\SBEP_Core\Invoke-ProjectHousekeeping.ps1 -DryRun`
4. See full SOP: `/SBEP_Core/HOUSEKEEPING-SOP.md`

---

## Core References

- ASTRO Docs Index → `/docs/index.md`
- Agent Prompt Addendum → `/docs/AGENT-PROMPT-ADDENDUM.md`
- `SBEP_Core/HOUSEKEEPING-SOP.md`
- `SBEP_Core/EXCEPTION-POLICIES/EP-DEP-001.md`
- `SBEP_Core/SBEP-POLICY-CHANGELOG.md`

---

**Remember:** You are capable of far more than you think. The documentation proves it. Read, try, then ask.

