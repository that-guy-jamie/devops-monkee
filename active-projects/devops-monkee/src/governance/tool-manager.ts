/**
 * Tool Manager - For v1.3.0
 * 
 * Manages shared tools across projects and teams
 * Provides discovery, validation, and registration of tools
 */

import * as fs from 'fs-extra';
import * as path from 'path';
import { logger } from '../utils/logger';
import { validatePath } from '../utils/path-validator';

export interface ToolMetadata {
  name: string;
  version: string;
  description: string;
  author: string;
  category: string;
  entryPoint: string;
  dependencies?: string[];
  tags?: string[];
}

export interface ToolRegistry {
  tools: ToolMetadata[];
  lastUpdated: string;
  version: string;
}

/**
 * Tool Manager - Manages shared tools
 */
export class ToolManager {
  private registryPath: string;
  
  constructor(projectPath: string = process.cwd()) {
    this.registryPath = path.join(projectPath, '.sbep', 'tools-registry.json');
  }

  /**
   * Register a new tool
   */
  async registerTool(tool: ToolMetadata): Promise<void> {
    const registry = await this.loadRegistry();
    
    // Check if tool already exists
    const existing = registry.tools.find(t => t.name === tool.name);
    if (existing) {
      throw new Error(`Tool ${tool.name} already registered`);
    }
    
    // Validate tool entry point exists
    const entryPath = validatePath(tool.entryPoint, process.cwd());
    if (!await fs.pathExists(entryPath)) {
      throw new Error(`Tool entry point not found: ${tool.entryPoint}`);
    }
    
    registry.tools.push(tool);
    registry.lastUpdated = new Date().toISOString();
    
    await this.saveRegistry(registry);
    logger.info(`Tool ${tool.name} registered successfully`);
  }

  /**
   * List all registered tools
   */
  async listTools(category?: string): Promise<ToolMetadata[]> {
    const registry = await this.loadRegistry();
    
    if (category) {
      return registry.tools.filter(t => t.category === category);
    }
    
    return registry.tools;
  }

  /**
   * Find a tool by name
   */
  async findTool(name: string): Promise<ToolMetadata | null> {
    const registry = await this.loadRegistry();
    return registry.tools.find(t => t.name === name) || null;
  }

  /**
   * Validate tool structure
   */
  async validateTool(toolPath: string): Promise<{ valid: boolean; issues: string[] }> {
    const issues: string[] = [];
    
    try {
      const validatedPath = validatePath(toolPath, process.cwd());
      
      // Check if tool file exists
      if (!await fs.pathExists(validatedPath)) {
        issues.push(`Tool file not found: ${validatedPath}`);
      }
      
      // Check if it exports something
      const content = await fs.readFile(validatedPath, 'utf-8');
      if (!content.includes('export')) {
        issues.push('Tool file must export at least one function or class');
      }
      
      // Check for documentation
      if (!content.includes('/**') && !content.includes('*')) {
        issues.push('Tool should include JSDoc documentation');
      }
      
      return {
        valid: issues.length === 0,
        issues
      };
    } catch (error) {
      issues.push(`Validation error: ${error instanceof Error ? error.message : 'Unknown error'}`);
      return { valid: false, issues };
    }
  }

  /**
   * Load tool registry
   */
  private async loadRegistry(): Promise<ToolRegistry> {
    try {
      if (await fs.pathExists(this.registryPath)) {
        const content = await fs.readFile(this.registryPath, 'utf-8');
        return JSON.parse(content);
      }
    } catch (error) {
      logger.warn(`Failed to load registry: ${error}`);
    }
    
    // Return empty registry
    return {
      tools: [],
      lastUpdated: new Date().toISOString(),
      version: '1.0.0'
    };
  }

  /**
   * Save tool registry
   */
  private async saveRegistry(registry: ToolRegistry): Promise<void> {
    const dir = path.dirname(this.registryPath);
    await fs.ensureDir(dir);
    await fs.writeFile(this.registryPath, JSON.stringify(registry, null, 2));
  }

  /**
   * Remove a tool from registry
   */
  async unregisterTool(name: string): Promise<void> {
    const registry = await this.loadRegistry();
    const index = registry.tools.findIndex(t => t.name === name);
    
    if (index === -1) {
      throw new Error(`Tool ${name} not found in registry`);
    }
    
    registry.tools.splice(index, 1);
    registry.lastUpdated = new Date().toISOString();
    await this.saveRegistry(registry);
    logger.info(`Tool ${name} unregistered`);
  }
}

