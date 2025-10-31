# SBEP Repository Organization

**Last Updated:** October 31, 2025
**SBEP Version:** v2.2

## Overview

This repository follows **SBEP (Source-Bound Execution Protocol)** guidelines for organized, scalable project management. The structure ensures clean separation of concerns while maintaining accessibility and discoverability.

## Directory Structure

```
Projects/
├── .git/                          # Main repository
├── SBEP-MANIFEST.md              # Core protocol (PROTECTED)
├── REPOSITORY-ORGANIZATION.md    # This file (PROTECTED)
├── .gitignore                    # SBEP-compliant ignore rules
├── README.md                     # Main repository documentation
├── CHANGELOG.md                  # Repository-level changes
├── CONTRIBUTING.md               # Contribution guidelines
│
├── active-projects/              # 🚀 Core ongoing projects
│   ├── devops-monkee/           # SBEP governance framework
│   ├── audit-monkee/            # AI auditing tools
│   ├── ads-monkee/              # Advertising automation
│   ├── google-ads-manager/      # Google Ads integration
│   └── schema-monkee/           # Data schema tools
│
├── client-work/                  # 🔒 Client-specific projects (GIT IGNORED)
│   ├── astro/                    # WordPress theme development
│   ├── lsa-dashboard/            # LSA survey system
│   ├── jamie_lcs-system/         # LCS lead system
│   ├── lcg-system-main/          # LCG call generation
│   └── one-click-cortex/         # AI workflow automation
│
├── shared-tools/                 # 🛠️ Reusable tools and scripts
│   ├── scripts/                  # Deployment and utility scripts
│   └── templates/                # Project templates
│
├── cross-project-docs/           # 📚 Shared documentation
│   ├── API-docs/                 # API documentation for external services
│   └── guides/                   # Cross-project guides
│
├── SBEP_Core/                    # ⚖️ Protocol core files (PROTECTED)
│   ├── SBEP-MANIFEST.md         # Global operating mandate
│   ├── HOUSEKEEPING-SOP.md      # Housekeeping procedures
│   └── EXCEPTION-POLICIES/      # Protocol exception handling
│
├── Workorders/                   # 📋 Project management
│   ├── active/                   # Current work orders
│   └── Archive/                  # Completed work orders (GIT IGNORED)
│
├── Archive/                      # 📦 Completed work (GIT IGNORED)
│   ├── projects/                 # Completed project files
│   └── housekeeping/             # Housekeeping operation archives
│
└── .tmp/                         # 🗂️ Temporary files (GIT IGNORED)
    ├── backup/                   # Emergency backups
    ├── recovery/                 # Recovery operations
    └── output/                   # Temporary outputs
```

## Directory Purposes

### 🚀 active-projects/
- **Purpose:** Core ongoing OneClickSEO projects that are actively developed
- **Git Status:** Fully version controlled
- **Examples:** devops-monkee, audit-monkee, ads-monkee
- **When to add:** New core platform projects

### 🔒 client-work/
- **Purpose:** Client-specific customizations and implementations
- **Git Status:** IGNORED (not version controlled)
- **Examples:** astro (WordPress themes), lsa-dashboard (client surveys)
- **When to add:** New client projects or custom implementations

### 🛠️ shared-tools/
- **Purpose:** Reusable tools, scripts, and templates
- **Git Status:** Fully version controlled
- **Examples:** Deployment scripts, CI/CD templates, utility functions
- **When to add:** General-purpose tools that could benefit multiple projects

### 📚 cross-project-docs/
- **Purpose:** Documentation that spans multiple projects
- **Git Status:** Fully version controlled
- **Examples:** API documentation, integration guides, architectural decisions
- **When to add:** Documentation that doesn't belong to a single project

### 📦 Archive/
- **Purpose:** Preserved completed work and historical data
- **Git Status:** IGNORED (preserved locally but not versioned)
- **Examples:** Completed project deliverables, old deployments
- **When to add:** Files that are complete but no longer actively worked on

### 🗂️ .tmp/
- **Purpose:** Temporary files and scratch work
- **Git Status:** IGNORED
- **Examples:** Log files, temporary outputs, test results
- **When to add:** Files that are truly temporary and disposable

## SBEP Compliance Rules

### ✅ What Gets Version Controlled
- `active-projects/` - Core platform development
- `shared-tools/` - Reusable infrastructure
- `cross-project-docs/` - Shared knowledge
- `SBEP_Core/` - Protocol documentation
- Core repository files (README, .gitignore, etc.)

### ❌ What Gets Ignored
- `client-work/` - Client-specific customizations
- `Archive/` - Completed historical work
- `.tmp/` - Temporary files
- `Workorders/Archive/` - Completed work orders
- Environment files (.env)
- Build outputs (node_modules, dist)

### 🛡️ Protected Files (Never Move)
- `SBEP-MANIFEST.md` - Core protocol
- `REPOSITORY-ORGANIZATION.md` - This organization guide
- `.cursorrules` - AI agent configuration
- Core configuration files

## Workflow Guidelines

### Adding New Projects
1. **Core Platform Project** → `active-projects/`
2. **Client Work** → `client-work/`
3. **Shared Tool** → `shared-tools/`
4. **Documentation** → `cross-project-docs/`

### File Lifecycle
1. **Active Work** → Project directories
2. **Complete** → Move to `Archive/`
3. **Temporary** → Move to `.tmp/`
4. **Deprecated** → Move to `Archive/` with deprecation notice

### Housekeeping Schedule
- **Daily:** Clean `.tmp/` directory
- **Weekly:** Review and archive completed work
- **Monthly:** Audit directory structure compliance
- **Quarterly:** Compress old archives

## Benefits of This Structure

1. **🔍 Discoverability:** Clear separation makes finding projects easy
2. **🚀 Performance:** Git operations faster with focused tracking
3. **🔒 Security:** Client work isolated from version control
4. **📚 Organization:** Related projects grouped logically
5. **🔄 Scalability:** Structure supports growth without complexity
6. **⚖️ Compliance:** Follows SBEP protocol for consistency

## Maintenance

Run the SBEP housekeeping script regularly:
```bash
# Dry run first
.\SBEP_Core\Invoke-ProjectHousekeeping.ps1 -DryRun

# Then execute
.\SBEP_Core\Invoke-ProjectHousekeeping.ps1
```

This ensures the repository remains clean and organized according to SBEP guidelines.

---

**Remember:** This structure evolves with the protocol. Always consult `SBEP-MANIFEST.md` for the latest guidelines.
