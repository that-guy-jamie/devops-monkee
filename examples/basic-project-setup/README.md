# Basic SBEP Project Setup Example

This example shows how to set up a new project following SBEP v2.0 standards.

## Step 1: Create Project Structure

```bash
mkdir my-new-project
cd my-new-project

# Create standard directories
mkdir sds docs ops scripts archive .tmp
mkdir docs/patterns docs/guides
mkdir ops/deployment ops/maintenance
```

## Step 2: Copy SBEP Templates

```bash
# Copy templates from SBEP_Core
cp ../SBEP_Core/SBEP-MANDATE-TEMPLATE.md sds/SBEP-MANDATE.md
cp ../SBEP_Core/SBEP-INDEX-TEMPLATE.yaml sds/SBEP-INDEX.yaml
```

## Step 3: Customize Project Configuration

### Edit `sds/SBEP-MANDATE.md`
- Update project name and description
- Add project-specific tech stack details
- Define integration points and APIs
- Set project-specific rules and patterns

### Edit `sds/SBEP-INDEX.yaml`
- List all project documentation
- Define API documentation locations
- Map out integration guides
- Reference external dependencies

## Step 4: Create Core Project Files

```bash
# Project overview
touch README.md

# Change tracking
touch CHANGELOG.md

# Documentation structure
touch docs/ARCHITECTURE.md
touch docs/API-INTEGRATION.md
touch docs/DEPLOYMENT-GUIDE.md
```

## Step 5: Initial Documentation Content

### README.md Template
```markdown
# My New Project

## Overview
Brief description of what this project does.

## Quick Start
1. Prerequisites
2. Installation steps
3. Basic usage

## Documentation
- Architecture: `docs/ARCHITECTURE.md`
- API Integration: `docs/API-INTEGRATION.md`
- Deployment: `docs/DEPLOYMENT-GUIDE.md`

## SBEP Compliance
This project follows SBEP v2.0 standards:
- Agent instructions: `sds/SBEP-MANDATE.md`
- Documentation index: `sds/SBEP-INDEX.yaml`
```

### CHANGELOG.md Template
```markdown
# Changelog

## [Unreleased]

### Added
- Initial project setup following SBEP v2.0
- Basic documentation structure
- SBEP compliance framework

### Changed

### Deprecated

### Removed

### Fixed

### Security
```

## Step 6: Validation

After setup, verify SBEP compliance:

1. **Documentation Check**: All files referenced in `sds/SBEP-INDEX.yaml` exist
2. **Structure Check**: Standard directories are present
3. **Agent Test**: Have an AI agent read the documentation and attempt a simple task
4. **Integration Check**: Verify API documentation is accessible and current

## Common Customizations

### Tech Stack Specific
- **Node.js**: Add `package.json`, `.nvmrc`, `docs/NPM-DEPENDENCIES.md`
- **Python**: Add `requirements.txt`, `.python-version`, `docs/PYTHON-SETUP.md`
- **WordPress**: Add `wp-config-template.php`, `docs/WORDPRESS-SETUP.md`

### Integration Specific  
- **API Integrations**: Document in `docs/API-INTEGRATION.md`
- **Database Schema**: Add `docs/DATABASE-SCHEMA.md`
- **Deployment**: Update `ops/deployment/` with scripts and guides

## Next Steps

1. Begin development following SBEP patterns
2. Update documentation as you build
3. Use `SBEP_Core/Invoke-ProjectHousekeeping.ps1` for cleanup
4. Archive obsolete files instead of deleting
5. Update `CHANGELOG.md` with each significant change

This structure ensures any AI agent can understand and work with your project immediately.
