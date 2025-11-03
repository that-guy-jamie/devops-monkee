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

// Types
export interface ValidationResult {
  score: number;
  grade: 'A' | 'B' | 'C' | 'D' | 'F';
  issues: ValidationIssue[];
  recommendations: string[];
}

export interface ValidationIssue {
  severity: 'critical' | 'high' | 'medium' | 'low';
  category: string;
  message: string;
  file?: string;
  line?: number;
  autoFixable?: boolean;
}

export interface SyncResult {
  updated: number;
  skipped: number;
  conflicts: VersionConflict[];
}

export interface VersionConflict {
  file: string;
  current: string;
  target: string;
  resolution?: 'update' | 'skip' | 'manual';
}

export interface AuditResult {
  score: number;
  categories: AuditCategory[];
  timestamp: Date;
}

export interface AuditCategory {
  name: string;
  score: number;
  issues: string[];
  recommendations: string[];
}

export interface GovernanceStatus {
  protocolVersion: string;
  governanceVersion: string;
  complianceScore: number;
  lastAudit?: Date;
  trackedFiles: number;
  issues: string[];
}

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

export function createValidator(): Validator {
  return new Validator();
}

export function createSynchronizer(): Synchronizer {
  return new Synchronizer();
}

export function createAuditor(): Auditor {
  return new Auditor();
}

export function createGovernor(): Governor {
  return new Governor();
}
