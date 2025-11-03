# Project Lifecycle with Corporate Docs Pattern

## Overview

This document walks through a complete project lifecycle using the corporate-docs pattern. It shows how agents access credentials, how incident reports are handled, and how institutional knowledge is shared across projects.

## Directory Structure

```
C:\Users\james\Desktop\Projects\
├── active-projects/
│   └── devops-monkee/              # Repository (in git)
│       ├── src/                    # Public code
│       ├── docs/                   # Public documentation
│       └── .gitignore             # Ignores corporate-docs
│
└── corporate-docs/                  # Outside repo (NOT in git)
    └── devops-monkee/
        ├── credentials/            # Agent credentials
        │   ├── render-api.env
        │   ├── github-tokens.env
        │   └── npm-auth.env
        ├── incident-reports/       # AARs, security incidents
        │   ├── SECURITY_INCIDENT_AAR.md
        │   └── EXPOSED_SECRETS_SUMMARY.md
        └── internal-docs/          # Institutional knowledge
            ├── deployment-patterns.md
            ├── team-workflows.md
            └── lessons-learned.md
```

## Project Lifecycle Walkthrough

### Phase 1: Project Initialization

**Agent Action:**
```typescript
// Agent needs to initialize project
// 1. Read credentials from corporate-docs
const credsPath = path.join(
  process.env.USERPROFILE,
  'Desktop/Projects/corporate-docs/devops-monkee/credentials/render-api.env'
);
const credentials = await fs.readFile(credsPath, 'utf-8');

// 2. Use credentials to set up services
// 3. Create project structure in active-projects/
```

**What Happens:**
- ✅ Credentials read from corporate-docs
- ✅ Services configured using credentials
- ✅ Project created in active-projects/
- ✅ No credentials committed to git

**Files Created:**
- `active-projects/devops-monkee/` - Repository structure
- `corporate-docs/devops-monkee/credentials/` - Already exists

---

### Phase 2: Development

**Agent Action:**
```typescript
// Agent working on feature
// 1. Read deployment patterns from internal-docs
const patternsPath = path.join(
  process.env.USERPROFILE,
  'Desktop/Projects/corporate-docs/devops-monkee/internal-docs/deployment-patterns.md'
);
const patterns = await fs.readFile(patternsPath, 'utf-8');

// 2. Apply patterns to code
// 3. Commit code (no credentials or patterns)
```

**What Happens:**
- ✅ Institutional knowledge read from corporate-docs
- ✅ Patterns applied to code
- ✅ Code committed (generic, no secrets)
- ✅ Corporate docs stay private

**Files Modified:**
- `active-projects/devops-monkee/src/` - Code changes
- `corporate-docs/` - Unchanged (agents read, don't write during dev)

---

### Phase 3: Security Incident

**Agent Action:**
```typescript
// Incident detected
// 1. Write incident report to corporate-docs
const incidentPath = path.join(
  process.env.USERPROFILE,
  'Desktop/Projects/corporate-docs/devops-monkee/incident-reports/INCIDENT-2025-11-03.md'
);
await fs.writeFile(incidentPath, incidentReport);

// 2. Rotate credentials
const newCreds = generateSecureCredentials();
await fs.writeFile(credsPath, newCreds);

// 3. Update public repo with fixes (no incident details)
```

**What Happens:**
- ✅ Incident report written to corporate-docs
- ✅ Credentials rotated in corporate-docs
- ✅ Public repo updated with security fixes
- ✅ No incident details in git history

**Files Created/Modified:**
- `corporate-docs/devops-monkee/incident-reports/INCIDENT-2025-11-03.md` - NEW
- `corporate-docs/devops-monkee/credentials/` - UPDATED
- `active-projects/devops-monkee/SECURITY.md` - UPDATED (generic, no details)

---

### Phase 4: Lessons Learned

**Agent Action:**
```typescript
// After incident, document lessons
// 1. Read incident report
const incident = await fs.readFile(incidentPath, 'utf-8');

// 2. Extract lessons learned
const lessons = extractLessons(incident);

// 3. Write to internal-docs
const lessonsPath = path.join(
  process.env.USERPROFILE,
  'Desktop/Projects/corporate-docs/devops-monkee/internal-docs/lessons-learned.md'
);
await fs.appendFile(lessonsPath, lessons);

// 4. Update public repo with best practices (generic)
//    - No incident details
//    - Just the practices
```

**What Happens:**
- ✅ Lessons learned documented in corporate-docs
- ✅ Institutional knowledge preserved
- ✅ Public repo gets best practices (generic)
- ✅ No incident exposure

**Files Modified:**
- `corporate-docs/devops-monkee/internal-docs/lessons-learned.md` - UPDATED
- `active-projects/devops-monkee/docs/SBEP-SECURITY-GUIDELINES.md` - UPDATED (generic)

---

### Phase 5: Cross-Project Sharing

**Agent Action:**
```typescript
// New project needs deployment patterns
// 1. Read from existing project's corporate-docs
const patterns = await fs.readFile(
  'C:/Users/james/Desktop/Projects/corporate-docs/devops-monkee/internal-docs/deployment-patterns.md',
  'utf-8'
);

// 2. Copy to new project's corporate-docs
const newProjectPath = 'C:/Users/james/Desktop/Projects/corporate-docs/new-project/internal-docs/';
await fs.ensureDir(newProjectPath);
await fs.writeFile(
  path.join(newProjectPath, 'deployment-patterns.md'),
  patterns
);
```

**What Happens:**
- ✅ Institutional knowledge shared across projects
- ✅ Patterns copied to new project
- ✅ No git exposure
- ✅ Knowledge preserved

**Files Created:**
- `corporate-docs/new-project/internal-docs/deployment-patterns.md` - NEW (from template)

---

### Phase 6: Agent Handoff

**Agent Action:**
```typescript
// Agent needs to hand off to another agent
// 1. Read context from corporate-docs
const context = {
  credentials: await fs.readFile(credsPath, 'utf-8'),
  patterns: await fs.readFile(patternsPath, 'utf-8'),
  lessons: await fs.readFile(lessonsPath, 'utf-8')
};

// 2. Agent has full context
// 3. Continues work without re-reading
```

**What Happens:**
- ✅ New agent reads corporate-docs
- ✅ Full context available
- ✅ No need to re-discover credentials
- ✅ Institutional knowledge accessible

---

## Key Workflows

### Credential Access Pattern

```typescript
// Standard pattern for agent credential access
function getCorporateDocsPath(projectName: string, category: string): string {
  return path.join(
    process.env.USERPROFILE || process.env.HOME,
    'Desktop/Projects/corporate-docs',
    projectName,
    category
  );
}

// Usage
const credsPath = getCorporateDocsPath('devops-monkee', 'credentials');
const credentials = await fs.readFile(credsPath, 'utf-8');
```

### Incident Reporting Pattern

```typescript
// When incident occurs
async function reportIncident(projectName: string, incident: string): Promise<void> {
  const incidentPath = path.join(
    getCorporateDocsPath(projectName, 'incident-reports'),
    `INCIDENT-${new Date().toISOString().split('T')[0]}.md`
  );
  
  await fs.ensureDir(path.dirname(incidentPath));
  await fs.writeFile(incidentPath, incident);
  
  // Never commit to git
  console.log(`Incident report written to: ${incidentPath}`);
  console.log('This file is NOT in git and will NOT be committed.');
}
```

### Knowledge Sharing Pattern

```typescript
// Share knowledge across projects
async function shareKnowledge(
  sourceProject: string,
  targetProject: string,
  knowledgeFile: string
): Promise<void> {
  const sourcePath = getCorporateDocsPath(sourceProject, 'internal-docs');
  const targetPath = getCorporateDocsPath(targetProject, 'internal-docs');
  
  const content = await fs.readFile(
    path.join(sourcePath, knowledgeFile),
    'utf-8'
  );
  
  await fs.ensureDir(targetPath);
  await fs.writeFile(
    path.join(targetPath, knowledgeFile),
    content
  );
}
```

## Benefits Throughout Lifecycle

### 1. No Git Exposure Risk
- ✅ Credentials never in git
- ✅ Incident reports never in git
- ✅ Internal knowledge never in git
- ✅ Even if accidentally staged, .gitignore blocks

### 2. Agent Collaboration
- ✅ Agents can read corporate-docs
- ✅ Shared credential access
- ✅ Shared institutional knowledge
- ✅ No need to re-discover

### 3. Institutional Memory
- ✅ Lessons learned preserved
- ✅ Patterns documented
- ✅ Knowledge shared across projects
- ✅ No loss when agents change

### 4. Clear Separation
- ✅ Public repo = public stuff
- ✅ Corporate docs = private stuff
- ✅ No confusion about what goes where
- ✅ No example files mixed with real files

## Example Files vs Real Files

### Problem Before:
```
active-projects/devops-monkee/
├── .env.example          # Example (safe)
├── .env                  # Real (shouldn't be in git!)
└── SECURITY_INCIDENT_AAR.md  # Real (shouldn't be in git!)
```

**Confusion:**
- Which .env is real?
- Accidentally committed .env
- Example files mixed with real files

### Solution Now:
```
active-projects/devops-monkee/
└── .env.example          # Only examples in repo

corporate-docs/devops-monkee/
├── credentials/
│   └── .env              # Real credentials (not in git)
└── incident-reports/
    └── SECURITY_INCIDENT_AAR.md  # Real incident (not in git)
```

**Clear:**
- ✅ Examples in repo only
- ✅ Real files in corporate-docs only
- ✅ No confusion
- ✅ No commit risk

## Agent Instructions

When agents need credentials or context:

1. **Read from corporate-docs:**
   ```typescript
   const path = 'C:/Users/james/Desktop/Projects/corporate-docs/devops-monkee/credentials/render-api.env';
   ```

2. **Never commit corporate-docs:**
   - Corporate-docs is outside repo
   - .gitignore blocks it anyway
   - But agents should never try to commit it

3. **Write incident reports to corporate-docs:**
   ```typescript
   await fs.writeFile(
     'C:/Users/james/Desktop/Projects/corporate-docs/devops-monkee/incident-reports/INCIDENT.md',
     report
   );
   ```

4. **Share knowledge across projects:**
   - Read from one project's corporate-docs
   - Write to another project's corporate-docs
   - Knowledge preserved, no git exposure

## Complete Example: New Project Setup

```typescript
// 1. Agent initializes project
const projectName = 'new-project';

// 2. Create corporate-docs structure
await fs.ensureDir(`C:/Users/james/Desktop/Projects/corporate-docs/${projectName}/credentials`);
await fs.ensureDir(`C:/Users/james/Desktop/Projects/corporate-docs/${projectName}/incident-reports`);
await fs.ensureDir(`C:/Users/james/Desktop/Projects/corporate-docs/${projectName}/internal-docs`);

// 3. Copy patterns from existing project
await shareKnowledge('devops-monkee', projectName, 'deployment-patterns.md');

// 4. Create project repo
await initializeSBEPProject(`C:/Users/james/Desktop/Projects/active-projects/${projectName}`);

// 5. Agent has:
//    - Project structure (in git)
//    - Corporate docs (outside git)
//    - Credentials location (corporate-docs)
//    - Patterns from other projects
```

## Maintenance

### Regular Tasks

1. **Backup corporate-docs:**
   - Separate from git backup
   - Encrypted backup recommended
   - Regular schedule

2. **Review corporate-docs:**
   - Clean up old credentials
   - Archive old incident reports
   - Update institutional knowledge

3. **Share knowledge:**
   - Extract patterns from projects
   - Document in internal-docs
   - Share across projects

---

**This pattern ensures clean separation, agent access, and institutional knowledge preservation throughout the entire project lifecycle.**

