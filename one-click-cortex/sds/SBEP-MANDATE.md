# one-click-cortex - SBEP Mandate v2.2

**Project-Specific Operating Instructions for AI Agents**

---

## Project Context

**Project Name:** one-click-cortex  
**Primary Language/Stack:** WordPress, PHP 8.0+, Bash/PowerShell deployment scripts  
**Key Integrations:** WP Engine hosting, WP-CLI, SSH/SFTP  
**Current Phase:** Production-ready deployment framework

---

## Quick Start for Agents

### Required Reading (In Order)

1. **This file** (`sds/SBEP-MANDATE.md`) - Project-specific agent instructions
2. **`README.md`** - Project overview, deployment framework
3. **`sds/SBEP-INDEX.yaml`** - Complete documentation inventory
4. **`CHANGELOG.md`** - Recent changes and version history
5. **`QUICK_START_OVERVIEW.md`** - High-level deployment process

### Project-Specific Documentation Locations

- **Deployment Guides:** `docs/REPLICATION_GUIDE.md`, `docs/TESTING_VALIDATION.md`
- **Security:** `docs/SECURITY_NOTES.md`
- **Prerequisites:** `docs/PREREQS_CHECKLIST.md`
- **Plugin Documentation:** `plugin/headcore/README.md`, `plugin/headcore/DEPLOYMENT.md`
- **Environment Management:** `env/README.md`
- **Analysis Reports:** `reports/route-inventory.json`, `reports/wp-environment.json`

---

## Project-Specific Rules

### 1. Technology Stack Awareness

**one-click-cortex uses:**
- **WordPress:** 6.4+ (target deployment environment)
- **PHP:** 8.0+ minimum
- **headcore plugin:** Located in `/plugin/headcore/`
- **WP Engine:** SSH gateway, SFTP, mu-plugins support
- **WP-CLI:** All deployments use WP-CLI commands
- **Theme:** Astra Pro + Beaver Builder (typical client setup)
- **Deployment:** Bash scripts (Linux/Mac), PowerShell fallback (Windows)

**Before making changes:**
- This is a **documentation + deployment framework project**
- Source code lives in `/plugin/headcore/` - this is the deployable package
- Never modify files in the ASTRO project directory
- Each deployment target gets its own `.env` file in `/env/`

### 2. Integration-Specific Documentation

**Source Code Location:**
- Deployable plugin: `/plugin/headcore/` (standalone, self-contained)
- **DO NOT** reference `astro/wordpress-integration/headcore/` - that's a separate project
- This package must be fully portable and independent

**WP Engine Specifics:**
- SSH key authentication required (no password-based SSH)
- SFTP may require password even with SSH key configured
- Port 2222 for SFTP, Port 22 for SSH
- Custom directories: `/wp-content/one-click-seo/config/`
- MU-plugins directory: `/wp-content/mu-plugins/`

### 3. Deployment & Operations

**Deployment Method:** SSH + WP-CLI (primary), SFTP fallback for file upload  
**Hosting:** WP Engine (managed WordPress)  
**CI/CD:** Not yet implemented (planned)

**Deployment Scripts:**
- Located in: `ops/scripts/`
- Environment configs: `env/{sitename}.env`
- Never hardcode credentials
- Always use dry-run testing first
- Create backups before deployment

**Critical Operations Files:**
- `env/README.md` - Environment management guide
- `docs/REPLICATION_GUIDE.md` - Step-by-step deployment process
- `docs/TESTING_VALIDATION.md` - Verification commands
- `Makefile` - Deployment orchestration

---

## Anti-Patterns (DO NOT DO THIS)

### ❌ DO NOT: Modify the ASTRO Project
- **Never** edit files in `C:\Users\james\Desktop\Projects\astro\`
- ASTRO is a separate project, not part of one-click-cortex
- Read from ASTRO for reference only, never modify

### ❌ DO NOT: Commit Credentials
- **Never** commit `.env` files with real credentials
- Use `.env.example` or `site-template.env` for templates
- Real credentials stay in gitignored `env/{site}.env` files

### ❌ DO NOT: Deploy Without Testing
- Always test SSH connectivity first
- Run health checks before and after deployment
- Create database backups before schema changes
- Use `--dry-run` modes when available

### ❌ DO NOT: Create Site-Specific Code
- Configuration only, no custom code per site
- Use `headcore.json` config files for site customization
- If you need site-specific logic, it goes in the plugin (not deployment scripts)

### ❌ DO NOT: Assume SCP Works on WP Engine
- WP Engine SSH is restricted - SCP often fails
- Use SSH with heredoc, base64 transfer, or Git deployment
- SFTP may work but requires password authentication

---

## Best Practices (DO THIS)

### ✅ DO: Use Environment Files
```bash
# Each site gets its own config
env/topusarealestate.env
env/client-acme.env
env/site-template.env (template)
```

### ✅ DO: Verify Connectivity First
```bash
# Test SSH access before deploying
ssh -i ~/.ssh/id_ed25519 user@site.ssh.wpengine.net "wp cli version"
```

### ✅ DO: Use Stealth Mode Appropriately
```bash
# Digital empire sites - hide tooling
HEADCORE_STEALTH_MODE=true

# Client sites - show branding
HEADCORE_STEALTH_MODE=false
```

### ✅ DO: Document Changes
- Update `CHANGELOG.md` for any plugin modifications
- Note deployment outcomes in site-specific notes
- Track issues in workorders if complex

### ✅ DO: Test After Deployment
```bash
# Verify SEO output
curl -s https://site.com/ | grep -E "(canonical|og:|schema.org)"

# Verify plugin active
wp plugin list | grep headcore

# Run health check
wp headcore doctor
```

---

## Escalation Paths

### When SSH Commands Hang (Common Issue)
**Problem:** Windows terminal not capturing SSH output  
**Solution:** 
1. Redirect output to file: `ssh ... "command" > output.txt`
2. Then read file with `read_file` tool
3. Or connect interactively and run commands manually

### When SCP Fails on WP Engine
**Problem:** SCP subsystem restricted  
**Solution:**
1. Use SSH with base64 encoding for file transfer
2. Use SFTP with password authentication
3. Use WP Engine Git Push feature (recommended long-term)

### When Plugin Won't Activate
**Problem:** Conflicting SEO plugin  
**Solution:**
1. Check for Yoast, Rank Math, All in One SEO
2. Either deactivate conflicting plugin
3. Or enable `force_output` setting in headcore
4. Or skip headcore entirely if site already has good SEO

---

## File Organization Standards

```
one-click-cortex/
├── plugin/              # THE deployable code (standalone)
│   └── headcore/        # WordPress SEO plugin
├── docs/                # Comprehensive guides
│   ├── EXEC_SUMMARY.md
│   ├── REPLICATION_GUIDE.md
│   ├── PREREQS_CHECKLIST.md
│   ├── TESTING_VALIDATION.md
│   ├── SECURITY_NOTES.md
│   ├── CORE_COMPONENTS.csv
│   └── STEALTH-MODE.md
├── env/                 # Per-site environment configs
│   ├── README.md
│   ├── site-template.env
│   └── {sitename}.env
├── ops/                 # Operations and deployment
│   └── scripts/
├── reports/             # Analysis outputs
├── scripts/             # Script templates
├── sds/                 # SBEP documentation (this file)
├── Makefile             # Deployment orchestration
├── CHANGELOG.md         # Version history
├── README.md            # Main documentation
└── QUICK_START_OVERVIEW.md
```

---

## Success Metrics

### Deployment Success
- Plugin activates without errors
- SEO tags appear in page source
- JSON-LD validates at schema.org
- No PHP errors in debug.log
- Health check passes: `wp headcore doctor`

### Security Success
- No credentials in repository
- SSH key authentication working
- No secrets in logs or outputs
- Environment files gitignored

### Documentation Success
- New agents can deploy without user intervention
- All steps in REPLICATION_GUIDE are accurate
- Environment templates are complete
- Testing commands produce expected results

---

## Common Tasks

### Deploy to New Site
```bash
# 1. Create env file
cp env/site-template.env env/newsite.env
# Edit env/newsite.env with site details

# 2. Test connection
ssh -i $SSH_KEY_PATH $SSH_USER@$SSH_HOST "wp cli version"

# 3. Deploy (via SSH + WP-CLI)
# Package locally
cd plugin/headcore && zip -r headcore.zip .

# Transfer and activate
# (See REPLICATION_GUIDE.md for full process)
```

### Enable Stealth Mode
```bash
# Via WP-CLI
wp option patch update headcore_settings stealth_mode 1

# Verify
curl -s https://site.com/ | grep "One Click SEO"
# (Should return nothing)
```

### Add New Site Environment
```bash
# Create new env file
cp env/site-template.env env/newclient.env

# Edit with site-specific values
# - WPE_SSH_HOST
# - WPE_SSH_USER
# - SITE_URL
# - HEADCORE_STEALTH_MODE
```

---

## Version Information

**Created:** 2025-10-16  
**SBEP Version:** 2.2  
**Project Version:** 1.0.1  
**Last Updated:** 2025-10-16

---

**Remember:** This is a deployment framework, not a web application. Focus on portability, repeatability, and clear documentation for future deployments.

