/**
 * Path validation utilities to prevent path traversal attacks
 */

import * as path from 'path';
import * as fs from 'fs-extra';

/**
 * Validates and sanitizes file paths to prevent path traversal attacks
 * @param filePath - The path to validate
 * @param basePath - The base directory that paths must stay within
 * @returns Validated absolute path
 * @throws Error if path is invalid or outside base directory
 */
export function validatePath(filePath: string, basePath?: string): string {
  // Resolve to absolute path
  const absolutePath = path.resolve(filePath);
  
  // If basePath is provided, ensure path is within it
  if (basePath) {
    const absoluteBase = path.resolve(basePath);
    const relative = path.relative(absoluteBase, absolutePath);
    
    // Check for path traversal attempts
    if (relative.startsWith('..') || path.isAbsolute(relative)) {
      throw new Error(`Path traversal detected: ${filePath} is outside base directory ${basePath}`);
    }
  }

  // Reject paths with suspicious patterns
  if (filePath.includes('..') && !basePath) {
    throw new Error(`Relative path traversal detected: ${filePath}`);
  }

  return absolutePath;
}

/**
 * Validates that a path exists and is within the allowed directory
 * @param filePath - Path to validate
 * @param basePath - Base directory
 * @returns Validated path if safe
 */
export async function validateAndCheckPath(filePath: string, basePath: string): Promise<string> {
  const validatedPath = validatePath(filePath, basePath);
  
  // Verify path exists
  const exists = await fs.pathExists(validatedPath);
  if (!exists) {
    throw new Error(`Path does not exist: ${validatedPath}`);
  }

  return validatedPath;
}

/**
 * Sanitizes a filename to prevent directory traversal
 * @param filename - Filename to sanitize
 * @returns Sanitized filename
 */
export function sanitizeFilename(filename: string): string {
  // Remove path separators and parent directory references
  const sanitized = filename
    .replace(/[\/\\]/g, '')
    .replace(/\.\./g, '')
    .replace(/^\./, '');
  
  if (sanitized !== filename) {
    throw new Error(`Invalid filename: ${filename}`);
  }
  
  return sanitized;
}

