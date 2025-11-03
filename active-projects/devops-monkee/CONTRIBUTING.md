# Contributing to DevOps Monkee

Thanks for helping make DevOps Monkee better! This doc covers local setup, coding standards, testing, and releases.

## Prereqs

- Node.js **18+**
- npm (comes with Node)
- macOS/Linux/Windows supported

## Setup

```bash
git clone https://github.com/that-guy-jamie/devops-monkee.git
cd devops-monkee
npm ci
npm run build
npm test
```

Run the CLI locally:

```bash
node dist/cli.js --help
npx devops-monkee --help
npx sbep --help
npx dopm --help
```

## Coding Standards

* **TypeScript** (ESM)
* **ESLint + Prettier**: `npm run lint` / `npm run format`
* **Tests:** Jest — `npm test`
* Keep `dist/` generated only by `npm run build`
* Ensure `dist/cli.js` keeps the shebang (`#!/usr/bin/env node`)

## Conventional Commits

Please use Conventional Commits:

```
feat(scope): add X
fix(scope): handle Y
chore(oss): docs, ci, config
refactor(...), perf(...), test(...), docs(...), build(...)
```

## Branch & PR Flow

* Branch from `main`: `feat/…`, `fix/…`, `docs/…`
* Open a PR with:
  * What/why summary
  * Screens/logs for CLI changes
  * Tests if behavior changes
* Passing CI required before merge

## Releasing (Maintainers)

DevOps Monkee uses **npm Trusted Publishing** with provenance.

1. Bump version & tag:
   ```bash
   npm run release:tag   # bumps patch with a conventional message
   git push && git push --tags
   ```

2. GitHub Actions builds/tests and runs:
   ```bash
   npm publish --provenance --access public
   ```

3. Verify the npm page.

**Never** run `npm publish` locally. CI handles it.

## Security Guidelines

Please see **SECURITY.md** for how to report vulnerabilities.

### Development Security

When contributing code:

- **Never commit secrets** - Use environment variables or placeholders (`"CHANGE_ME"`)
- **Validate inputs** - All file paths and user inputs must be validated
- **Sanitize logs** - Never log sensitive information
- **Use secure parsing** - Use safe YAML/JSON parsing methods
- **Review before commit** - Check for hardcoded credentials or secrets

For comprehensive security practices, see [SBEP Security Guidelines](./docs/SBEP-SECURITY-GUIDELINES.md).

### Pre-Commit Checks

Consider installing pre-commit hooks for secret detection:

```bash
# Install gitleaks (recommended)
brew install gitleaks

# Add to .git/hooks/pre-commit
gitleaks protect --staged --verbose
```
