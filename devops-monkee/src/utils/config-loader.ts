// Configuration Loader
// Loads project-specific configuration with fallback to defaults

import * as fs from 'fs-extra';
import * as path from 'path';
import { logger } from './logger';

export interface DevOpsMonkeeConfig {
  constitution?: {
    source?: string;
    validateStructure?: boolean;
  };
  validation?: {
    schema?: string;
    validator?: string;
  };
  standards?: {
    documentation?: {
      minQuality?: number;
      requiredSections?: string[];
    };
    safety?: {
      rollbackRequired?: boolean;
      exceptionPolicy?: string;
      weight?: number;
    };
  };
  tools?: {
    validator?: {
      type?: 'default' | 'custom' | 'plugin';
      module?: string;
    };
    synchronizer?: {
      type?: 'default' | 'custom' | 'plugin';
      module?: string;
    };
    auditor?: {
      type?: 'default' | 'custom' | 'plugin';
      module?: string;
    };
    governor?: {
      type?: 'default' | 'custom' | 'plugin';
      module?: string;
    };
  };
  plugins?: string[];
}

const CONFIG_FILE_NAME = '.devops-monkee/config.json';

export class ConfigLoader {
  /**
   * Load configuration from project directory
   * Returns null if no config file exists (use defaults)
   */
  static async loadConfig(projectPath: string): Promise<DevOpsMonkeeConfig | null> {
    const configPath = path.join(projectPath, CONFIG_FILE_NAME);
    
    try {
      if (await fs.pathExists(configPath)) {
        const config = await fs.readJson(configPath);
        logger.debug(`Loaded config from: ${configPath}`);
        return config as DevOpsMonkeeConfig;
      }
    } catch (error) {
      logger.warn(`Failed to load config from ${configPath}:`, error);
    }
    
    return null;
  }

  /**
   * Resolve a file path relative to project directory
   */
  static resolveProjectPath(projectPath: string, filePath: string): string {
    if (path.isAbsolute(filePath)) {
      return filePath;
    }
    return path.join(projectPath, filePath);
  }

  /**
   * Check if a custom file exists in project
   */
  static async hasCustomFile(projectPath: string, filePath: string): Promise<boolean> {
    const fullPath = this.resolveProjectPath(projectPath, filePath);
    return await fs.pathExists(fullPath);
  }

  /**
   * Load custom constitution from project or return null
   */
  static async loadCustomConstitution(projectPath: string): Promise<string | null> {
    const config = await this.loadConfig(projectPath);
    
    if (config?.constitution?.source) {
      const constitutionPath = this.resolveProjectPath(projectPath, config.constitution.source);
      
      if (await fs.pathExists(constitutionPath)) {
        logger.debug(`Loading custom constitution from: ${constitutionPath}`);
        return await fs.readFile(constitutionPath, 'utf-8');
      } else {
        logger.warn(`Custom constitution not found: ${constitutionPath}`);
      }
    }
    
    return null;
  }

  /**
   * Get path to custom validation schema if it exists
   */
  static async getCustomSchemaPath(projectPath: string): Promise<string | null> {
    const config = await this.loadConfig(projectPath);
    
    if (config?.validation?.schema) {
      const schemaPath = this.resolveProjectPath(projectPath, config.validation.schema);
      
      if (await fs.pathExists(schemaPath)) {
        logger.debug(`Custom validation schema found: ${schemaPath}`);
        return schemaPath;
      } else {
        logger.warn(`Custom validation schema not found: ${schemaPath}`);
      }
    }
    
    return null;
  }

  /**
   * Get custom validator module path if specified
   */
  static async getCustomValidatorPath(projectPath: string): Promise<string | null> {
    const config = await this.loadConfig(projectPath);
    
    if (config?.validation?.validator) {
      const validatorPath = this.resolveProjectPath(projectPath, config.validation.validator);
      
      if (await fs.pathExists(validatorPath)) {
        logger.debug(`Custom validator found: ${validatorPath}`);
        return validatorPath;
      } else {
        logger.warn(`Custom validator not found: ${validatorPath}`);
      }
    }
    
    return null;
  }

  /**
   * Get plugin paths from config
   */
  static async getPluginPaths(projectPath: string): Promise<string[]> {
    const config = await this.loadConfig(projectPath);
    const plugins: string[] = [];
    
    if (config?.plugins) {
      for (const pluginPath of config.plugins) {
        const resolvedPath = this.resolveProjectPath(projectPath, pluginPath);
        if (await fs.pathExists(resolvedPath)) {
          plugins.push(resolvedPath);
        } else {
          logger.warn(`Plugin not found: ${resolvedPath}`);
        }
      }
    }
    
    return plugins;
  }
}

