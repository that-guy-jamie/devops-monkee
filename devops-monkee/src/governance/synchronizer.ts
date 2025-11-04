import * as fs from 'fs-extra';
import * as path from 'path';
import * as glob from 'glob';
import { VERSION_MANIFEST } from '../utils/version-manifest';
import { logger } from '../utils/logger';
import { SyncResult, VersionConflict } from '../types';
import { ISynchronizer } from '../interfaces/tool-interfaces';

export class Synchronizer implements ISynchronizer {
  async sync(projectPath: string, options: any = {}): Promise<SyncResult> {
    const progress = logger.startProgress('Version synchronization');

    try {
      progress.update('Loading version manifest');
      const manifest = await VERSION_MANIFEST.loadManifest();

      progress.update('Scanning project files');
      const projectFiles = await this.scanProjectFiles(projectPath);

      progress.update('Analyzing version references');
      const conflicts = await this.analyzeVersionReferences(projectFiles, manifest, projectPath);

      let updated = 0;

      if (conflicts.length > 0 && !options.force) {
        progress.complete(`found ${conflicts.length} conflicts - use --force to resolve`);
        return {
          updated: 0,
          skipped: projectFiles.length,
          conflicts
        };
      }

      progress.update('Synchronizing versions');
      updated = await this.applyVersionUpdates(conflicts, projectPath, options.dryRun);

      progress.complete(`synchronized ${updated} files`);
      return {
        updated,
        skipped: projectFiles.length - updated,
        conflicts: []
      };
    } catch (error) {
      progress.fail(error instanceof Error ? error.message : 'Unknown error');
      throw error;
    }
  }

  private async scanProjectFiles(projectPath: string): Promise<string[]> {
    const patterns = [
      '**/*.md',
      '**/*.json',
      '**/*.yaml',
      '**/*.yml',
      '**/package.json',
      '**/composer.json'
    ];

    const files: string[] = [];

    for (const pattern of patterns) {
      const matches = glob.sync(pattern, {
        cwd: projectPath,
        ignore: [
          '**/node_modules/**',
          '**/.git/**',
          '**/dist/**',
          '**/build/**',
          '**/.tmp/**'
        ]
      });
      files.push(...matches);
    }

    return [...new Set(files)]; // Remove duplicates
  }

  private async analyzeVersionReferences(
    files: string[],
    manifest: any,
    projectPath: string
  ): Promise<VersionConflict[]> {
    const conflicts: VersionConflict[] = [];

    for (const file of files) {
      try {
        const filePath = path.join(projectPath, file);
        const content = await fs.readFile(filePath, 'utf-8');
        const fileConflicts = await this.checkFileForVersionIssues(content, file, manifest);

        conflicts.push(...fileConflicts);
      } catch (error) {
        logger.debug(`Skipping file ${file}: ${error}`);
      }
    }

    return conflicts;
  }

  private async checkFileForVersionIssues(
    content: string,
    filePath: string,
    manifest: any
  ): Promise<VersionConflict[]> {
    const conflicts: VersionConflict[] = [];
    const lines = content.split('\n');

    // Check for version references in various formats
    const versionPatterns = [
      // Markdown headers and text
      /SBEP v(\d+\.\d+\.\d+)/gi,
      /Protocol v(\d+\.\d+\.\d+)/gi,
      /Governance v(\d+\.\d+\.\d+)/gi,

      // JSON version fields
      /"version":\s*"(\d+\.\d+\.\d+)"/g,
      /"sbep-version":\s*"(\d+\.\d+\.\d+)"/g,

      // YAML version fields
      /^version:\s*(\d+\.\d+\.\d+)/gm,
      /^sbep_version:\s*(\d+\.\d+\.\d+)/gm,

      // Comments and documentation
      /Version:?\s*(\d+\.\d+\.\d+)/gi,
      /v(\d+\.\d+\.\d+)/g
    ];

    for (let lineIndex = 0; lineIndex < lines.length; lineIndex++) {
      const line = lines[lineIndex];

      for (const pattern of versionPatterns) {
        const matches = line.match(pattern);
        if (matches) {
          for (const match of matches) {
            // Extract version number from match
            const versionMatch = match.match(/(\d+\.\d+\.\d+)/);
            if (versionMatch) {
              const foundVersion = versionMatch[1];
              const expectedVersion = this.getExpectedVersion(match, manifest);

              if (expectedVersion && foundVersion !== expectedVersion) {
                conflicts.push({
                  file: filePath,
                  current: foundVersion,
                  target: expectedVersion,
                  resolution: 'update'
                });
              }
            }
          }
        }
      }
    }

    return conflicts;
  }

  private getExpectedVersion(text: string, manifest: any): string | null {
    if (text.includes('Protocol') || text.includes('SBEP v')) {
      return manifest.versions.protocol.current;
    }

    if (text.includes('Governance')) {
      return manifest.versions.governance.current;
    }

    // Check component versions
    for (const [component, info] of Object.entries(manifest.versions.components)) {
      if (text.toLowerCase().includes(component.toLowerCase())) {
        return (info as any).current;
      }
    }

    return null;
  }

  private async applyVersionUpdates(
    conflicts: VersionConflict[],
    projectPath: string,
    dryRun: boolean = false
  ): Promise<number> {
    let updated = 0;

    for (const conflict of conflicts) {
      if (conflict.resolution === 'update') {
        try {
          const filePath = path.join(projectPath, conflict.file);
          let content = await fs.readFile(filePath, 'utf-8');

          // Replace version references
          content = content.replace(
            new RegExp(conflict.current.replace(/\./g, '\\.'), 'g'),
            conflict.target
          );

          if (!dryRun) {
            await fs.writeFile(filePath, content);
            logger.debug(`Updated ${conflict.file}: ${conflict.current} → ${conflict.target}`);
          }

          updated++;
        } catch (error) {
          logger.warn(`Failed to update ${conflict.file}: ${error}`);
        }
      }
    }

    return updated;
  }

  async validateSync(projectPath: string): Promise<{ valid: boolean; issues: string[] }> {
    const manifest = await VERSION_MANIFEST.loadManifest();
    const files = await this.scanProjectFiles(projectPath);
    const conflicts = await this.analyzeVersionReferences(files, manifest, projectPath);

    return {
      valid: conflicts.length === 0,
      issues: conflicts.map(c => `${c.file}: ${c.current} should be ${c.target}`)
    };
  }

  async createVersionReport(projectPath: string): Promise<any> {
    const manifest = await VERSION_MANIFEST.loadManifest();
    const files = await this.scanProjectFiles(projectPath);
    const conflicts = await this.analyzeVersionReferences(files, manifest, projectPath);

    return {
      timestamp: new Date().toISOString(),
      manifest_versions: {
        protocol: manifest.versions.protocol.current,
        governance: manifest.versions.governance.current,
        components: Object.fromEntries(
          Object.entries(manifest.versions.components).map(([k, v]) => [k, (v as any).current])
        )
      },
      project_analysis: {
        files_scanned: files.length,
        conflicts_found: conflicts.length,
        conflicts: conflicts
      },
      compliance: {
        synchronized: conflicts.length === 0,
        score: Math.max(0, 100 - (conflicts.length * 10))
      }
    };
  }

  async forceSync(projectPath: string): Promise<SyncResult> {
    return this.sync(projectPath, { force: true });
  }

  async previewSync(projectPath: string): Promise<SyncResult> {
    return this.sync(projectPath, { dryRun: true });
  }

  // ISynchronizer interface implementation
  preview(projectPath: string, options: any = {}): Promise<SyncResult> {
    return this.previewSync(projectPath);
  }

  getName(): string {
    return 'default-synchronizer';
  }

  getVersion(): string {
    return '1.0.0';
  }
}
