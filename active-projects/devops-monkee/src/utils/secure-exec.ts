/**
 * Secure command execution utilities to prevent command injection
 */

import { spawn } from 'child_process';
import { promisify } from 'util';

export interface ExecResult {
  success: boolean;
  stdout?: string;
  stderr?: string;
  code?: number;
}

/**
 * Safely executes a command using spawn (no shell interpretation)
 * @param command - Command to execute (e.g., 'git')
 * @param args - Array of arguments (never user-controlled strings)
 * @param options - Execution options
 * @returns Promise with execution result
 */
export async function secureExec(
  command: string,
  args: string[] = [],
  options: { cwd?: string; env?: NodeJS.ProcessEnv; timeout?: number } = {}
): Promise<ExecResult> {
  return new Promise((resolve) => {
    // Validate command is not a shell command
    if (command.includes(';') || command.includes('|') || command.includes('&') || command.includes('$')) {
      resolve({
        success: false,
        stderr: 'Invalid command: shell metacharacters not allowed',
        code: 1
      });
      return;
    }

    // Validate arguments don't contain shell metacharacters
    for (const arg of args) {
      if (typeof arg !== 'string' || arg.includes(';') || arg.includes('|') || arg.includes('&')) {
        resolve({
          success: false,
          stderr: 'Invalid argument: shell metacharacters not allowed',
          code: 1
        });
        return;
      }
    }

    const child = spawn(command, args, {
      cwd: options.cwd || process.cwd(),
      env: options.env || process.env,
      shell: false, // Explicitly disable shell
      stdio: ['ignore', 'pipe', 'pipe']
    });

    let stdout = '';
    let stderr = '';

    child.stdout?.on('data', (data) => {
      stdout += data.toString();
    });

    child.stderr?.on('data', (data) => {
      stderr += data.toString();
    });

    const timeout = options.timeout || 30000; // 30 second default
    const timeoutId = setTimeout(() => {
      child.kill();
      resolve({
        success: false,
        stderr: 'Command execution timeout',
        code: 124
      });
    }, timeout);

    child.on('close', (code) => {
      clearTimeout(timeoutId);
      resolve({
        success: code === 0,
        stdout: stdout.trim(),
        stderr: stderr.trim(),
        code: code || undefined
      });
    });

    child.on('error', (error) => {
      clearTimeout(timeoutId);
      resolve({
        success: false,
        stderr: error.message,
        code: 1
      });
    });
  });
}

/**
 * Validates that a command is in the allowed list
 * @param command - Command to validate
 * @param allowedCommands - List of allowed commands
 * @returns true if command is allowed
 */
export function isCommandAllowed(command: string, allowedCommands: string[]): boolean {
  return allowedCommands.includes(command);
}

/**
 * Default allowed commands for Synchronizer
 */
export const ALLOWED_GIT_COMMANDS = [
  'git'
];

