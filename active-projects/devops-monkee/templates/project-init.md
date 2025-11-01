# SBEP Project Initialization Template

This template provides the structure and content for initializing a new project with SBEP governance.

## Files Created

### Core SBEP Files
- `sds/SBEP-MANDATE.md` - Project-specific agent instructions
- `sds/SBEP-INDEX.yaml` - Documentation inventory
- `VERSION-MANIFEST.json` - Version tracking (copied from governance layer)
- `VALIDATION-SCHEMA.json` - Validation rules (copied from governance layer)

### Governance Files
- `CONSTITUTION.md` - SBEP constitutional principles
- `GOVERNANCE-LAYER.md` - Governance implementation guide
- `CHANGE-MANAGEMENT.md` - Protocol change procedures

### Directory Structure
- `.tmp/` - Temporary files and test outputs
- `archive/` - Deprecated files and completed work
- `sds/` - Source Documentation Store

## Post-Initialization Steps

### 1. Customize SBEP-MANDATE.md
Edit `sds/SBEP-MANDATE.md` to include:
- Actual technology stack used
- Project-specific integrations
- Deployment methods
- Testing approaches
- Anti-patterns to avoid

### 2. Update SBEP-INDEX.yaml
Review and update `sds/SBEP-INDEX.yaml` to:
- Mark existing files as `exists: true`
- Add project-specific documentation references
- Remove irrelevant template entries

### 3. Create README.md
If not already present, create a comprehensive `README.md` with:
- Project overview and purpose
- Installation and setup instructions
- Architecture overview
- Contributing guidelines

### 4. Initialize CHANGELOG.md
Create `CHANGELOG.md` following semantic versioning:
```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- SBEP v2.2 compliance and governance layer
- Project initialization with DevOps Monkee

## [0.1.0] - 2025-10-30

### Added
- Initial project setup
- Basic functionality
```

### 5. Run Initial Validation
Execute the first compliance check:
```bash
devops-monkee validate .
```

This will identify any missing files or configuration issues that need to be addressed.

### 6. Set Up CI/CD Integration
Consider adding to your CI/CD pipeline:
```yaml
# GitHub Actions example
- name: Validate SBEP Compliance
  run: npx devops-monkee validate .

- name: Audit Code Quality
  run: npx devops-monkee audit . --type quality
```

## Common Issues & Solutions

### Issue: "VERSION-MANIFEST.json not found"
**Solution:** Run `devops-monkee init .` again or manually copy from the governance layer.

### Issue: Validation fails with many errors
**Solution:** Focus on critical issues first, then address high-priority items. Use `--fix` flag for auto-remediation where available.

### Issue: Project-specific documentation missing
**Solution:** Create placeholder files and gradually fill them in. Update `SBEP-INDEX.yaml` as you add documentation.

## Next Steps

1. **Week 1**: Complete basic project documentation
2. **Week 2**: Set up CI/CD integration and automated validation
3. **Week 3**: Train team members on SBEP processes
4. **Month 1**: Conduct first governance audit and address findings

## Resources

- [SBEP Constitution](CONSTITUTION.md) - Core protocol principles
- [Governance Layer Guide](GOVERNANCE-LAYER.md) - Implementation details
- [DevOps Monkee Documentation](https://docs.devops-monkee.dev) - Complete reference
