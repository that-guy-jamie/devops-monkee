# HOW TO PUBLISH DEVOPS-MONKEE TO NPM

**SIMPLE AF - 4 STEPS**

---

## Prerequisites

1. You're logged into npm as `that-guy-jamie`
   ```bash
   npm whoami
   # Should show: that-guy-jamie
   ```

2. If not logged in:
   ```bash
   npm login
   # Username: that-guy-jamie
   # Email: shorttermrentalowners@gmail.com
   # Password: [your npm password]
   ```

---

## The 4-Step Publish Process

### Step 1: Update Version

Edit `package.json` - change the version number:
```json
{
  "version": "1.1.1"  ← Change this (was 1.1.0)
}
```

**Or use npm:**
```bash
npm version patch   # 1.1.0 → 1.1.1 (bug fixes)
npm version minor   # 1.1.0 → 1.2.0 (new features)
npm version major   # 1.1.0 → 2.0.0 (breaking changes)
```

### Step 2: Build

```bash
npm run build
```

This compiles TypeScript (`src/`) to JavaScript (`dist/`)

### Step 3: Test (Optional but Recommended)

```bash
# Test locally
npm test

# Or manual test
node dist/cli.js --help
```

### Step 4: Publish

```bash
npm publish
```

**THAT'S IT. DONE.**

---

## Full Workflow Example

```powershell
cd C:\Users\james\Desktop\Projects\devops-monkee

# 1. Make your changes to src/
# (edit TypeScript files)

# 2. Bump version
npm version patch

# 3. Build
npm run build

# 4. Publish
npm publish

# 5. Verify
npm view devops-monkee version
```

---

## Troubleshooting

### "You must be logged in to publish"
```bash
npm login
```

### "Cannot publish over existing version"
You forgot to bump the version. Run:
```bash
npm version patch
```

### "Build failed"
Check for TypeScript errors:
```bash
npm run build
# Fix any errors in src/
```

### "Permission denied"
Make sure you're logged in as `that-guy-jamie`:
```bash
npm whoami
```

---

## Quick Reference

| Command | What It Does |
|---------|-------------|
| `npm version patch` | 1.1.0 → 1.1.1 |
| `npm run build` | Compile TS to JS |
| `npm publish` | Push to npm |
| `npm view devops-monkee` | Check live version |

---

## The Files That Matter

```
devops-monkee/
├── src/              ← Edit these (TypeScript source)
│   ├── cli.ts
│   ├── governance/
│   └── utils/
├── dist/             ← Gets published (compiled JS)
├── package.json      ← Version number lives here
└── tsconfig.json     ← Build configuration
```

**Never edit `dist/` directly** - it gets overwritten on build.

---

## THAT'S THE WHOLE FUCKING PROCESS

1. Edit `src/`
2. `npm version patch`
3. `npm run build`
4. `npm publish`

**DONE.**

