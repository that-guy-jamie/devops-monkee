# {PROJECT_NAME} - SBEP Mandate v2.2

**Project-Specific Operating Instructions for AI Agents**

---

## Project Context

**Project Name:** {PROJECT_NAME}  
**Primary Language/Stack:** {TECH_STACK}  
**Key Integrations:** {INTEGRATIONS}  
**Current Phase:** {PHASE}

---

## Quick Start for Agents

### Required Reading (In Order)

1. **This file** (`sds/SBEP-MANDATE.md`) - Project-specific agent instructions
2. **`README.md`** - Project overview, architecture, quick start
3. **`sds/SBEP-INDEX.yaml`** - Complete documentation inventory
4. **`/projects/API-docs/`** - Centralized API documentation (as needed)
5. **`CHANGELOG.md`** - Recent changes and current state

### Project-Specific Documentation Locations

- **Architecture:** `docs/architecture/` or `docs/{PROJECT}-ARCHITECTURE.md`
- **Operations:** `ops/` (deployment scripts, tasks, runbooks)
- **Integration Guides:** `docs-reference/` or `docs/integrations/`
- **Work Orders:** `workorders/` (current tasks, priorities, completion status)

---

## Project-Specific Rules

### 1. Technology Stack Awareness

**{PROJECT_NAME} uses:**
- {LIST_TECH_STACK_ITEMS}
- {DATABASE_INFO}
- {HOSTING_INFO}

**Before making changes:**
- Verify compatibility with existing dependencies
- Check `package.json` / `composer.json` / `requirements.txt`
- Review recent CHANGELOG entries for context

### 2. Integration-Specific Documentation

**API Documentation Locations:**

{EXAMPLE_FOR_GHL_PROJECT:}
- **GoHighLevel API:** `/projects/API-docs/highlevel-api-docs-main/`
  - Use v2 API with PIT token authentication
  - Base URL: `https://services.leadconnectorhq.com`
  - Required header: `Version: 2021-07-28`
  - Never claim GHL endpoints are inaccessible without checking docs first

{EXAMPLE_FOR_GOOGLE_ADS:}
- **Google Ads API:** `/projects/API-docs/google-ads-api/`
  - Use v21 API
  - OAuth 2.0 authentication with refresh tokens
  - Check rate limits and batch request patterns

### 3. Deployment & Operations

**Deployment Method:** {DEPLOYMENT_METHOD}  
**Hosting:** {HOSTING_PROVIDER}  
**CI/CD:** {CI_CD_INFO}

**Deployment Scripts:**
- Located in: `ops/` or `ops/tasks/`
- Always use scripts, never manual deployment
- Verify with `--dry-run` or test environment first

**Critical Operations Files:**
- `ops/README.md` - Deployment procedures
- `ops/tasks/` - Scheduled automation
- `ops/deploy-*.{sh|ps1}` - Deployment automation

### 4. Testing & Validation

**Before Committing Changes:**
- Run linter if configured
- Test in development/staging environment
- Update relevant tests
- Update CHANGELOG.md

**Testing Approach:**
{PROJECT_TESTING_APPROACH}

### 5. Documentation Maintenance

**When Adding Features:**
- Update `README.md` if user-facing
- Update `CHANGELOG.md` (follow existing format)
- Update `sds/SBEP-INDEX.yaml` if adding new docs
- Add inline code comments for complex logic

**When Deprecating Features:**
- Move obsolete files to `archive/` (don't delete)
- Update documentation references
- Add deprecation notice with migration path

---

## Common Tasks Reference

### Task: API Integration
1. Check `/projects/API-docs/{platform}/` for endpoints
2. Review similar patterns in other `/projects/` directories
3. Implement with error handling and retries
4. Document in `docs/integrations/`

### Task: Deployment
1. Read `ops/README.md`
2. Use existing deployment scripts
3. Never deploy manually
4. Verify success, update CHANGELOG

### Task: Bug Fix
1. Search CHANGELOG and git history for context
2. Check `workorders/` for related tasks
3. Implement fix with tests
4. Document root cause and solution

### Task: New Feature
1. Check if similar feature exists in other projects
2. Design following project architecture patterns
3. Create work order document if complex
4. Implement with documentation

---

## Escalation Path

**If Documentation is Insufficient:**
1. Search all project markdown files for related info
2. Check other `/projects/` for similar implementations
3. Review git history for relevant changes
4. THEN ask user with evidence of search performed

**When Asking for Help:**
Provide:
- Files consulted (with paths)
- Methods attempted (commands/code)
- Error messages (full output)
- Why each approach failed

---

## Project-Specific Anti-Patterns

**Avoid:**
{PROJECT_SPECIFIC_ANTIPATTERNS}

**Prefer:**
{PROJECT_SPECIFIC_BEST_PRACTICES}

---

## Success Metrics

Agent performance is measured by:
- Documentation consulted before asking questions
- Methods attempted before requesting help
- Proper rollback plans for changes
- CHANGELOG updates
- Code quality and maintainability

---

## Version History

- **v2.0** (2025-10-15): SBEP v2.0 compliance, housekeeping policy
- **v1.0** (Project init): Initial project setup

---

**Remember:** This project's documentation is your source of truth. Read it, trust it, use it.

