import * as fs from 'fs-extra';
import * as path from 'path';
import * as glob from 'glob';
import { VALIDATION_SCHEMA, ValidationSchema } from '../utils/validation-schema';
import { VERSION_MANIFEST } from '../utils/version-manifest';
import { logger } from '../utils/logger';
import { ValidationResult, ValidationIssue } from '../types';
import { ConfigLoader } from '../utils/config-loader';
import { IValidator } from '../interfaces/tool-interfaces';

export class Validator implements IValidator {
  private schemaManager = VALIDATION_SCHEMA;
  private schema: ValidationSchema | null = null;
  
  /**
   * Load schema from project config or use default
   */
  private async loadSchema(projectPath: string): Promise<ValidationSchema> {
    if (this.schema) {
      return this.schema;
    }
    
    const customSchemaPath = await ConfigLoader.getCustomSchemaPath(projectPath);
    
    if (customSchemaPath) {
      try {
        const customSchema = await fs.readJson(customSchemaPath);
        logger.info(`Using custom validation schema from: ${customSchemaPath}`);
        this.schema = customSchema as ValidationSchema;
        return this.schema;
      } catch (error) {
        logger.warn(`Failed to load custom schema, using default:`, error);
      }
    }
    
    this.schema = await this.schemaManager.loadSchema();
    return this.schema;
  }

  async validate(projectPath: string, options: any = {}): Promise<ValidationResult> {
    logger.info('Starting SBEP compliance validation...');
    
    // Load custom schema if available
    this.schema = await this.loadSchema(projectPath);

    const issues: ValidationIssue[] = [];
    let totalScore = 0;

    // 1. Document Structure Validation
    const structureScore = await this.validateDocumentStructure(projectPath);
    totalScore += structureScore.score * 0.25; // 25% weight
    issues.push(...structureScore.issues);

    // 2. Version Consistency Check
    const versionScore = await this.validateVersionConsistency(projectPath);
    totalScore += versionScore.score * 0.20; // 20% weight
    issues.push(...versionScore.issues);

    // 3. Quality Metrics Assessment
    const qualityScore = await this.validateQualityMetrics(projectPath);
    totalScore += qualityScore.score * 0.25; // 25% weight
    issues.push(...qualityScore.issues);

    // 4. Safety Compliance Check
    const safetyScore = await this.validateSafetyCompliance(projectPath);
    totalScore += safetyScore.score * 0.15; // 15% weight
    issues.push(...safetyScore.issues);

    // 5. Exception Policy Validation
    const exceptionScore = await this.validateExceptionPolicies(projectPath);
    totalScore += exceptionScore.score * 0.15; // 15% weight
    issues.push(...exceptionScore.issues);

    const score = Math.round(totalScore);
    const grade = await this.calculateGrade(score, projectPath);

    const result: ValidationResult = {
      score,
      grade,
      issues,
      recommendations: this.generateRecommendations(issues)
    };

    if (options.verbose || options.fix) {
      this.logDetailedResults(result);
    }

    if (options.fix) {
      await this.attemptAutoFixes(issues, projectPath);
    }

    return result;
  }

  private async validateDocumentStructure(projectPath: string): Promise<{ score: number; issues: ValidationIssue[] }> {
    const issues: ValidationIssue[] = [];
    let score = 100;

    const schema = await this.loadSchema(projectPath);
    // Check required files
    for (const requiredFile of schema.validation_rules.document_structure.required_files) {
      const filePath = path.join(projectPath, requiredFile.path);

      if (!await fs.pathExists(filePath)) {
        issues.push({
          severity: 'critical',
          category: 'document_structure',
          message: `Required file missing: ${requiredFile.path}`,
          file: requiredFile.path
        });
        score -= 20;
        continue;
      }

      // Check required sections
      if (requiredFile.required_sections) {
        const content = await fs.readFile(filePath, 'utf-8');
        for (const section of requiredFile.required_sections) {
          if (!content.includes(`## ${section}`)) {
            issues.push({
              severity: 'high',
              category: 'document_structure',
              message: `Required section missing: ${section} in ${requiredFile.path}`,
              file: requiredFile.path
            });
            score -= 5;
          }
        }
      }
    }

    // Check for obsolete files
    const obsoletePatterns = ['*cheatsheet*.md', '*deprecated*.md', '*old*.md'];
    for (const pattern of obsoletePatterns) {
      const matches = glob.sync(pattern, { cwd: projectPath });
      if (matches.length > 0) {
        issues.push({
          severity: 'medium',
          category: 'document_structure',
          message: `Obsolete files found: ${matches.join(', ')} - should be archived`,
          autoFixable: true
        });
        score -= 2;
      }
    }

    return { score: Math.max(0, score), issues };
  }

  private async validateVersionConsistency(projectPath: string): Promise<{ score: number; issues: ValidationIssue[] }> {
    const issues: ValidationIssue[] = [];
    let score = 100;

    // Check version manifest exists
    const manifestPath = path.join(projectPath, 'VERSION-MANIFEST.json');
    if (!await fs.pathExists(manifestPath)) {
      issues.push({
        severity: 'critical',
        category: 'version_consistency',
        message: 'VERSION-MANIFEST.json missing - single source of truth for versions',
        file: 'VERSION-MANIFEST.json'
      });
      score -= 30;
      return { score, issues };
    }

    // Validate version format and consistency
    const manifest = await fs.readJson(manifestPath);
    const loadedManifest = await VERSION_MANIFEST.loadManifest();
    const currentVersions = loadedManifest.versions;

    // Check protocol version
    if (manifest.versions?.protocol?.current !== currentVersions.protocol.current) {
      issues.push({
        severity: 'high',
        category: 'version_consistency',
        message: `Protocol version mismatch: ${manifest.versions.protocol.current} vs ${currentVersions.protocol.current}`,
        file: 'VERSION-MANIFEST.json',
        autoFixable: true
      });
      score -= 15;
    }

    // Check semantic versioning
    const semverPattern = /^\d+\.\d+\.\d+$/;
    for (const [component, versionInfo] of Object.entries(manifest.versions?.components || {})) {
      if (versionInfo && typeof versionInfo === 'object' && 'current' in versionInfo) {
        const version = (versionInfo as any).current;
        if (typeof version === 'string' && !semverPattern.test(version)) {
          issues.push({
            severity: 'medium',
            category: 'version_consistency',
            message: `Invalid semantic version for ${component}: ${version}`,
            file: 'VERSION-MANIFEST.json'
          });
          score -= 5;
        }
      }
    }

    return { score: Math.max(0, score), issues };
  }

  private async validateQualityMetrics(projectPath: string): Promise<{ score: number; issues: ValidationIssue[] }> {
    const issues: ValidationIssue[] = [];
    let score = 100;

    const metrics = (await this.loadSchema(projectPath)).validation_rules.quality_metrics;

    // Check documentation completeness
    const readmePath = path.join(projectPath, 'README.md');
    if (await fs.pathExists(readmePath)) {
      const content = await fs.readFile(readmePath, 'utf-8');
      const wordCount = content.split(/\s+/).length;

      if (wordCount < metrics.documentation_completeness.minimum_word_count) {
        issues.push({
          severity: 'medium',
          category: 'quality_metrics',
          message: `README.md too short: ${wordCount} words (minimum: ${metrics.documentation_completeness.minimum_word_count})`,
          file: 'README.md'
        });
        score -= 10;
      }

      // Check for required sections
      const requiredSections = ['## Overview', '## Installation', '## Usage'];
      for (const section of requiredSections) {
        if (!content.includes(section)) {
          issues.push({
            severity: 'low',
            category: 'quality_metrics',
            message: `Missing recommended section in README.md: ${section}`,
            file: 'README.md',
            autoFixable: true
          });
          score -= 2;
        }
      }
    }

    // Check cross-references
    const docsPath = path.join(projectPath, 'sds');
    if (await fs.pathExists(docsPath)) {
      const mandatePath = path.join(docsPath, 'SBEP-MANDATE.md');
      const indexPath = path.join(docsPath, 'SBEP-INDEX.yaml');

      if (await fs.pathExists(mandatePath) && await fs.pathExists(indexPath)) {
        const mandateContent = await fs.readFile(mandatePath, 'utf-8');
        const indexContent = await fs.readFile(indexPath, 'utf-8');

        // Check if mandate references index and vice versa
        if (!mandateContent.includes('SBEP-INDEX.yaml') || !indexContent.includes('SBEP-MANDATE.md')) {
          issues.push({
            severity: 'low',
            category: 'quality_metrics',
            message: 'Missing cross-references between SBEP-MANDATE.md and SBEP-INDEX.yaml',
            autoFixable: true
          });
          score -= 5;
        }
      }
    }

    return { score: Math.max(0, score), issues };
  }

  private async validateSafetyCompliance(projectPath: string): Promise<{ score: number; issues: ValidationIssue[] }> {
    const issues: ValidationIssue[] = [];
    let score = 100;

    // Check for rollback documentation
    const hasOpsDir = await fs.pathExists(path.join(projectPath, 'ops'));
    if (!hasOpsDir) {
      issues.push({
        severity: 'high',
        category: 'safety_compliance',
        message: 'Missing ops/ directory - required for deployment and rollback procedures',
        file: 'ops/'
      });
      score -= 20;
    }

    // Check for housekeeping script
    const housekeepingScript = path.join(projectPath, 'SBEP_Core', 'Invoke-ProjectHousekeeping.ps1');
    if (!await fs.pathExists(housekeepingScript)) {
      issues.push({
        severity: 'medium',
        category: 'safety_compliance',
        message: 'Housekeeping script missing - required for workspace organization',
        file: 'SBEP_Core/Invoke-ProjectHousekeeping.ps1'
      });
      score -= 10;
    }

    // Check for archive directory
    const hasArchive = await fs.pathExists(path.join(projectPath, 'archive'));
    if (!hasArchive) {
      issues.push({
        severity: 'low',
        category: 'safety_compliance',
        message: 'Missing archive/ directory - required for safe file deprecation',
        file: 'archive/',
        autoFixable: true
      });
      score -= 5;
    }

    return { score: Math.max(0, score), issues };
  }

  private async validateExceptionPolicies(projectPath: string): Promise<{ score: number; issues: ValidationIssue[] }> {
    const issues: ValidationIssue[] = [];
    let score = 100;

    const schema = await this.loadSchema(projectPath);
    const requiredPolicies = schema.validation_rules.exception_policy_compliance.required_policies;

    for (const policy of requiredPolicies) {
      const policyPath = path.join(projectPath, 'SBEP_Core', 'EXCEPTION-POLICIES', `${policy}.md`);

      if (!await fs.pathExists(policyPath)) {
        issues.push({
          severity: 'high',
          category: 'exception_policies',
          message: `Required exception policy missing: ${policy}`,
          file: `SBEP_Core/EXCEPTION-POLICIES/${policy}.md`
        });
        score -= 15;
      } else {
        // Validate policy structure
        const content = await fs.readFile(policyPath, 'utf-8');
        const structure = schema.validation_rules.exception_policy_compliance.policy_structure;

        for (const [section, required] of Object.entries(structure)) {
          if (required && !content.includes(`## ${section.charAt(0).toUpperCase() + section.slice(1)}`)) {
            issues.push({
              severity: 'medium',
              category: 'exception_policies',
              message: `Policy structure incomplete: missing ${section} in ${policy}`,
              file: policyPath
            });
            score -= 5;
          }
        }
      }
    }

    return { score: Math.max(0, score), issues };
  }

  private async calculateGrade(score: number, projectPath: string): Promise<'A' | 'B' | 'C' | 'D' | 'F'> {
    const schema = await this.loadSchema(projectPath);
    const thresholds = schema.scoring_system.grade_thresholds;
    if (score >= thresholds.A.min) return 'A';
    if (score >= thresholds.B.min) return 'B';
    if (score >= thresholds.C.min) return 'C';
    if (score >= thresholds.D.min) return 'D';
    return 'F';
  }

  private generateRecommendations(issues: ValidationIssue[]): string[] {
    const recommendations: string[] = [];

    const criticalCount = issues.filter(i => i.severity === 'critical').length;
    const highCount = issues.filter(i => i.severity === 'high').length;

    if (criticalCount > 0) {
      recommendations.push(`Address ${criticalCount} critical issues immediately - these prevent basic SBEP compliance`);
    }

    if (highCount > 0) {
      recommendations.push(`Fix ${highCount} high-priority issues to achieve basic functionality`);
    }

    // Category-specific recommendations
    const categories = [...new Set(issues.map(i => i.category))];
    for (const category of categories) {
      const categoryIssues = issues.filter(i => i.category === category);
      recommendations.push(...this.getCategoryRecommendations(category, categoryIssues));
    }

    return recommendations;
  }

  private getCategoryRecommendations(category: string, issues: ValidationIssue[]): string[] {
    const recommendations: string[] = [];

    switch (category) {
      case 'document_structure':
        recommendations.push('Ensure all required SBEP documentation files are present and properly structured');
        break;
      case 'version_consistency':
        recommendations.push('Synchronize all version references to use VERSION-MANIFEST.json as single source of truth');
        break;
      case 'quality_metrics':
        recommendations.push('Improve documentation completeness and cross-referencing');
        break;
      case 'safety_compliance':
        recommendations.push('Implement proper rollback procedures and housekeeping processes');
        break;
      case 'exception_policies':
        recommendations.push('Create and maintain required exception policies for edge cases');
        break;
    }

    return recommendations;
  }

  private logDetailedResults(result: ValidationResult): void {
    logger.info(`\nValidation Score: ${result.score}/100 (Grade: ${result.grade})`);
    logger.info(`Total Issues: ${result.issues.length}`);

    const bySeverity = result.issues.reduce((acc, issue) => {
      acc[issue.severity] = (acc[issue.severity] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    Object.entries(bySeverity).forEach(([severity, count]) => {
      logger.info(`  ${severity.toUpperCase()}: ${count}`);
    });

    if (result.recommendations.length > 0) {
      logger.info('\nRecommendations:');
      result.recommendations.forEach(rec => logger.info(`  • ${rec}`));
    }
  }

  private async attemptAutoFixes(issues: ValidationIssue[], projectPath: string): Promise<void> {
    const fixableIssues = issues.filter(issue => issue.autoFixable);
    logger.info(`Attempting to auto-fix ${fixableIssues.length} issues...`);

    for (const issue of fixableIssues) {
      try {
        await this.fixIssue(issue, projectPath);
        logger.success(`Fixed: ${issue.message}`);
      } catch (error) {
        logger.warn(`Failed to fix: ${issue.message} - ${error}`);
      }
    }
  }

  private async fixIssue(issue: ValidationIssue, projectPath: string): Promise<void> {
    switch (issue.category) {
      case 'document_structure':
        if (issue.message.includes('archive/')) {
          await fs.ensureDir(path.join(projectPath, 'archive'));
        }
        break;
      case 'quality_metrics':
        if (issue.message.includes('README.md') && issue.message.includes('recommended section')) {
          await this.addRecommendedSection(issue, projectPath);
        }
        break;
    }
  }

  private async addRecommendedSection(issue: ValidationIssue, projectPath: string): Promise<void> {
    const readmePath = path.join(projectPath, 'README.md');
    let content = await fs.readFile(readmePath, 'utf-8');

    if (issue.message.includes('Overview')) {
      content = `## Overview\n\n[Add project overview here]\n\n${content}`;
    } else if (issue.message.includes('Installation')) {
      content += '\n## Installation\n\n[Add installation instructions here]\n';
    } else if (issue.message.includes('Usage')) {
      content += '\n## Usage\n\n[Add usage examples here]\n';
    }

    await fs.writeFile(readmePath, content);
  }

  async generateReport(results: ValidationResult, outputPath: string): Promise<void> {
    const report = {
      timestamp: new Date().toISOString(),
      summary: {
        score: results.score,
        grade: results.grade,
        totalIssues: results.issues.length,
        issuesBySeverity: results.issues.reduce((acc, issue) => {
          acc[issue.severity] = (acc[issue.severity] || 0) + 1;
          return acc;
        }, {} as Record<string, number>)
      },
      issues: results.issues,
      recommendations: results.recommendations
    };

    await fs.writeJson(outputPath, report, { spaces: 2 });
  }

  // IValidator interface implementation
  getName(): string {
    return 'default-validator';
  }

  getVersion(): string {
    return '1.0.0';
  }

  supportsAutoFix(): boolean {
    return true;
  }
}
