// DevOps Monkee - SBEP Governance Layer
// Main entry point for programmatic usage

export { ValidationSchemaManager } from './utils/validation-schema';
export { VersionManifestManager } from './utils/version-manifest';
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

// Lazy-loaded class exports and factory functions to avoid circular dependencies
export function createValidator() {
  const { Validator } = require('./governance/validator');
  return new Validator();
}

export function createSynchronizer() {
  const { Synchronizer } = require('./governance/synchronizer');
  return new Synchronizer();
}

export function createAuditor() {
  const { Auditor } = require('./governance/auditor');
  return new Auditor();
}

export function createGovernor() {
  const { Governor } = require('./governance/governor');
  return new Governor();
}

// Re-export classes for TypeScript
export { Validator } from './governance/validator';
export { Synchronizer } from './governance/synchronizer';
export { Auditor } from './governance/auditor';
export { Governor } from './governance/governor';
