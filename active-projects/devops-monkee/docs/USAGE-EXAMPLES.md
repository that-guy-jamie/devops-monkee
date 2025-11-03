# DevOps Monkee Usage Examples

This document provides practical examples of how to use DevOps Monkee in your projects.

## Example 1: Basic Project Validation

Validate that your project meets SBEP compliance standards:

```bash
# Navigate to your project
cd ~/projects/my-ai-agent

# Run validation
dopm abide . --validate

# Output:
# ✅ Project structure: PASS
# ✅ Documentation: PASS
# ✅ Version sync: PASS
# ⚠️  Testing: 3 tests missing
# Score: 85/100 (Grade: B)
```

## Example 2: Version Synchronization

Keep all version references in sync across your project:

```bash
# Check current version status
dopm abide . --sync

# Output:
# Found 3 version conflicts:
# - README.md: v1.0.0 → v1.2.0
# - package.json: v1.0.0 → v1.2.0
# - docs/CHANGELOG.md: v1.0.0 → v1.2.0
# 
# Run with --force to apply updates

# Apply version updates
dopm abide . --sync --force

# Output:
# ✅ Updated 3 files
# All versions synchronized to v1.2.0
```

## Example 3: Repository Status Check

Check if your local repository is up-to-date with remote:

```bash
dopm abide . --sync

# Output:
# 📦 Repository Status:
# - Local branch: main
# - Remote: origin/main
# - Status: 2 commits behind
# - Last fetch: 2 hours ago
# 
# Use --auto-pull to sync with remote
```

## Example 4: Quality Audit

Run a comprehensive quality audit:

```bash
dopm abide . --audit

# Output:
# 📊 Quality Audit Report
# 
# Documentation: 90/100
#   ✅ README.md present
#   ✅ CHANGELOG.md present
#   ⚠️  API docs incomplete
# 
# Code Quality: 85/100
#   ✅ TypeScript configured
#   ✅ ESLint configured
#   ⚠️  Missing unit tests
# 
# Compliance: 88/100
#   ✅ SBEP structure present
#   ✅ Version manifest present
# 
# Overall Score: 88/100 (Grade: B+)
```

## Example 5: Programmatic API Usage

Use DevOps Monkee in your own Node.js scripts:

```typescript
import { Validator, Synchronizer, Auditor } from 'devops-monkee';

// Validate a project
const validator = new Validator();
const result = await validator.validate('./my-project');

console.log(`Score: ${result.score}/100`);
console.log(`Grade: ${result.grade}`);
result.issues.forEach(issue => {
  console.log(`${issue.severity}: ${issue.message}`);
});

// Synchronize versions
const synchronizer = new Synchronizer();
const syncResult = await synchronizer.sync('./my-project', {
  force: true
});

console.log(`Updated ${syncResult.updated} files`);
console.log(`Skipped ${syncResult.skipped} files`);

// Run audit
const auditor = new Auditor();
const auditResult = await auditor.audit('./my-project');

console.log(`Audit Score: ${auditResult.score}/100`);
```

## Example 6: CI/CD Integration

Integrate DevOps Monkee into your CI/CD pipeline:

```yaml
# .github/workflows/ci.yml
name: CI
on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
      - run: npm ci
      - run: npm install -g devops-monkee
      - run: dopm abide . --validate
      - run: dopm abide . --sync --dry-run
```

## Example 7: Custom Validator Plugin

Create a custom validator for project-specific rules:

```typescript
import { IValidator, ValidationResult } from 'devops-monkee';

class CustomValidator implements IValidator {
  async validate(projectPath: string): Promise<ValidationResult> {
    // Your custom validation logic
    const issues = [];
    
    // Check for custom requirements
    if (!this.hasCustomConfig(projectPath)) {
      issues.push({
        severity: 'medium',
        category: 'configuration',
        message: 'Missing custom configuration file',
        file: 'custom.config.json',
        autoFixable: false
      });
    }
    
    return {
      score: issues.length === 0 ? 100 : 80,
      grade: issues.length === 0 ? 'A' : 'B',
      issues,
      recommendations: ['Add custom.config.json']
    };
  }
  
  getName(): string {
    return 'custom-validator';
  }
  
  getVersion(): string {
    return '1.0.0';
  }
  
  supportsAutoFix(): boolean {
    return false;
  }
  
  private hasCustomConfig(projectPath: string): boolean {
    // Implementation
    return false;
  }
}
```

## Example 8: Batch Processing

Process multiple projects at once:

```bash
# Process all SBEP projects in a directory
for project in ~/projects/*/; do
  echo "Validating $project"
  dopm abide "$project" --validate
done

# Or use a script
#!/bin/bash
projects=("project1" "project2" "project3")

for project in "${projects[@]}"; do
  echo "Processing $project..."
  dopm abide "./$project" --validate --audit --sync
done
```

## Example 9: Documentation Check

Ensure your project documentation is complete:

```bash
dopm abide . --docs

# Output:
# 📚 Documentation Audit
# 
# ✅ README.md: Present and complete
# ✅ CHANGELOG.md: Present and up-to-date
# ✅ LICENSE: Present (MIT)
# ⚠️  API docs: Missing
# ⚠️  CONTRIBUTING.md: Missing
# 
# Recommendations:
# - Add API documentation
# - Create CONTRIBUTING.md
```

## Example 10: Testing Verification

Check that your test suite is properly configured:

```bash
dopm abide . --test

# Output:
# 🧪 Testing Verification
# 
# ✅ Test directory: Present (tests/)
# ✅ Test framework: Jest configured
# ✅ Test coverage: 75% (target: 80%)
# ⚠️  Integration tests: Missing
# ⚠️  E2E tests: Missing
# 
# Recommendations:
# - Add integration tests
# - Add E2E tests
# - Increase coverage to 80%
```

## Common Use Cases

### New Project Setup
```bash
# Initialize SBEP compliance for a new project
dopm init ./my-new-project
dopm abide ./my-new-project --validate
```

### Pre-Release Check
```bash
# Run all checks before releasing
dopm abide . --validate --audit --docs --test --sync
```

### Version Update Workflow
```bash
# Update version across all files
dopm abide . --sync --force
git add .
git commit -m "chore: sync versions to v1.2.0"
git tag v1.2.0
```

### Continuous Monitoring
```bash
# Add to your daily workflow
dopm abide . --validate --sync
```

---

For more information, see the [main README](../README.md) and [SBEP Security Guidelines](./SBEP-SECURITY-GUIDELINES.md).

