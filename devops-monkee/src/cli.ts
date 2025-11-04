#!/usr/bin/env node

import { Command } from 'commander';
import { Validator } from './governance/validator';
import { Synchronizer } from './governance/synchronizer';
import { Auditor } from './governance/auditor';
import { Governor } from './governance/governor';
import { logger } from './utils/logger';

const program = new Command();

program
  .name('devops-monkee')
  .description('SBEP Protocol Governance Layer - Enterprise-grade AI agent operating framework')
  .version('1.0.0');

program
  .command('validate')
  .description('Validate SBEP compliance for a project or workspace')
  .argument('<path>', 'Path to project or workspace to validate')
  .option('-v, --verbose', 'Enable verbose output')
  .option('-f, --fix', 'Attempt to auto-fix validation issues')
  .option('-r, --report <file>', 'Generate detailed validation report')
  .action(async (path: string, options) => {
    try {
      logger.info(`Validating SBEP compliance for: ${path}`);

      const validator = new Validator();
      const results = await validator.validate(path, options);

      if (options.report) {
        await validator.generateReport(results, options.report);
        logger.info(`Validation report saved to: ${options.report}`);
      }

      if (results.score >= 90) {
        logger.success('✅ SBEP compliance validation passed!');
        process.exit(0);
      } else {
        logger.error('❌ SBEP compliance validation failed!');
        logger.info(`Score: ${results.score}/100`);
        logger.info('Run with --verbose for detailed issues');
        process.exit(1);
      }
    } catch (error) {
      logger.error('Validation failed:', error);
      process.exit(1);
    }
  });

program
  .command('sync')
  .description('Synchronize versions across SBEP components')
  .argument('<path>', 'Path to workspace to synchronize')
  .option('-d, --dry-run', 'Preview changes without applying them')
  .option('-f, --force', 'Force synchronization even with conflicts')
  .action(async (path: string, options) => {
    try {
      logger.info(`Synchronizing SBEP versions for: ${path}`);

      const synchronizer = new Synchronizer();
      const results = await synchronizer.sync(path, options);

      if (results.conflicts.length > 0 && !options.force) {
        logger.warn('Version conflicts detected:');
        results.conflicts.forEach(conflict => {
          logger.warn(`  ${conflict.file}: ${conflict.current} → ${conflict.target}`);
        });
        logger.info('Use --force to apply changes or resolve conflicts manually');
        process.exit(1);
      }

      logger.success('✅ Version synchronization completed!');
      logger.info(`Updated ${results.updated} files`);
    } catch (error) {
      logger.error('Synchronization failed:', error);
      process.exit(1);
    }
  });

program
  .command('audit')
  .description('Audit documentation quality and protocol adherence')
  .argument('<path>', 'Path to project or workspace to audit')
  .option('-t, --type <type>', 'Audit type: quality|compliance|security', 'quality')
  .option('-o, --output <file>', 'Output audit results to file')
  .action(async (path: string, options) => {
    try {
      logger.info(`Auditing ${options.type} for: ${path}`);

      const auditor = new Auditor();
      const results = await auditor.audit(path, options.type);

      if (options.output) {
        await auditor.saveResults(results, options.output);
        logger.info(`Audit results saved to: ${options.output}`);
      }

      logger.success('✅ Audit completed!');
      logger.info(`Overall score: ${results.score}/100`);
    } catch (error) {
      logger.error('Audit failed:', error);
      process.exit(1);
    }
  });

program
  .command('govern')
  .description('Check for governance violations and protocol drift')
  .argument('<path>', 'Path to workspace to govern')
  .option('-s, --strict', 'Enforce strict governance rules')
  .option('-a, --auto-fix', 'Automatically fix governance issues')
  .action(async (path: string, options) => {
    try {
      logger.info(`Checking governance compliance for: ${path}`);

      const governor = new Governor();
      const violations = await governor.checkCompliance(path, options);

      if (violations.length === 0) {
        logger.success('✅ Governance compliance verified!');
        return;
      }

      logger.warn(`Found ${violations.length} governance violations:`);
      violations.forEach((violation, index) => {
        logger.warn(`${index + 1}. ${violation.severity.toUpperCase()}: ${violation.message}`);
        if (violation.file) {
          logger.info(`   File: ${violation.file}`);
        }
      });

      if (options.autoFix && violations.some(v => v.autoFixable)) {
        logger.info('Attempting auto-fix for eligible violations...');
        const fixed = await governor.autoFix(violations);
        logger.success(`Auto-fixed ${fixed} violations`);
      }

      const criticalCount = violations.filter(v => v.severity === 'critical').length;
      if (criticalCount > 0) {
        logger.error(`❌ ${criticalCount} critical governance violations require immediate attention`);
        process.exit(1);
      }
    } catch (error) {
      logger.error('Governance check failed:', error);
      process.exit(1);
    }
  });

program
  .command('init')
  .description('Initialize SBEP governance for a new project')
  .argument('<path>', 'Path to initialize SBEP governance')
  .option('-t, --template <template>', 'SBEP template to use', 'default')
  .option('-f, --force', 'Overwrite existing SBEP files')
  .action(async (path: string, options) => {
    try {
      logger.info(`Initializing SBEP governance for: ${path}`);

      const governor = new Governor();
      await governor.init(path, options);

      logger.success('✅ SBEP governance initialized!');
      logger.info('Next steps:');
      logger.info('1. Customize sds/SBEP-MANDATE.md for your project');
      logger.info('2. Update sds/SBEP-INDEX.yaml with your documentation');
      logger.info('3. Run "devops-monkee validate ." to check compliance');
    } catch (error) {
      logger.error('Initialization failed:', error);
      process.exit(1);
    }
  });

program
  .command('status')
  .description('Show SBEP governance status for workspace')
  .argument('<path>', 'Path to check governance status')
  .action(async (path: string) => {
    try {
      const governor = new Governor();
      const status = await governor.getStatus(path);

      logger.info('SBEP Governance Status:');
      logger.info(`Protocol Version: ${status.protocolVersion}`);
      logger.info(`Governance Version: ${status.governanceVersion}`);
      logger.info(`Compliance Score: ${status.complianceScore}/100`);
      logger.info(`Last Audit: ${status.lastAudit || 'Never'}`);
      logger.info(`Files Tracked: ${status.trackedFiles}`);

      if (status.issues.length > 0) {
        logger.warn(`Issues Found: ${status.issues.length}`);
        status.issues.slice(0, 5).forEach(issue => {
          logger.warn(`  - ${issue}`);
        });
        if (status.issues.length > 5) {
          logger.info(`  ... and ${status.issues.length - 5} more`);
        }
      } else {
        logger.success('No issues found!');
      }
    } catch (error) {
      logger.error('Status check failed:', error);
      process.exit(1);
    }
  });

// Error handling
program.on('command:*', (unknownCommand) => {
  logger.error(`Unknown command: ${unknownCommand[0]}`);
  logger.info('Run "devops-monkee --help" for available commands');
  process.exit(1);
});

// Global error handler
process.on('uncaughtException', (error) => {
  logger.error('Uncaught exception:', error);
  process.exit(1);
});

process.on('unhandledRejection', (reason, promise) => {
  logger.error('Unhandled rejection at:', promise, 'reason:', reason);
  process.exit(1);
});

program.parse();
