import * as fs from 'fs-extra';
import * as path from 'path';
import { ValidationSchemaManager } from '../utils/validation-schema';
import { logger } from '../utils/logger';
import { AuditResult, AuditCategory } from '../index';

export class Auditor {
  private schemaManager = ValidationSchemaManager.getInstance();

  async audit(projectPath: string, type: string = 'quality'): Promise<AuditResult> {
    const startTime = Date.now();

    logger.info(`Starting ${type} audit for: ${projectPath}`);

    const categories: AuditCategory[] = [];

    switch (type) {
      case 'quality':
        categories.push(...await this.auditQualityMetrics(projectPath));
        break;
      case 'compliance':
        categories.push(...await this.auditCompliance(projectPath));
        break;
      case 'security':
        categories.push(...await this.auditSecurity(projectPath));
        break;
      case 'comprehensive':
        categories.push(
          ...await this.auditQualityMetrics(projectPath),
          ...await this.auditCompliance(projectPath),
          ...await this.auditSecurity(projectPath)
        );
        break;
      default:
        throw new Error(`Unknown audit type: ${type}`);
    }

    const totalScore = this.calculateTotalScore(categories);
    const totalIssues = categories.reduce((sum, cat) => sum + cat.issues.length, 0);

    const result: AuditResult = {
      score: totalScore,
      categories,
      timestamp: new Date()
    };

    const duration = Date.now() - startTime;
    logger.logAuditResult({
      type,
      score: totalScore,
      categories: categories.length,
      issues: totalIssues,
      duration
    });

    return result;
  }

  private async auditQualityMetrics(projectPath: string): Promise<AuditCategory[]> {
    const categories: AuditCategory[] = [];

    // Documentation Completeness
    const completeness = await this.auditDocumentationCompleteness(projectPath);
    categories.push(completeness);

    // Consistency Checks
    const consistency = await this.auditConsistency(projectPath);
    categories.push(consistency);

    // Technical Accuracy
    const accuracy = await this.auditTechnicalAccuracy(projectPath);
    categories.push(accuracy);

    return categories;
  }

  private async auditCompliance(projectPath: string): Promise<AuditCategory[]> {
    const categories: AuditCategory[] = [];

    // Protocol Adherence
    const adherence = await this.auditProtocolAdherence(projectPath);
    categories.push(adherence);

    // Safety Compliance
    const safety = await this.auditSafetyCompliance(projectPath);
    categories.push(safety);

    // Exception Policy Compliance
    const exceptions = await this.auditExceptionPolicies(projectPath);
    categories.push(exceptions);

    return categories;
  }

  private async auditSecurity(projectPath: string): Promise<AuditCategory[]> {
    const categories: AuditCategory[] = [];

    // Access Control
    const access = await this.auditAccessControl(projectPath);
    categories.push(access);

    // Data Protection
    const data = await this.auditDataProtection(projectPath);
    categories.push(data);

    // Dependency Security
    const dependencies = await this.auditDependencies(projectPath);
    categories.push(dependencies);

    return categories;
  }

  private async auditDocumentationCompleteness(projectPath: string): Promise<AuditCategory> {
    const issues: string[] = [];
    const recommendations: string[] = [];
    let score = 100;

    const schema = await this.schemaManager.loadSchema();
    const metrics = schema.validation_rules.quality_metrics.documentation_completeness;

    // Check README completeness
    const readmePath = path.join(projectPath, 'README.md');
    if (await fs.pathExists(readmePath)) {
      const content = await fs.readFile(readmePath, 'utf-8');
      const wordCount = content.split(/\s+/).length;

      if (wordCount < metrics.minimum_word_count) {
        issues.push(`README too short: ${wordCount} words (minimum: ${metrics.minimum_word_count})`);
        recommendations.push('Expand README with detailed project description, setup instructions, and usage examples');
        score -= 20;
      }

      // Check for required sections
      const requiredSections = ['## Overview', '## Installation', '## Usage'];
      for (const section of requiredSections) {
        if (!content.includes(section)) {
          issues.push(`Missing section: ${section}`);
          score -= 5;
        }
      }
    } else {
      issues.push('README.md missing');
      recommendations.push('Create comprehensive README.md with project overview, installation, and usage instructions');
      score -= 30;
    }

    // Check cross-references
    const docsPath = path.join(projectPath, 'sds');
    if (await fs.pathExists(docsPath)) {
      const mandatePath = path.join(docsPath, 'SBEP-MANDATE.md');
      const indexPath = path.join(docsPath, 'SBEP-INDEX.yaml');

      if (await fs.pathExists(mandatePath) && await fs.pathExists(indexPath)) {
        const mandateContent = await fs.readFile(mandatePath, 'utf-8');
        const indexContent = await fs.readFile(indexPath, 'utf-8');

        if (!mandateContent.includes('SBEP-INDEX.yaml')) {
          issues.push('SBEP-MANDATE.md missing reference to SBEP-INDEX.yaml');
          recommendations.push('Add cross-reference to SBEP-INDEX.yaml in mandate document');
          score -= 10;
        }
      }
    }

    return {
      name: 'Documentation Completeness',
      score,
      issues,
      recommendations
    };
  }

  private async auditConsistency(projectPath: string): Promise<AuditCategory> {
    const issues: string[] = [];
    const recommendations: string[] = [];
    let score = 100;

    const schema = await this.schemaManager.loadSchema();
    const standards = schema.validation_rules.quality_metrics.consistency_checks;

    // Check terminology standardization
    const docsPath = path.join(projectPath, 'sds');
    if (await fs.pathExists(docsPath)) {
      const files = await fs.readdir(docsPath);
      const mdFiles = files.filter(f => f.endsWith('.md'));

      for (const file of mdFiles) {
        const content = await fs.readFile(path.join(docsPath, file), 'utf-8');

        // Check for inconsistent terminology
        for (const term of standards.terminology_standardization) {
          const variations = this.findTermVariations(content, term);
          if (variations.length > 1) {
            issues.push(`Inconsistent terminology in ${file}: ${variations.join(', ')}`);
            recommendations.push(`Standardize on '${term}' throughout documentation`);
            score -= 5;
          }
        }
      }
    }

    return {
      name: 'Consistency',
      score,
      issues,
      recommendations
    };
  }

  private async auditTechnicalAccuracy(projectPath: string): Promise<AuditCategory> {
    const issues: string[] = [];
    const recommendations: string[] = [];
    let score = 100;

    // Check file path references
    const docsPath = path.join(projectPath, 'sds');
    if (await fs.pathExists(docsPath)) {
      const files = await fs.readdir(docsPath);
      const mdFiles = files.filter(f => f.endsWith('.md'));

      for (const file of mdFiles) {
        const content = await fs.readFile(path.join(docsPath, file), 'utf-8');
        const filePathRefs = this.extractFilePathReferences(content);

        for (const ref of filePathRefs) {
          if (!await fs.pathExists(path.join(projectPath, ref))) {
            issues.push(`Broken file reference in ${file}: ${ref}`);
            recommendations.push(`Fix or remove broken reference to ${ref}`);
            score -= 10;
          }
        }
      }
    }

    return {
      name: 'Technical Accuracy',
      score,
      issues,
      recommendations
    };
  }

  private async auditProtocolAdherence(projectPath: string): Promise<AuditCategory> {
    const issues: string[] = [];
    const recommendations: string[] = [];
    let score = 100;

    // Check for required SBEP components
    const requiredPaths = [
      'sds/SBEP-MANDATE.md',
      'sds/SBEP-INDEX.yaml',
      'SBEP_Core/'
    ];

    for (const requiredPath of requiredPaths) {
      if (!await fs.pathExists(path.join(projectPath, requiredPath))) {
        issues.push(`Missing required SBEP component: ${requiredPath}`);
        recommendations.push(`Create ${requiredPath} following SBEP standards`);
        score -= 25;
      }
    }

    return {
      name: 'Protocol Adherence',
      score,
      issues,
      recommendations
    };
  }

  private async auditSafetyCompliance(projectPath: string): Promise<AuditCategory> {
    const issues: string[] = [];
    const recommendations: string[] = [];
    let score = 100;

    // Check for rollback procedures
    const opsPath = path.join(projectPath, 'ops');
    if (!await fs.pathExists(opsPath)) {
      issues.push('Missing ops/ directory for deployment and rollback procedures');
      recommendations.push('Create ops/ directory with deployment scripts and rollback procedures');
      score -= 20;
    }

    // Check for housekeeping
    const housekeepingScript = path.join(projectPath, 'SBEP_Core', 'Invoke-ProjectHousekeeping.ps1');
    if (!await fs.pathExists(housekeepingScript)) {
      issues.push('Missing housekeeping script for workspace organization');
      recommendations.push('Implement SBEP housekeeping procedures');
      score -= 15;
    }

    return {
      name: 'Safety Compliance',
      score,
      issues,
      recommendations
    };
  }

  private async auditExceptionPolicies(projectPath: string): Promise<AuditCategory> {
    const issues: string[] = [];
    const recommendations: string[] = [];
    let score = 100;

    const schema = await this.schemaManager.loadSchema();
    const requiredPolicies = schema.validation_rules.exception_policy_compliance.required_policies;

    for (const policy of requiredPolicies) {
      const policyPath = path.join(projectPath, 'SBEP_Core', 'EXCEPTION-POLICIES', `${policy}.md`);

      if (!await fs.pathExists(policyPath)) {
        issues.push(`Missing required exception policy: ${policy}`);
        recommendations.push(`Create ${policy}.md following exception policy standards`);
        score -= 20;
      }
    }

    return {
      name: 'Exception Policies',
      score,
      issues,
      recommendations
    };
  }

  private async auditAccessControl(projectPath: string): Promise<AuditCategory> {
    const issues: string[] = [];
    const recommendations: string[] = [];
    let score = 100;

    // Check for sensitive files
    const sensitivePatterns = [
      '.env',
      'secrets.json',
      '*.key',
      '*.pem'
    ];

    for (const pattern of sensitivePatterns) {
      // This is a simplified check - in reality, you'd want more sophisticated pattern matching
      if (pattern === '.env' && await fs.pathExists(path.join(projectPath, '.env'))) {
        issues.push('Sensitive file .env found in repository');
        recommendations.push('Add .env to .gitignore and use .env.example template');
        score -= 25;
      }
    }

    return {
      name: 'Access Control',
      score,
      issues,
      recommendations
    };
  }

  private async auditDataProtection(projectPath: string): Promise<AuditCategory> {
    const issues: string[] = [];
    const recommendations: string[] = [];
    let score = 100;

    // Check for data handling documentation
    const docsPath = path.join(projectPath, 'docs');
    if (await fs.pathExists(docsPath)) {
      const dataFiles = ['data-policy.md', 'privacy.md', 'data-handling.md'];
      let hasDataDocs = false;

      for (const file of dataFiles) {
        if (await fs.pathExists(path.join(docsPath, file))) {
          hasDataDocs = true;
          break;
        }
      }

      if (!hasDataDocs) {
        issues.push('Missing data protection and privacy documentation');
        recommendations.push('Create data handling policy and privacy documentation');
        score -= 15;
      }
    }

    return {
      name: 'Data Protection',
      score,
      issues,
      recommendations
    };
  }

  private async auditDependencies(projectPath: string): Promise<AuditCategory> {
    const issues: string[] = [];
    const recommendations: string[] = [];
    let score = 100;

    // Check package.json for security issues (simplified check)
    const packagePath = path.join(projectPath, 'package.json');
    if (await fs.pathExists(packagePath)) {
      try {
        const packageJson = await fs.readJson(packagePath);

        // Check for outdated dependencies (simplified)
        if (packageJson.dependencies || packageJson.devDependencies) {
          issues.push('Dependency security audit recommended');
          recommendations.push('Run npm audit and update vulnerable dependencies');
          score -= 10;
        }
      } catch (error) {
        issues.push('Invalid package.json format');
        score -= 20;
      }
    }

    return {
      name: 'Dependency Security',
      score,
      issues,
      recommendations
    };
  }

  private calculateTotalScore(categories: AuditCategory[]): number {
    if (categories.length === 0) return 100;

    const totalScore = categories.reduce((sum, cat) => sum + cat.score, 0);
    return Math.round(totalScore / categories.length);
  }

  private findTermVariations(content: string, standardTerm: string): string[] {
    const variations: string[] = [];
    const lowerContent = content.toLowerCase();
    const lowerTerm = standardTerm.toLowerCase();

    // Simple variation detection - could be enhanced
    if (lowerContent.includes(lowerTerm)) {
      variations.push(standardTerm);
    }

    return variations;
  }

  private extractFilePathReferences(content: string): string[] {
    const references: string[] = [];
    const patterns = [
      /\[([^\]]+)\]\(([^)]+)\)/g,  // Markdown links
      /`([^`]+)`/g,  // Inline code
      /file:\/\/([^\s]+)/g  // File URLs
    ];

    for (const pattern of patterns) {
      let match;
      while ((match = pattern.exec(content)) !== null) {
        const ref = match[2] || match[1];
        if (ref && (ref.includes('/') || ref.includes('.md') || ref.includes('.json'))) {
          references.push(ref);
        }
      }
    }

    return [...new Set(references)];
  }

  async saveResults(results: AuditResult, outputPath: string): Promise<void> {
    const report = {
      timestamp: results.timestamp.toISOString(),
      summary: {
        overall_score: results.score,
        categories_audited: results.categories.length,
        total_issues: results.categories.reduce((sum, cat) => sum + cat.issues.length, 0),
        total_recommendations: results.categories.reduce((sum, cat) => sum + cat.recommendations.length, 0)
      },
      categories: results.categories
    };

    await fs.writeJson(outputPath, report, { spaces: 2 });
    logger.info(`Audit report saved to: ${outputPath}`);
  }
}
