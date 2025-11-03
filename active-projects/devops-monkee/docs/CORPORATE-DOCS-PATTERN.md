# Corporate Docs Pattern

## Overview

This document describes the recommended pattern for storing corporate documentation outside the repository. This includes sensitive documents, credentials, incident reports, and other materials that should not be in version control.

## Directory Structure

```
C:\Users\james\Desktop\Projects\
├── active-projects/
│   └── devops-monkee/          # Repository (in git)
│       ├── src/
│       ├── docs/               # Public documentation
│       └── ...
│
└── corporate-docs/              # Outside repo (NOT in git)
    ├── devops-monkee/
    │   ├── credentials.env     # Agent credentials
    │   ├── incident-reports/    # AARs, security incidents
    │   ├── internal-notes.md    # Private notes
    │   └── ...
    └── [other-projects]/
```

## Benefits

1. **Separation of Concerns**
   - Public repo: Public documentation only
   - Corporate docs: Private, sensitive materials

2. **Security**
   - Credentials never risk git exposure
   - Incident reports stay private
   - No risk of accidental commits

3. **Agent Access**
   - Agents can read from corporate-docs
   - Credentials available for MCP/API access
   - Not written to git history

4. **Flexibility**
   - Easy to share with team members
   - Can be backed up separately
   - No git history concerns

## Implementation

### Create Corporate Docs Structure

```powershell
# Create corporate docs folder
New-Item -ItemType Directory -Path "C:\Users\james\Desktop\Projects\corporate-docs\devops-monkee" -Force

# Create subdirectories
New-Item -ItemType Directory -Path "C:\Users\james\Desktop\Projects\corporate-docs\devops-monkee\credentials" -Force
New-Item -ItemType Directory -Path "C:\Users\james\Desktop\Projects\corporate-docs\devops-monkee\incident-reports" -Force
New-Item -ItemType Directory -Path "C:\Users\james\Desktop\Projects\corporate-docs\devops-monkee\internal-docs" -Force
```

### Add to Global .gitignore

Create or update `C:\Users\james\.gitignore_global`:

```
# Corporate docs - never commit
corporate-docs/
```

Then configure git:
```bash
git config --global core.excludesfile ~/.gitignore_global
```

### Agent Access Pattern

Agents can read from corporate-docs:

```typescript
// Example: Agent reading credentials
const credentialsPath = path.join(
  process.env.HOME || process.env.USERPROFILE,
  'Desktop/Projects/corporate-docs/devops-monkee/credentials.env'
);

// Read but never commit
const creds = await fs.readFile(credentialsPath, 'utf-8');
```

## What Goes Where

### ✅ Repository (in git)
- Public documentation
- Code examples
- Templates
- API documentation
- Usage guides

### ❌ Corporate Docs (outside git)
- Credentials and secrets
- Incident reports (AARs)
- Security incident details
- Internal notes
- Private documentation
- Proprietary information

## Best Practices

1. **Never Reference Corporate Docs in Code**
   - Don't hardcode paths to corporate-docs
   - Use environment variables or config
   - Document that agents should read from corporate-docs

2. **Document the Pattern**
   - Include this pattern in onboarding
   - Make it clear where things go
   - Update as needed

3. **Regular Backups**
   - Corporate docs should be backed up separately
   - Not part of git repo backup
   - Consider encrypted backup

4. **Access Control**
   - Corporate docs folder permissions
   - Only team members who need access
   - Consider encryption for sensitive files

## Example Structure

```
corporate-docs/
└── devops-monkee/
    ├── credentials/
    │   ├── render-api.env
    │   ├── github-tokens.env
    │   └── npm-auth.env
    ├── incident-reports/
    │   ├── SECURITY_INCIDENT_AAR.md
    │   ├── EXPOSED_SECRETS_SUMMARY.md
    │   └── HOW_SECRETS_GOT_EXPOSED.md
    └── internal-docs/
        ├── roadmap.md
        ├── team-notes.md
        └── proprietary-info.md
```

## Agent Workflow

1. **Agent needs credentials** → Read from `corporate-docs/devops-monkee/credentials/`
2. **Agent needs context** → Read from `corporate-docs/devops-monkee/internal-docs/`
3. **Agent finds incident** → Write to `corporate-docs/devops-monkee/incident-reports/`
4. **Never commit** → Corporate docs are outside git

## Security Notes

- ✅ Corporate docs are NOT in git
- ✅ Can't be accidentally committed
- ✅ No git history exposure
- ✅ Can be shared with team separately
- ✅ Agents can access without git risk

---

**This pattern ensures sensitive corporate documentation stays private while allowing agents to access what they need.**

