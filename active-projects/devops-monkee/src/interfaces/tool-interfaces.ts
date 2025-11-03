// Tool Interfaces for Plugin Architecture
// These interfaces allow tools to be replaced with custom implementations

import { ValidationResult, ValidationIssue } from '../index';
import { SyncResult, VersionConflict } from '../index';
import { AuditResult, AuditCategory } from '../index';
import { GovernanceStatus } from '../index';

/**
 * Interface for validators
 * Allows custom validation logic while maintaining compatibility
 */
export interface IValidator {
  /**
   * Validate SBEP compliance for a project
   */
  validate(projectPath: string, options?: any): Promise<ValidationResult>;
  
  /**
   * Get validator name for identification
   */
  getName(): string;
  
  /**
   * Get validator version
   */
  getVersion(): string;
  
  /**
   * Check if validator supports auto-fix
   */
  supportsAutoFix(): boolean;
}

/**
 * Interface for synchronizers
 * Handles version synchronization across project files
 */
export interface ISynchronizer {
  /**
   * Synchronize versions across all files
   */
  sync(projectPath: string, options?: any): Promise<SyncResult>;
  
  /**
   * Preview sync changes without applying
   */
  preview(projectPath: string, options?: any): Promise<SyncResult>;
  
  /**
   * Get synchronizer name
   */
  getName(): string;
  
  /**
   * Get synchronizer version
   */
  getVersion(): string;
}

/**
 * Interface for auditors
 * Performs comprehensive governance audits
 */
export interface IAuditor {
  /**
   * Perform governance audit
   */
  audit(projectPath: string, options?: any): Promise<AuditResult>;
  
  /**
   * Generate audit report
   */
  generateReport(result: AuditResult, outputPath: string): Promise<void>;
  
  /**
   * Get auditor name
   */
  getName(): string;
  
  /**
   * Get auditor version
   */
  getVersion(): string;
}

/**
 * Interface for governors
 * Provides overall governance oversight
 */
export interface IGovernor {
  /**
   * Get governance status for project
   */
  getStatus(projectPath: string, options?: any): Promise<GovernanceStatus>;
  
  /**
   * Initialize governance for new project
   */
  init(projectPath: string, options?: any): Promise<void>;
  
  /**
   * Get governor name
   */
  getName(): string;
  
  /**
   * Get governor version
   */
  getVersion(): string;
}

