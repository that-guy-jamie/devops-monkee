// DevOps Monkee - SBEP Governance Layer
// Main entry point for programmatic usage

export { Validator } from './governance/validator';
export { Synchronizer } from './governance/synchronizer';
export { Auditor } from './governance/auditor';
export { Governor } from './governance/governor';

// Tool interfaces for plugin architecture
export { 
  IValidator, 
  ISynchronizer, 
  IAuditor, 
  IGovernor 
} from './interfaces/tool-interfaces';

// Configuration system
export { ConfigLoader, DevOpsMonkeeConfig } from './utils/config-loader';

export { VERSION_MANIFEST } from './utils/version-manifest';
export { VALIDATION_SCHEMA } from './utils/validation-schema';
export { logger } from './utils/logger';

// Types - re-export from types file
export type {
  ValidationResult,
  ValidationIssue,
  SyncResult,
  VersionConflict,
  AuditResult,
  AuditCategory,
  GovernanceStatus
} from './types';

// Constants
export const GOVERNANCE_VERSION = '1.0.0';
export const PROTOCOL_VERSION = '2.2.0';
export const CLI_NAME = 'devops-monkee';

// Utility functions
export function getVersion(): string {
  return GOVERNANCE_VERSION;
}

export function getProtocolVersion(): string {
  return PROTOCOL_VERSION;
}

import { Validator as ValidatorClass } from './governance/validator';
import { Synchronizer as SynchronizerClass } from './governance/synchronizer';
import { Auditor as AuditorClass } from './governance/auditor';
import { Governor as GovernorClass } from './governance/governor';

export function createValidator(): ValidatorClass {
  return new ValidatorClass();
}

export function createSynchronizer(): SynchronizerClass {
  return new SynchronizerClass();
}

export function createAuditor(): AuditorClass {
  return new AuditorClass();
}

export function createGovernor(): GovernorClass {
  return new GovernorClass();
}
