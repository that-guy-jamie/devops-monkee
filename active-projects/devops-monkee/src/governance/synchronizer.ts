import * as fs from 'fs-extra';
import * as path from 'path';
import * as glob from 'glob';
import { VERSION_MANIFEST } from '../utils/version-manifest';
import { logger } from '../utils/logger';
import { SyncResult, VersionConflict } from '../index';
import { ISynchronizer } from '../interfaces/tool-interfaces';
import { validatePath } from '../utils/path-validator';
import { sanitizeLog } from '../utils/log-sanitizer';
import { secureExec } from '../utils/secure-exec';

export class Synchronizer implements ISynchronizer {
  async sync(projectPath: string, options: any = {}): Promise<SyncResult> {
    const progress = logger.startProgress('Version synchronization');

    try {
      // Validate project path
      const validatedPath = validatePath(projectPath);
      
      progress.update('Checking repository status');
      const repoStatus = await this.checkRepositoryStatus(validatedPath);
      
      if (repoStatus.hasRemoteUpdates && !options.ignoreRemote) {
        logger.info(`Remote updates available: ${repoStatus.remoteBranch} is ${repoStatus.commitsBehind} commits behind`);
        if (!options.autoPull) {
          logger.warn('Use --auto-pull to automatically sync remote updates');
        }
      }

      progress.update('Loading version manifest');
      const manifest = await VERSION_MANIFEST.loadManifest();

      progress.update('Scanning project files');
      const projectFiles = await this.scanProjectFiles(validatedPath);

      progress.update('Analyzing version references');
      const conflicts = await this.analyzeVersionReferences(projectFiles, manifest, validatedPath);

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
      updated = await this.applyVersionUpdates(conflicts, validatedPath, options.dryRun);

      progress.complete(`synchronized ${updated} files`);
      return {
        updated,
        skipped: projectFiles.length - updated,
        conflicts: []
      };
    } catch (error) {
      const safeError = sanitizeLog(error instanceof Error ? error.message : 'Unknown error');
      progress.fail(safeError);
      throw error;
    }
  }

  /**
   * Check git repository for remote updates
   */
  private async checkRepositoryStatus(projectPath: string): Promise<{
    hasRemoteUpdates: boolean;
    remoteBranch: string;
    commitsBehind: number;
    commitsAhead: number;
  }> {
    try {
      // Verify this is a git repository
      const gitRoot = await secureExec('git', ['rev-parse', '--show-toplevel'], { cwd: projectPath });
      if (!gitRoot.success || !gitRoot.stdout) {
        return { hasRemoteUpdates: false, remoteBranch: '', commitsBehind: 0, commitsAhead: 0 };
      }

      // Fetch remote updates (read-only operation)
      await secureExec('git', ['fetch', '--dry-run'], { cwd: projectPath });

      // Get current branch
      const branchResult = await secureExec('git', ['rev-parse', '--abbrev-ref', 'HEAD'], { cwd: projectPath });
      const currentBranch = branchResult.stdout?.trim() || 'main';

      // Check if branch has upstream
      const upstreamResult = await secureExec('git', ['rev-parse', '--abbrev-ref', '--symbolic-full-name', '@{u}'], { cwd: projectPath });
      if (!upstreamResult.success) {
        return { hasRemoteUpdates: false, remoteBranch: currentBranch, commitsBehind: 0, commitsAhead: 0 };
      }

      const remoteBranch = upstreamResult.stdout?.trim() || currentBranch;

      // Compare local vs remote
      const compareResult = await secureExec('git', ['rev-list', '--left-right', '--count', `${currentBranch}...${remoteBranch}`], { cwd: projectPath });
      
      if (compareResult.success && compareResult.stdout) {
        const [ahead, behind] = compareResult.stdout.trim().split('\t').map(Number);
        return {
          hasRemoteUpdates: behind > 0,
          remoteBranch,
          commitsBehind: behind || 0,
          commitsAhead: ahead || 0
        };
      }

      return { hasRemoteUpdates: false, remoteBranch, commitsBehind: 0, commitsAhead: 0 };
    } catch (error) {
      // If git operations fail, continue without repository checking
      logger.debug(`Repository check failed: ${sanitizeLog(error instanceof Error ? error.message : 'Unknown error')}`);
      return { hasRemoteUpdates: false, remoteBranch: '', commitsBehind: 0, commitsAhead: 0 };
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
        const validatedPath = validatePath(path.join(projectPath, file));
        const content = await fs.readFile(validatedPath, 'utf-8');
        const fileConflicts = await this.checkFileForVersionIssues(content, file, manifest);

        conflicts.push(...fileConflicts);
      } catch (error) {
        logger.debug(`Skipping file ${file}: ${sanitizeLog(error instanceof Error ? error.message : 'Unknown error')}`);
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
          const validatedPath = validatePath(path.join(projectPath, conflict.file));
          let content = await fs.readFile(validatedPath, 'utf-8');

          // Replace version references
          content = content.replace(
            new RegExp(conflict.current.replace(/\./g, '\\.'), 'g'),
            conflict.target
          );

          if (!dryRun) {
            await fs.writeFile(validatedPath, content);
            logger.debug(`Updated ${conflict.file}: ${conflict.current} → ${conflict.target}`);
          }

          updated++;
        } catch (error) {
          logger.warn(`Failed to update ${conflict.file}: ${sanitizeLog(error instanceof Error ? error.message : 'Unknown error')}`);
        }
      }
    }

    return updated;
  }

  async validateSync(projectPath: string): Promise<{ valid: boolean; issues: string[] }> {
    const validatedPath = validatePath(projectPath);
    const manifest = await VERSION_MANIFEST.loadManifest();
    const files = await this.scanProjectFiles(validatedPath);
    const conflicts = await this.analyzeVersionReferences(files, manifest, validatedPath);

    return {
      valid: conflicts.length === 0,
      issues: conflicts.map(c => `${c.file}: ${c.current} should be ${c.target}`)
    };
  }

  async createVersionReport(projectPath: string): Promise<any> {
    const validatedPath = validatePath(projectPath);
    const manifest = await VERSION_MANIFEST.loadManifest();
    const files = await this.scanProjectFiles(validatedPath);
    const conflicts = await this.analyzeVersionReferences(files, manifest, validatedPath);

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

