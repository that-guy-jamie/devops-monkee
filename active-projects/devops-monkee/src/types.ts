// Type definitions for DevOps Monkee

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

