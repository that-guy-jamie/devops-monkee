import * as fs from 'fs-extra';
import * as path from 'path';

export interface ValidationSchema {
  schema: {
    name: string;
    version: string;
    description: string;
    governance_version: string;
  };
  validation_rules: {
    document_structure: {
      required_files: RequiredFile[];
      optional_files: string[];
    };
    version_consistency: {
      rules: ValidationRule[];
    };
    quality_metrics: QualityMetricsSchema;
    safety_compliance: SafetyComplianceSchema;
    exception_policy_compliance: ExceptionPolicySchema;
  };
  scoring_system: ScoringSystem;
  automated_checks: AutomatedChecks;
  remediation_actions: Record<string, RemediationAction>;
  exception_conditions: ExceptionConditions;
  metadata: SchemaMetadata;
}

export interface RequiredFile {
  path: string;
  description: string;
  required_sections?: string[];
  required_fields?: string[];
  minimum_length?: number;
}

export interface ValidationRule {
  name: string;
  description: string;
  check_type: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  pattern?: string;
  max_drift?: string;
}

export interface QualityMetricsSchema {
  documentation_completeness: {
    required_sections: number;
    minimum_word_count: number;
    cross_references_required: number;
    code_examples_required: number;
  };
  consistency_checks: {
    terminology_standardization: string[];
    formatting_standards: Record<string, string>;
  };
  technical_accuracy: {
    version_references_current: boolean;
    file_paths_exist: boolean;
    commands_executable: boolean;
    api_endpoints_accessible: boolean;
  };
}

export interface SafetyComplianceSchema {
  rollback_requirements: Record<string, string>;
  deprecation_workflow: Record<string, string>;
}

export interface ExceptionPolicySchema {
  required_policies: string[];
  policy_structure: Record<string, boolean>;
}

export interface ScoringSystem {
  categories: Record<string, ScoringCategory>;
  grade_thresholds: Record<string, GradeThreshold>;
}

export interface ScoringCategory {
  weight: number;
  criteria: string[];
}

export interface GradeThreshold {
  min: number;
  description: string;
}

export interface AutomatedChecks {
  pre_commit_hooks: string[];
  ci_cd_gates: string[];
  scheduled_audits: {
    frequency: string;
    scope: string;
    reporting: string;
  };
}

export interface RemediationAction {
  action: string;
  requires_approval: boolean;
  notification: string;
}

export interface ExceptionConditions {
  emergency_bypass: {
    conditions: string[];
    approval_required: string;
    audit_required: boolean;
    review_required: string;
  };
  legacy_systems: {
    conditions: string[];
    temporary_exemption: string;
    remediation_plan_required: boolean;
  };
}

export interface SchemaMetadata {
  created: string;
  last_updated: string;
  governance_version: string;
  validation_engine_version: string;
}

export class ValidationSchemaManager {
  private static instance: ValidationSchemaManager;
  private schema: ValidationSchema | null = null;
  private schemaPath: string;

  private constructor() {
    this.schemaPath = path.join(__dirname, '../../VALIDATION-SCHEMA.json');
  }

  static getInstance(): ValidationSchemaManager {
    if (!ValidationSchemaManager.instance) {
      ValidationSchemaManager.instance = new ValidationSchemaManager();
    }
    return ValidationSchemaManager.instance;
  }

  async loadSchema(): Promise<ValidationSchema> {
    if (this.schema) {
      return this.schema;
    }

    try {
      this.schema = await fs.readJson(this.schemaPath);
      if (!this.schema) {
        throw new Error('Validation schema is empty or invalid');
      }
      return this.schema;
    } catch (error) {
      throw new Error(`Failed to load validation schema: ${error}`);
    }
  }

  async saveSchema(schema: ValidationSchema): Promise<void> {
    try {
      await fs.writeJson(this.schemaPath, schema, { spaces: 2 });
      this.schema = schema;
    } catch (error) {
      throw new Error(`Failed to save validation schema: ${error}`);
    }
  }

  async getValidationRules(category?: string): Promise<any> {
    const schema = await this.loadSchema();

    if (category) {
      return schema.validation_rules[category as keyof typeof schema.validation_rules] || {};
    }

    return schema.validation_rules;
  }

  async getScoringWeights(): Promise<Record<string, number>> {
    const schema = await this.loadSchema();
    const weights: Record<string, number> = {};

    for (const [category, config] of Object.entries(schema.scoring_system.categories)) {
      weights[category] = config.weight;
    }

    return weights;
  }

  async calculateGrade(score: number): Promise<string> {
    const schema = await this.loadSchema();
    const thresholds = schema.scoring_system.grade_thresholds;

    for (const [grade, threshold] of Object.entries(thresholds)) {
      if (score >= threshold.min) {
        return grade;
      }
    }

    return 'F';
  }

  async getRemediationAction(issueType: string): Promise<RemediationAction | null> {
    const schema = await this.loadSchema();
    return schema.remediation_actions[issueType] || null;
  }

  async validateSchema(): Promise<{ valid: boolean; errors: string[] }> {
    const schema = await this.loadSchema();
    const errors: string[] = [];

    // Validate required fields
    if (!schema.schema.name) {
      errors.push('Schema name is required');
    }

    if (!schema.schema.version) {
      errors.push('Schema version is required');
    }

    // Validate scoring system adds up to 100
    const totalWeight = Object.values(schema.scoring_system.categories)
      .reduce((sum, cat) => sum + cat.weight, 0);

    if (totalWeight !== 100) {
      errors.push(`Scoring categories must total 100% (currently ${totalWeight}%)`);
    }

    // Validate grade thresholds are in descending order
    const thresholds = Object.values(schema.scoring_system.grade_thresholds)
      .map(t => t.min)
      .sort((a, b) => b - a);

    const originalThresholds = Object.values(schema.scoring_system.grade_thresholds)
      .map(t => t.min);

    if (JSON.stringify(thresholds) !== JSON.stringify(originalThresholds)) {
      errors.push('Grade thresholds must be in descending order');
    }

    return {
      valid: errors.length === 0,
      errors
    };
  }

  async updateValidationRule(category: string, ruleName: string, updates: Partial<ValidationRule>): Promise<void> {
    const schema = await this.loadSchema();

    const categoryRules = schema.validation_rules[category as keyof typeof schema.validation_rules];
    if (!categoryRules || !Array.isArray(categoryRules)) {
      throw new Error(`Invalid category: ${category}`);
    }

    const ruleIndex = (categoryRules as ValidationRule[]).findIndex(rule => rule.name === ruleName);
    if (ruleIndex === -1) {
      throw new Error(`Rule not found: ${ruleName} in category ${category}`);
    }

    (categoryRules as ValidationRule[])[ruleIndex] = {
      ...(categoryRules as ValidationRule[])[ruleIndex],
      ...updates
    };

    await this.saveSchema(schema);
  }
}

// Export singleton instance
export const VALIDATION_SCHEMA = ValidationSchemaManager.getInstance();
