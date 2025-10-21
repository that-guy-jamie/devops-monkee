# audit-monkee - SBEP Mandate v2.0

**Project-Specific Operating Instructions for AI Agents**

---

## Project Context

**Project Name:** audit-monkee
**Primary Language/Stack:** Python, Markdown documentation
**Key Integrations:** GoHighLevel (GHL) API v2, Website auditing tools
**Current Phase:** Production-ready implementation with comprehensive auditing capabilities

**Implementation Status:** ✅ **CORE FUNCTIONALITY COMPLETE**
- All audit engines implemented (SEO, Tech Stack, Lighthouse)
- PDF report generation with professional formatting
- GHL API integration for notes, custom fields, and file uploads
- Headcore config generation with cryptographic signing
- Database schema and migrations complete
- Render deployment configuration ready

---

## Quick Start for Agents

### Required Reading (In Order)

1. **This file** (`sds/SBEP-MANDATE.md`) - Project-specific agent instructions
2. **`README.md`** - Project overview, architecture, quick start
3. **`sds/SBEP-INDEX.yaml`** - Complete documentation inventory
4. **`/projects/API-docs/`** - Centralized API documentation (GHL API)
5. **`docs/01-overview.md`** - Project overview and capabilities

### Project-Specific Documentation Locations

- **Architecture:** `docs/` (comprehensive documentation suite)
- **Operations:** `workorder-audit-monkey.md` (current tasks and priorities)
- **Integration Guides:** `docs/04-api.md` (API integration details)
- **Schemas:** `schemas/headcore-config.schema.json` (data structures)

---

## Project-Specific Rules

### 1. Technology Stack Awareness

**audit-monkee uses:**
- Python for core auditing functionality
- Markdown for documentation (comprehensive docs/ directory)
- JSON schemas for data validation
- GoHighLevel API v2 for CRM integration

**Before making changes:**
- Verify compatibility with GHL API v2 requirements
- Check existing documentation patterns in docs/
- Review JSON schema compatibility

### 2. Integration-Specific Documentation

**API Documentation Locations:**

**GoHighLevel API:** `/projects/API-docs/highlevel-api-docs-main/`
  - Use v2 API with PIT token authentication
  - Base URL: `https://services.leadconnectorhq.com`
  - Required header: `Version: 2021-07-28`
  - Never claim GHL endpoints are inaccessible without checking docs first

**Website Auditing APIs:**
  - Lighthouse/PageSpeed Insights for performance metrics
  - Custom web scraping for tech stack detection
  - Schema.org detection and validation

### 3. Deployment & Operations

**Deployment Method:** GoHighLevel Marketplace app installation
**Hosting:** GoHighLevel platform (SaaS)
**CI/CD:** Manual deployment via GHL marketplace

**Critical Operations Files:**
- `docs/10-deployment.md` - Deployment procedures
- `docs/02-ghl-marketplace.md` - Marketplace listing requirements
- `workorder-audit-monkey.md` - Current development tasks

### 4. Testing & Validation

**Before Committing Changes:**
- Validate JSON schemas in schemas/
- Test GHL API integration patterns
- Update relevant documentation in docs/
- Verify marketplace listing requirements

**Testing Approach:**
- Unit tests for auditing functions
- Integration tests with GHL API
- Documentation validation (schema compliance)

### 5. Documentation Maintenance

**When Adding Features:**
- Update `docs/` with comprehensive documentation
- Update JSON schemas for new data structures
- Update marketplace listing documentation
- Add inline code comments for complex logic

**When Deprecating Features:**
- Move obsolete files to `archive/` (don't delete)
- Update documentation references
- Add deprecation notice with migration path

---

## Common Tasks Reference

### Task: GHL API Integration
1. Check `/projects/API-docs/highlevel-api-docs-main/` for endpoints
2. Review `docs/04-api.md` for integration patterns
3. Implement with error handling and retries
4. Document in `docs/04-api.md`

### Task: Website Auditing
1. Read `docs/01-overview.md` for capability requirements
2. Review `docs/08-reporting.md` for output formats
3. Implement following existing patterns in docs/
4. Validate against JSON schemas

### Task: Documentation Update
1. Follow existing documentation structure in docs/
2. Update README.md if user-facing changes
3. Update schemas for data structure changes
4. Cross-reference related documentation

---

## Escalation Path

**If Documentation is Insufficient:**
1. Search all project markdown files in docs/ for related info
2. Check GHL API documentation in `/projects/API-docs/`
3. Review similar implementations in other `/projects/` directories
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
- Hardcoded GHL API credentials or endpoints
- Undocumented API integrations
- Incomplete audit reporting (missing required fields)
- Inconsistent documentation formatting

**Prefer:**
- Environment-based configuration
- Comprehensive API documentation
- Complete audit result sets
- Consistent markdown formatting across docs/

---

## Success Metrics

Agent performance is measured by:
- Documentation consulted before asking questions
- Methods attempted before requesting help
- Proper JSON schema compliance
- GHL API integration success rate
- Documentation quality and completeness

---

## Version History

- **v2.0** (2025-10-21): SBEP v2.0 compliance, GHL API integration focus
- **v1.0** (Project init): Initial project setup

---

**Remember:** This project's documentation is your source of truth. Read it, trust it, use it.
