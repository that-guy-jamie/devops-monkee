import * as fs from 'fs-extra';
import * as path from 'path';

export interface VersionManifest {
  manifest: {
    name: string;
    description: string;
    created: string;
    governance: string;
  };
  versions: {
    protocol: VersionInfo;
    governance: VersionInfo;
    components: Record<string, VersionInfo>;
  };
  compatibility: CompatibilityInfo;
  quality_metrics: QualityMetrics;
  distribution: DistributionInfo;
  governance: GovernanceInfo;
  validation: ValidationInfo;
  checksums: Record<string, string>;
}

export interface VersionInfo {
  current: string;
  previous?: string;
  released: string;
  status: 'stable' | 'beta' | 'deprecated';
}

export interface CompatibilityInfo {
  minimum_agent_version: string;
  supported_node_versions: string[];
  breaking_changes: BreakingChange[];
  deprecated_features: DeprecatedFeature[];
}

export interface BreakingChange {
  version: string;
  description: string;
  migration_guide: string;
  deprecated_date: string;
}

export interface DeprecatedFeature {
  feature: string;
  replaced_by: string;
  removal_version: string;
  removal_date: string;
}

export interface QualityMetrics {
  documentation_completeness: {
    required_sections: number;
    minimum_word_count: number;
    cross_references_required: number;
    code_examples_required: number;
  };
  code_quality: {
    test_coverage: number;
    linting_rules: number;
    type_safety: string;
  };
}

export interface DistributionInfo {
  npm_package: string;
  github_repository: string;
  documentation_site: string;
  changelog: string;
}

export interface GovernanceInfo {
  last_audit: string;
  next_review: string;
  responsible_party: string;
  contact: string;
}

export interface ValidationInfo {
  last_validation: string;
  validation_status: 'passed' | 'failed';
  issues_found: number;
  warnings: number;
}

export class VersionManifestManager {
  private static instance: VersionManifestManager;
  private manifest: VersionManifest | null = null;
  private manifestPath: string;

  private constructor() {
    this.manifestPath = path.join(__dirname, '../../VERSION-MANIFEST.json');
  }

  static getInstance(): VersionManifestManager {
    if (!VersionManifestManager.instance) {
      VersionManifestManager.instance = new VersionManifestManager();
    }
    return VersionManifestManager.instance;
  }

  async loadManifest(): Promise<VersionManifest> {
    if (this.manifest) {
      return this.manifest;
    }

    try {
      this.manifest = await fs.readJson(this.manifestPath);
      return this.manifest;
    } catch (error) {
      throw new Error(`Failed to load version manifest: ${error}`);
    }
  }

  async saveManifest(manifest: VersionManifest): Promise<void> {
    try {
      await fs.writeJson(this.manifestPath, manifest, { spaces: 2 });
      this.manifest = manifest;
    } catch (error) {
      throw new Error(`Failed to save version manifest: ${error}`);
    }
  }

  async getVersion(component: string): Promise<string | null> {
    const manifest = await this.loadManifest();

    if (component === 'protocol') {
      return manifest.versions.protocol.current;
    }

    if (component === 'governance') {
      return manifest.versions.governance.current;
    }

    return manifest.versions.components[component]?.current || null;
  }

  async updateVersion(component: string, newVersion: string, releasedDate?: string): Promise<void> {
    const manifest = await this.loadManifest();

    if (component === 'protocol') {
      manifest.versions.protocol.previous = manifest.versions.protocol.current;
      manifest.versions.protocol.current = newVersion;
      manifest.versions.protocol.released = releasedDate || new Date().toISOString().split('T')[0];
    } else if (component === 'governance') {
      manifest.versions.governance.previous = manifest.versions.governance.current;
      manifest.versions.governance.current = newVersion;
      manifest.versions.governance.released = releasedDate || new Date().toISOString().split('T')[0];
    } else if (manifest.versions.components[component]) {
      manifest.versions.components[component].previous = manifest.versions.components[component].current;
      manifest.versions.components[component].current = newVersion;
      manifest.versions.components[component].last_sync = new Date().toISOString();
    }

    await this.saveManifest(manifest);
  }

  async validateVersion(version: string): Promise<boolean> {
    const semverPattern = /^\d+\.\d+\.\d+$/;
    return semverPattern.test(version);
  }

  async checkCompatibility(version: string, component: string): Promise<{ compatible: boolean; issues: string[] }> {
    const manifest = await this.loadManifest();
    const issues: string[] = [];

    // Check if version is deprecated
    const deprecated = manifest.compatibility.deprecated_features.find(
      df => df.feature === component && df.removal_version <= version
    );

    if (deprecated) {
      issues.push(`Component ${component} is deprecated as of version ${deprecated.removal_version}`);
    }

    // Check breaking changes
    const breakingChange = manifest.compatibility.breaking_changes.find(
      bc => bc.version === version
    );

    if (breakingChange) {
      issues.push(`Breaking change in ${version}: ${breakingChange.description}`);
    }

    return {
      compatible: issues.length === 0,
      issues
    };
  }

  async getBreakingChanges(sinceVersion?: string): Promise<BreakingChange[]> {
    const manifest = await this.loadManifest();

    if (!sinceVersion) {
      return manifest.compatibility.breaking_changes;
    }

    // Filter breaking changes since the specified version
    return manifest.compatibility.breaking_changes.filter(
      bc => bc.version > sinceVersion
    );
  }
}

// Export singleton instance
export const VERSION_MANIFEST = VersionManifestManager.getInstance();
