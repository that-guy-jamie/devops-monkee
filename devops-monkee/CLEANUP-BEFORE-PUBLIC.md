# Cleanup Checklist Before Making Repo Public

## Files That Should Be in GitHub

### Core Package Files
- [x] `package.json` - Package configuration
- [x] `package-lock.json` - Dependency lock file
- [x] `tsconfig.json` - TypeScript configuration
- [x] `.gitignore` - Git ignore rules
- [x] `LICENSE` - MIT License

### Source Code
- [x] `src/` - All TypeScript source files
- [x] `tests/` - Test files
- [ ] `dist/` - **SHOULD NOT BE IN GIT** (build artifacts, already in .gitignore)

### Documentation
- [x] `README.md` - Main readme (displays on npmjs.com)
- [x] `CHANGELOG.md` - Version history
- [x] `SECURITY.md` - Security policy
- [x] `CONTRIBUTING.md` - Contribution guidelines
- [x] `CODE_OF_CONDUCT.md` - Code of conduct
- [x] `CONSTITUTION.md` - SBEP constitution
- [x] `GOVERNANCE-LAYER.md` - Governance documentation
- [x] `CHANGE-MANAGEMENT.md` - Change management process
- [x] `docs/` - Documentation directory
- [x] `templates/` - Template files
- [x] `readme-for-people.md` - Human-readable readme

### Configuration Files
- [x] `VALIDATION-SCHEMA.json` - SBEP validation schema
- [x] `VERSION-MANIFEST.json` - Version manifest
- [x] `.editorconfig` - Editor configuration

### GitHub Files
- [x] `.github/` - GitHub workflows, templates, funding
- [x] `.github/FUNDING.yml`
- [x] `.github/ISSUE_TEMPLATE/`
- [x] `.github/PULL_REQUEST_TEMPLATE.md`
- [x] `.github/workflows/ci.yml`

## Files That Should NOT Be in GitHub

### Already in .gitignore (good)
- [x] `node_modules/` - Dependencies
- [x] `dist/` - Build output (should NOT be committed)
- [x] `.env*` - Environment variables
- [x] `.vscode/` - Editor configs
- [x] `.idea/` - IDE configs
- [x] `*.tgz` - Pack files
- [x] `*.log` - Log files
- [x] `.tmp/` - Temporary files
- [x] `archive/` - Archive files

### Check for These (might need .gitignore updates)
- [ ] Any `*.key`, `*.pem`, `*.p12` files - Credentials
- [ ] `secrets/` directory - Secrets
- [ ] `credentials.json` - API credentials
- [ ] `google-service-account.json` - Service account keys
- [ ] Any personal/orphan data files
- [ ] `housekeeping.config.json` - Local config
- [ ] `.cursor/` - Cursor IDE files (already in .gitignore)
- [ ] `.cursorrules` - Cursor rules

## Orphan Branch Cleanup Steps

### 1. Check What's in the Orphan Branch
```bash
cd c:/Users/james/Desktop/Projects/devops-monkee
git checkout chore/orphans-20251031
git ls-files > files-in-orphan-branch.txt
```

### 2. Compare to Main
```bash
git checkout main
git ls-files > files-in-main.txt
# Compare the two files
```

### 3. Remove Files That Shouldn't Be There
If orphan branch has files that shouldn't be committed:
```bash
git checkout chore/orphans-20251031

# Remove specific files
git rm path/to/file-that-shouldnt-be-there

# Remove directories
git rm -r path/to/directory/

# Commit the cleanup
git commit -m "Remove files that shouldn't be in public repo"
```

### 4. Ensure Required Files Are Present
Compare with main branch to ensure nothing essential is missing:
```bash
# Check if main has files that orphan branch is missing
git diff main...chore/orphans-20251031 --name-only --diff-filter=D
```

### 5. Merge Cleanup Back to Main (if needed)
```bash
git checkout main
git merge chore/orphans-20251031
# Or cherry-pick specific commits
```

## Make Repo Public

### 1. Final Checks
- [ ] Review all files in repo: `git ls-files`
- [ ] Check for secrets: `git grep -i "password\|secret\|key\|token" -- '*.json' '*.ts' '*.js'`
- [ ] Verify .gitignore is comprehensive
- [ ] Check README.md is complete and professional
- [ ] Ensure LICENSE file is correct (MIT)

### 2. Clean Up History (if needed)
If sensitive data was committed in the past:
```bash
# Use BFG Repo-Cleaner or git-filter-repo
# Remove sensitive files from history
```

### 3. Make Public on GitHub
1. Go to repository settings
2. Scroll to "Danger Zone"
3. Click "Change visibility"
4. Select "Make public"
5. Confirm

### 4. Update npm Package (if publishing)
```bash
npm run build
npm publish
```

## Recommended .gitignore Additions

Add these if not already present:
```
# Credentials and secrets
*.key
*.pem
*.p12
*.p8
credentials.json
service-account*.json
secrets/

# Personal/orphan data
orphan*/
personal-data/
client-work/
Workorders/
Tools/theastro-*.txt

# Local configs
housekeeping.config.json
.cursorrules
```

## Verification Commands

```bash
# List all tracked files
git ls-files

# Check for potential secrets
git ls-files | grep -E "(secret|key|token|credential|password)"

# Verify no large files
git ls-files -z | xargs -0 du -h | sort -rh | head -20

# Check for common mistakes
git ls-files | grep -E "(node_modules|dist/|\.env|\.log)"
```

