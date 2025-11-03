/**
 * Log sanitization utilities to prevent sensitive information leakage
 */

/**
 * Patterns that indicate sensitive information
 */
const SENSITIVE_PATTERNS = [
  /(?:password|passwd|pwd)\s*[:=]\s*["']?([^"'\s]+)/gi,
  /(?:secret|api[_-]?key|token|auth)\s*[:=]\s*["']?([^"'\s]+)/gi,
  /(?:bearer|authorization)\s+([^\s]+)/gi,
  /(?:connection|conn)[_-]?string\s*[:=]\s*["']?([^"']+)/gi,
  /postgresql?:\/\/[^:]+:([^@]+)@/gi,
  /mongodb:\/\/[^:]+:([^@]+)@/gi,
  /redis:\/\/[^:]+:([^@]+)@/gi,
  /(?:refresh[_-]?token|access[_-]?token)\s*[:=]\s*["']?([^"'\s]+)/gi,
  /(?:client[_-]?secret|secret[_-]?key)\s*[:=]\s*["']?([^"'\s]+)/gi,
];

/**
 * Redacts sensitive information from log messages
 * @param message - Log message to sanitize
 * @returns Sanitized message with secrets redacted
 */
export function sanitizeLog(message: string): string {
  if (!message || typeof message !== 'string') {
    return message;
  }

  let sanitized = message;

  // Replace sensitive patterns with redaction marker
  for (const pattern of SENSITIVE_PATTERNS) {
    sanitized = sanitized.replace(pattern, (match, secret) => {
      if (secret && secret.length > 4) {
        return match.replace(secret, '***REDACTED***');
      }
      return match;
    });
  }

  // Check for long strings that might be secrets (32+ chars, alphanumeric)
  const longSecretPattern = /\b([A-Za-z0-9]{32,})\b/g;
  sanitized = sanitized.replace(longSecretPattern, (match) => {
    // Skip if it's a URL or already contains special chars
    if (match.includes('://') || match.includes('/') || match.includes('@')) {
      return match;
    }
    // Redact potential secrets
    return '***REDACTED***';
  });

  return sanitized;
}

/**
 * Sanitizes an error object, removing sensitive information from message and stack
 * @param error - Error object to sanitize
 * @returns Sanitized error message
 */
export function sanitizeError(error: unknown): string {
  if (error instanceof Error) {
    const sanitizedMessage = sanitizeLog(error.message);
    const sanitizedStack = error.stack ? sanitizeLog(error.stack) : undefined;
    
    return sanitizedStack || sanitizedMessage;
  }
  
  return sanitizeLog(String(error));
}

/**
 * Checks if a string might contain sensitive information
 * @param text - Text to check
 * @returns true if text might contain secrets
 */
export function mightContainSecrets(text: string): boolean {
  const lowerText = text.toLowerCase();
  const secretIndicators = [
    'password',
    'secret',
    'token',
    'api_key',
    'api-key',
    'auth',
    'credential',
    'private_key',
    'private-key'
  ];

  return secretIndicators.some(indicator => lowerText.includes(indicator));
}

