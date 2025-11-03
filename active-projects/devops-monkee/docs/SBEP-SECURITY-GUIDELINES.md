# SBEP Security Guidelines

Security best practices for SBEP-compliant projects. These guidelines ensure secure development, deployment, and maintenance of AI agent projects.

## Secret Management

### Never Commit Secrets
- **Never** commit secrets to version control, even in private repositories
- Private repositories can become public, be cloned, or shared
- Use environment variables exclusively for sensitive data
- Use secret management services for production (AWS Secrets Manager, HashiCorp Vault, etc.)

### Default Values Must Be Placeholders
- Configuration defaults should use placeholders: `None`, `"CHANGE_ME"`, `""`, or `undefined`
- **Never** use real production credentials as defaults
- Document that environment variables are required for production
- Example:
  ```typescript
  // ✅ Good
  DATABASE_URL: string = process.env.DATABASE_URL || "CHANGE_ME";
  
  // ❌ Bad
  DATABASE_URL: string = process.env.DATABASE_URL || "postgresql://user:password@host/db";
  ```

### Environment Variables
- All secrets must be provided via environment variables
- Use `.env` files for local development (add to `.gitignore`)
- Never commit `.env` files or any files containing secrets
- Document required environment variables in README

## Pre-Release Security Checklist

Before making any repository public or releasing code:

- [ ] Scan git history for secrets using `gitleaks` or `git-secrets`
- [ ] Review all configuration files for hardcoded credentials
- [ ] Verify no `.env` files are tracked
- [ ] Check for secrets in default values
- [ ] Audit environment variable usage
- [ ] Clean git history if secrets found (use BFG Repo-Cleaner or `git filter-repo`)
- [ ] Run dependency vulnerability scan (`npm audit`)
- [ ] Review all files that will be published

### Tools for Secret Scanning
- **gitleaks**: `gitleaks detect --source . --verbose`
- **git-secrets**: Pre-commit hook for secret detection
- **GitGuardian**: Automated monitoring for repositories
- **truffleHog**: Scans git history for secrets

### Git History Management
- **Important**: Deleting files does not remove them from git history
- If secrets were committed, they remain in history until cleaned
- Use history rewriting tools BEFORE making repository public:
  - `git filter-repo` (recommended)
  - BFG Repo-Cleaner
  - `git filter-branch` (deprecated, but works)

## Automated Detection

### Pre-Commit Hooks
Install secret scanning tools to prevent secrets from entering history:

```bash
# Install gitleaks
brew install gitleaks  # macOS
# or download from https://github.com/gitleaks/gitleaks

# Add to .git/hooks/pre-commit
#!/bin/sh
gitleaks protect --staged --verbose
```

### CI/CD Pipeline
- Add secret scanning to CI/CD pipeline
- Block merges/releases if secrets detected
- Run `npm audit` before publishing
- Scan dependencies for vulnerabilities

## Dependency Security

### Vulnerability Scanning
- Run `npm audit` regularly (automated in CI/CD)
- Address moderate+ severity vulnerabilities before release
- Use `npm audit fix` for automatic fixes when safe
- Document dependency update policy

### Supply Chain Security
- Consider generating SBOM (Software Bill of Materials)
- Use `npm ci` instead of `npm install` in CI/CD
- Pin critical dependencies to specific versions when needed
- Review dependency updates before merging

## Input Validation

### Path Traversal Protection
- Validate all file paths before file operations
- Use `path.resolve()` and verify paths stay within project directory
- Reject paths with `..` or absolute paths outside project
- Use path validation utilities for all file operations

### Command Injection Prevention
- Use `child_process.spawn()` with explicit arguments (not shell)
- Never use `exec()` or shell commands with user input
- Validate all inputs before passing to system commands
- Use secure execution utilities for command execution

## Secure Parsing

### YAML/JSON Parsing
- Use safe parsing methods:
  - `js-yaml.safeLoad()` or `js-yaml.load()` with `schema: 'safe'`
  - Never use `load()` with unsafe schemas
- Validate parsed content structure
- Never parse untrusted YAML from external sources

### File Operations
- Validate file paths before reading/writing
- Use secure file permissions (600 for secrets, 644 for configs)
- Never read files outside project directory
- Sanitize file content before processing

## Logging Security

### Secret Redaction
- Never log environment variables
- Redact secrets from log messages automatically
- Sanitize error messages before logging
- Use structured logging with field filtering

### Error Handling
- Never include sensitive data in error messages
- Sanitize stack traces that might contain secrets
- Use generic error messages for production
- Log detailed errors only in development mode

## Code Review Standards

### Security Checklist
- Never approve commits with secrets
- Reject real credentials in defaults
- Require placeholders only
- Verify environment variable usage
- Check for path traversal vulnerabilities
- Validate input sanitization

## Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [npm Security Best Practices](https://docs.npmjs.com/security-best-practices)
- [GitHub Security](https://docs.github.com/en/code-security)
- [Node.js Security Checklist](https://nodejs.org/en/docs/guides/security/)

---

**Remember**: Security is a continuous process, not a one-time task. Regular audits and updates are essential.

