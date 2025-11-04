import * as fs from 'fs-extra';
import * as path from 'path';
import { Validator } from './validator';
import { Synchronizer } from './synchronizer';
import { Auditor } from './auditor';
import { VERSION_MANIFEST } from '../utils/version-manifest';
import { logger } from '../utils/logger';
import { GovernanceStatus } from '../types';
import { IGovernor } from '../interfaces/tool-interfaces';

export interface GovernanceViolation {
  severity: 'critical' | 'high' | 'medium' | 'low';
  category: string;
  message: string;
  file?: string;
  autoFixable?: boolean;
  remediation?: string;
}

export class Governor implements IGovernor {
  private validator = new Validator();
  private synchronizer = new Synchronizer();
  private auditor = new Auditor();

  async checkCompliance(projectPath: string, options: any = {}): Promise<GovernanceViolation[]> {
    const violations: GovernanceViolation[] = [];

    try {
      // 1. Check version synchronization
      const syncValidation = await this.synchronizer.validateSync(projectPath);
      if (!syncValidation.valid) {
        violations.push(...syncValidation.issues.map(issue => ({
          severity: 'high' as const,
          category: 'version_sync',
          message: `Version synchronization issue: ${issue}`,
          remediation: 'Run "devops-monkee sync ." to synchronize versions'
        })));
      }

      // 2. Run validation
      const validationResult = await this.validator.validate(projectPath, { verbose: false });
      validationResult.issues.forEach(issue => {
        violations.push({
          severity: issue.severity,
          category: 'validation',
          message: issue.message,
          file: issue.file,
          autoFixable: issue.autoFixable
        });
      });

      // 3. Check for governance-specific issues
      const governanceIssues = await this.checkGovernanceSpecificIssues(projectPath);
      violations.push(...governanceIssues);

      // 4. Check exception policy compliance
      if (options.strict) {
        const exceptionIssues = await this.checkExceptionPolicyCompliance(projectPath);
        violations.push(...exceptionIssues);
      }

      // Log summary
      const criticalCount = violations.filter(v => v.severity === 'critical').length;
      const highCount = violations.filter(v => v.severity === 'high').length;

      logger.info(`Governance check complete: ${violations.length} violations found`);
      if (criticalCount > 0) logger.error(`${criticalCount} critical violations`);
      if (highCount > 0) logger.warn(`${highCount} high-priority violations`);

    } catch (error) {
      violations.push({
        severity: 'critical',
        category: 'governance_failure',
        message: `Governance check failed: ${error instanceof Error ? error.message : 'Unknown error'}`,
        remediation: 'Check system logs and retry governance check'
      });
    }

    return violations;
  }

  async getStatus(projectPath: string): Promise<GovernanceStatus> {
    try {
      const manifest = await VERSION_MANIFEST.loadManifest();

      // Get compliance score
      const violations = await this.checkCompliance(projectPath, { strict: false });
      const complianceScore = Math.max(0, 100 - (violations.length * 5));

      // Get tracked files count
      const trackedFiles = await this.countTrackedFiles(projectPath);

      // Get last audit date (simplified - would need proper tracking)
      const lastAudit = await this.getLastAuditDate(projectPath);

      return {
        protocolVersion: manifest.versions.protocol.current,
        governanceVersion: manifest.versions.governance.current,
        complianceScore,
        lastAudit,
        trackedFiles,
        issues: violations.map(v => v.message).slice(0, 10) // Limit to first 10
      };
    } catch (error) {
      logger.error('Failed to get governance status:', error);
      return {
        protocolVersion: 'unknown',
        governanceVersion: 'unknown',
        complianceScore: 0,
        trackedFiles: 0,
        issues: ['Failed to determine governance status']
      };
    }
  }

  async init(projectPath: string, options: any = {}): Promise<void> {
    const progress = logger.startProgress('Initializing SBEP governance');

    try {
      // Create SDS directory
      const sdsPath = path.join(projectPath, 'sds');
      await fs.ensureDir(sdsPath);
      progress.update('Created sds/ directory');

      // Create SBEP-MANDATE.md
      const mandatePath = path.join(sdsPath, 'SBEP-MANDATE.md');
      if (!await fs.pathExists(mandatePath) || options.force) {
        const mandateContent = await this.generateMandateTemplate(projectPath);
        await fs.writeFile(mandatePath, mandateContent);
        progress.update('Created SBEP-MANDATE.md');
      }

      // Create SBEP-INDEX.yaml
      const indexPath = path.join(sdsPath, 'SBEP-INDEX.yaml');
      if (!await fs.pathExists(indexPath) || options.force) {
        const indexContent = await this.generateIndexTemplate(projectPath);
        await fs.writeFile(indexPath, indexContent);
        progress.update('Created SBEP-INDEX.yaml');
      }

      // Create .tmp directory
      await fs.ensureDir(path.join(projectPath, '.tmp'));
      progress.update('Created .tmp/ directory');

      // Create archive directory
      await fs.ensureDir(path.join(projectPath, 'archive'));
      progress.update('Created archive/ directory');

      progress.complete('SBEP governance initialized successfully');
    } catch (error) {
      progress.fail(error instanceof Error ? error.message : 'Unknown error');
      throw error;
    }
  }

  async autoFix(violations: GovernanceViolation[]): Promise<number> {
    let fixed = 0;

    for (const violation of violations) {
      if (violation.autoFixable) {
        try {
          await this.fixViolation(violation);
          logger.success(`Auto-fixed: ${violation.message}`);
          fixed++;
        } catch (error) {
          logger.warn(`Failed to auto-fix: ${violation.message} - ${error}`);
        }
      }
    }

    return fixed;
  }

  private async checkGovernanceSpecificIssues(projectPath: string): Promise<GovernanceViolation[]> {
    const issues: GovernanceViolation[] = [];

    // Check for VERSION-MANIFEST.json
    const manifestPath = path.join(projectPath, 'VERSION-MANIFEST.json');
    if (!await fs.pathExists(manifestPath)) {
      issues.push({
        severity: 'critical',
        category: 'governance_core',
        message: 'VERSION-MANIFEST.json missing - required for version governance',
        file: 'VERSION-MANIFEST.json',
        remediation: 'Create VERSION-MANIFEST.json with current protocol versions'
      });
    }

    // Check VALIDATION-SCHEMA.json
    const schemaPath = path.join(projectPath, 'VALIDATION-SCHEMA.json');
    if (!await fs.pathExists(schemaPath)) {
      issues.push({
        severity: 'high',
        category: 'governance_core',
        message: 'VALIDATION-SCHEMA.json missing - required for validation rules',
        file: 'VALIDATION-SCHEMA.json',
        remediation: 'Copy VALIDATION-SCHEMA.json from governance layer'
      });
    }

    // Check for governance documentation
    const governanceFiles = [
      'GOVERNANCE-LAYER.md',
      'CONSTITUTION.md',
      'CHANGE-MANAGEMENT.md'
    ];

    for (const file of governanceFiles) {
      const filePath = path.join(projectPath, file);
      if (!await fs.pathExists(filePath)) {
        issues.push({
          severity: 'medium',
          category: 'governance_docs',
          message: `Governance documentation missing: ${file}`,
          file,
          remediation: 'Copy governance documentation from DevOps Monkee package'
        });
      }
    }

    return issues;
  }

  private async checkExceptionPolicyCompliance(projectPath: string): Promise<GovernanceViolation[]> {
    const issues: GovernanceViolation[] = [];

    // Check if any exceptions are currently active
    const exceptionDir = path.join(projectPath, 'SBEP_Core', 'EXCEPTION-POLICIES');
    if (await fs.pathExists(exceptionDir)) {
      const files = await fs.readdir(exceptionDir);
      const activeExceptions = files.filter(f => f.endsWith('.active'));

      if (activeExceptions.length > 0) {
        issues.push({
          severity: 'medium',
          category: 'exception_policy',
          message: `Active exception policies found: ${activeExceptions.join(', ')}`,
          remediation: 'Review and sunset expired exception policies'
        });
      }
    }

    return issues;
  }

  private async countTrackedFiles(projectPath: string): Promise<number> {
    try {
      const sdsPath = path.join(projectPath, 'sds');
      if (!await fs.pathExists(sdsPath)) return 0;

      const files = await fs.readdir(sdsPath);
      return files.filter(f => f.endsWith('.md') || f.endsWith('.yaml') || f.endsWith('.json')).length;
    } catch {
      return 0;
    }
  }

  private async getLastAuditDate(projectPath: string): Promise<Date | undefined> {
    try {
      const auditLogPath = path.join(projectPath, '.tmp', 'governance-audit.log');
      if (await fs.pathExists(auditLogPath)) {
        const stat = await fs.stat(auditLogPath);
        return stat.mtime;
      }
    } catch {
      // Ignore errors
    }
    return undefined;
  }

  private async generateMandateTemplate(projectPath: string): Promise<string> {
    const projectName = path.basename(projectPath);
    const packageJsonPath = path.join(projectPath, 'package.json');

    let techStack = 'Node.js, TypeScript';
    if (await fs.pathExists(packageJsonPath)) {
      try {
        const packageJson = await fs.readJson(packageJsonPath);
        // Extract tech stack from dependencies (simplified)
        techStack = 'Node.js, TypeScript';
      } catch {
        // Use default
      }
    }

    return `# ${projectName} - SBEP Mandate v2.2

**Project-Specific Operating Instructions for AI Agents**

---

## Project Context

**Project Name:** ${projectName}
**Primary Language/Stack:** ${techStack}
**Key Integrations:** [Fill in project-specific integrations]
**Current Phase:** Development

---

## Quick Start for Agents

### Required Reading (In Order)

1. **This file** (\`sds/SBEP-MANDATE.md\`) - Project-specific agent instructions
2. **\`README.md\`** - Project overview, architecture, quick start
3. **\`sds/SBEP-INDEX.yaml\`** - Complete documentation inventory
4. **\`/projects/API-docs/\`** - Centralized API documentation (as needed)
5. **\`CHANGELOG.md\`** - Recent changes and current state

### Project-Specific Documentation Locations

- **Architecture:** \`docs/architecture/\` or \`docs/${projectName}-ARCHITECTURE.md\`
- **Operations:** \`ops/\` (deployment scripts, tasks, runbooks)
- **Integration Guides:** \`docs/integrations/\`
- **Work Orders:** \`workorders/\` (current tasks, priorities, completion status)

---

## Project-Specific Rules

### 1. Technology Stack Awareness

**${projectName} uses:**
- ${techStack}
- [Add database information]
- [Add hosting information]

**Before making changes:**
- Verify compatibility with existing dependencies
- Check \`package.json\` / \`composer.json\` / \`requirements.txt\`
- Review recent CHANGELOG entries for context

### 2. Integration-Specific Documentation

**API Documentation Locations:**

[Add project-specific API documentation references]

### 3. Deployment & Operations

**Deployment Method:** [Fill in deployment method]
**Hosting:** [Fill in hosting provider]
**CI/CD:** [Fill in CI/CD information]

**Deployment Scripts:**
- Located in: \`ops/\` or \`ops/tasks/\`
- Always use scripts, never manual deployment
- Verify with \`--dry-run\` or test environment first

### 4. Testing & Validation

**Before Committing Changes:**
- Run linter if configured
- Test in development/staging environment
- Update relevant tests
- Update CHANGELOG.md

**Testing Approach:**
[Add project-specific testing approach]

### 5. Documentation Maintenance

**When Adding Features:**
- Update \`README.md\` if user-facing
- Update \`CHANGELOG.md\` (follow existing format)
- Update \`sds/SBEP-INDEX.yaml\` if adding new docs
- Add inline code comments for complex logic

---

## Success Metrics

Agent performance is measured by:
- Documentation consulted before asking questions
- Methods attempted before requesting help
- Proper rollback plans for changes
- CHANGELOG updates
- Code quality and maintainability

---

**Remember:** This project's documentation is your source of truth. Read it, trust it, use it.
`;
  }

  private async generateIndexTemplate(projectPath: string): Promise<string> {
    const projectName = path.basename(projectPath);

    return `# ${projectName} - SBEP Documentation Index
# Version: 1.0
# Last Updated: ${new Date().toISOString().split('T')[0]}

title: "${projectName} - Project Documentation Index"
description: "Comprehensive index of all project documentation and resources"

# Core SBEP Documentation
core_documentation:
  mandate:
    path: "sds/SBEP-MANDATE.md"
    description: "Project-specific agent operating instructions"
    priority: "critical"
    exists: true

  index:
    path: "sds/SBEP-INDEX.yaml"
    description: "This documentation index"
    priority: "critical"
    exists: true

# Project Documentation
project_documentation:
  readme:
    path: "README.md"
    description: "Project overview and getting started"
    priority: "high"
    exists: false

  changelog:
    path: "CHANGELOG.md"
    description: "Change history and release notes"
    priority: "high"
    exists: false

  architecture:
    path: "docs/architecture/"
    description: "System architecture and design documents"
    priority: "medium"
    exists: false

# Operational Documentation
operations:
  deployment:
    path: "ops/"
    description: "Deployment scripts and operational procedures"
    priority: "high"
    exists: false

  housekeeping:
    path: "SBEP_Core/Invoke-ProjectHousekeeping.ps1"
    description: "Workspace organization and cleanup script"
    priority: "medium"
    exists: false

# Governance Documentation
governance:
  constitution:
    path: "CONSTITUTION.md"
    description: "SBEP constitutional principles"
    priority: "high"
    exists: false

  governance_layer:
    path: "GOVERNANCE-LAYER.md"
    description: "Governance layer implementation guide"
    priority: "high"
    exists: false

# Cross-Project References
cross_project_patterns:
  - pattern: "SBEP Protocol Implementation"
    reference_project: "devops-monkee"
    location: "https://github.com/devops-monkee/devops-monkee"
    description: "Official SBEP governance layer and tools"

# Development Guidelines
development:
  coding_standards:
    path: ".eslintrc.json"
    description: "Code linting and formatting rules"
    priority: "medium"
    exists: false

  testing:
    path: "tests/"
    description: "Test suites and testing documentation"
    priority: "medium"
    exists: false

# API Documentation References
api_documentation:
  centralized:
    path: "/projects/API-docs/"
    description: "Centralized API documentation repository"
    priority: "high"
    exists: false

# Work Orders and Planning
work_orders:
  active:
    path: "workorders/"
    description: "Active work orders and current tasks"
    priority: "medium"
    exists: false

  completed:
    path: "workorders/Completed Workorders/"
    description: "Completed work orders and delivery records"
    priority: "low"
    exists: false

# Temporary and Archive Locations
file_management:
  temporary:
    path: ".tmp/"
    description: "Temporary files and test outputs"
    priority: "low"
    exists: true

  archive:
    path: "archive/"
    description: "Archived files and deprecated content"
    priority: "low"
    exists: true

# Version Information
version_info:
  protocol: "2.2.0"
  governance: "1.0.0"
  last_updated: "${new Date().toISOString()}"

# Maintenance Notes
maintenance:
  last_review: "${new Date().toISOString().split('T')[0]}"
  next_review: "${new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]}"
  responsible: "Development Team"
`;
  }

  private async fixViolation(violation: GovernanceViolation): Promise<void> {
    switch (violation.category) {
      case 'validation':
        // Delegate to validator's auto-fix
        if (violation.file) {
          await this.validator.validate(path.dirname(violation.file), { fix: true });
        }
        break;

      case 'governance_core':
        if (violation.file === 'VERSION-MANIFEST.json') {
          // Copy from governance layer
          const sourcePath = path.join(__dirname, '../../VERSION-MANIFEST.json');
          const targetPath = path.join(process.cwd(), 'VERSION-MANIFEST.json');
          await fs.copy(sourcePath, targetPath);
        }
        break;

      default:
        throw new Error(`No auto-fix available for violation: ${violation.message}`);
    }
  }

  // IGovernor interface implementation
  getName(): string {
    return 'default-governor';
  }

  getVersion(): string {
    return '1.0.0';
  }
}
