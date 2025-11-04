/**
 * Example Tool Template
 * 
 * This is an example showing HOW to create and share tools across your team.
 * Copy this template and customize for your specific tool needs.
 * 
 * Pattern: Export tools that can be imported and reused across projects
 */

import { validatePath, sanitizeLog } from 'devops-monkee';

/**
 * Example: Custom file processor tool
 * 
 * This demonstrates the pattern for creating shareable tools
 */
export class ExampleFileProcessor {
  /**
   * Process a file safely using shared utilities
   */
  async processFile(filePath: string, baseDir: string): Promise<string> {
    // Use shared path validation utility
    const safePath = validatePath(filePath, baseDir);
    
    // Your custom logic here
    // ...
    
    return safePath;
  }
  
  /**
   * Log safely using shared sanitization
   */
  logSafely(message: string): void {
    // Use shared log sanitization utility
    const safeMessage = sanitizeLog(message);
    console.log(safeMessage);
  }
}

/**
 * Export for use across projects
 * 
 * Team members can import like:
 * import { ExampleFileProcessor } from 'devops-monkee/templates/example-tool';
 */
export default ExampleFileProcessor;

