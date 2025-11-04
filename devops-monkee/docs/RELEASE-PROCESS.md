# Release Process for DevOps Monkee

This document describes how to release new versions of `devops-monkee` to npm.

## Overview

Releases are automated via GitHub Actions using **npm Trusted Publishers** (OIDC). No npm tokens are required.

## Prerequisites

1. **npm Trusted Publishers** configured (one-time setup)
   - Go to: https://www.npmjs.com/settings/that-guy-jamie/packages
   - Navigate to "Trusted Publishers"
   - Add:
     - Publisher: GitHub Actions
     - Organization/user: `that-guy-jamie`
     - Repository: `devops-monkee`
     - Workflow filename: `release.yml`

2. **GitHub Actions** enabled for the repository

3. **SSH key** for GitHub (optional, for easier git operations)
   - See SSH setup in main README

## Release Steps

### 1. Update Version

Update `package.json` version:
```bash
npm version patch  # or minor, major
```

Or manually edit `package.json`:
```json
{
  "version": "1.2.0"
}
```

### 2. Update CHANGELOG.md

Document the changes in `CHANGELOG.md`:
```markdown
## [1.2.0] - 2025-11-03

### Added
- New feature X
- Security enhancement Y

### Changed
- Improved Z
```

### 3. Commit and Push

```bash
git add package.json CHANGELOG.md
git commit -m "chore: bump version to 1.2.0"
git push github main
```

### 4. Create and Push Tag

```bash
git tag -a v1.2.0 -m "Release v1.2.0: Description of changes"
git push github v1.2.0
```

### 5. GitHub Actions Automatically Publishes

- The workflow triggers on tag push
- It runs from `active-projects/devops-monkee/` directory
- Builds, tests, and publishes to npm with provenance
- No npm tokens needed (uses OIDC)

### 6. Verify Release

Check npm:
```bash
npm view devops-monkee version
```

Or visit: https://www.npmjs.com/package/devops-monkee

## Workflow Details

The `.github/workflows/release.yml` workflow:

1. **Triggers**: On push of tags matching `v*.*.*`
2. **Authentication**: Uses OIDC (npm Trusted Publishers) - no tokens
3. **Steps**:
   - Checks out code
   - Sets up Node.js 20
   - Changes to `active-projects/devops-monkee/` directory
   - Runs `npm ci`
   - Runs `npm audit --audit-level=moderate`
   - Builds with `npm run build`
   - Runs tests (if any)
   - Publishes with `npm publish --provenance --access public`

## Important Notes

### Directory Structure

The workflow assumes the project is in `active-projects/devops-monkee/` because:
- The repository root contains multiple projects
- `devops-monkee` is a subdirectory
- All workflow steps use `working-directory: active-projects/devops-monkee`

### Authentication

**No npm tokens are used or stored.** The workflow uses:
- **OpenID Connect (OIDC)** via GitHub Actions
- **npm Trusted Publishers** for authentication
- **Provenance** for package integrity

This is more secure than tokens because:
- No secrets to manage
- No tokens to rotate
- Automatic authentication via GitHub
- Package provenance proves authenticity

### Troubleshooting

**Workflow not triggering?**
- Check tag format: must match `v*.*.*` (e.g., `v1.2.0`)
- Verify tag was pushed: `git push github v1.2.0`

**Publish failing?**
- Check npm Trusted Publishers is configured
- Verify repository name matches: `that-guy-jamie/devops-monkee`
- Check workflow filename: `release.yml`

**Can't find package.json?**
- Verify workflow uses `working-directory: active-projects/devops-monkee`
- Check directory structure matches

## Manual Publish (Fallback)

If GitHub Actions fails, you can publish manually:

```bash
cd active-projects/devops-monkee
npm install
npm run build
npm publish --access public
```

**Note**: Manual publish doesn't include provenance. Use GitHub Actions when possible.

## Version Numbering

Follow [Semantic Versioning](https://semver.org/):
- **MAJOR**: Breaking changes (1.0.0 → 2.0.0)
- **MINOR**: New features, backwards compatible (1.0.0 → 1.1.0)
- **PATCH**: Bug fixes, backwards compatible (1.0.0 → 1.0.1)

## Post-Release Checklist

- [ ] Verify version appears on npm
- [ ] Check GitHub releases page
- [ ] Update documentation if needed
- [ ] Announce release (if appropriate)

---

**Built entirely in Cursor** - This entire project, including releases, is managed through Cursor IDE.

