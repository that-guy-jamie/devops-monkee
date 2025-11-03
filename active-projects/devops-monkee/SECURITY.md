# Security Policy

We take the security of DevOps Monkee seriously. If you believe you've found a vulnerability, please follow the steps below.

## Supported Versions

We support the latest minor within the current major (e.g., `1.x`). Security fixes will be released as patch versions.

## Reporting a Vulnerability

- **Do not** open a public issue.
- Email: **jamie@oneclick.agency**
- Include: affected version(s), OS, reproduction steps, impact, and any PoC you can share safely.

We aim to acknowledge within **72 hours** and provide a remediation plan or status update within **7 days**.

## Coordinated Disclosure

We follow coordinated disclosure. Once a fix is available on npm, we'll publish release notes crediting reporters (opt-in) and describing the impact and mitigation.

## Safe Harbor

Good-faith security research that follows this policy won't be considered a violation. Please avoid accessing data that isn't yours, and limit testing to your own environments.

## Security Best Practices

For comprehensive security guidelines, see [SBEP Security Guidelines](./docs/SBEP-SECURITY-GUIDELINES.md).

### Key Principles

1. **Never commit secrets** - Use environment variables exclusively
2. **Default values are placeholders** - Never use real credentials as defaults
3. **Always audit before release** - Scan for secrets, run dependency audits
4. **Validate all inputs** - Prevent path traversal and command injection
5. **Sanitize logs** - Never log sensitive information

### Pre-Release Checklist

Before publishing code or making repositories public:

- [ ] Scan git history for secrets
- [ ] Review configuration files
- [ ] Verify no `.env` files tracked
- [ ] Run dependency vulnerability scan
- [ ] Clean git history if secrets found

See [SBEP Security Guidelines](./docs/SBEP-SECURITY-GUIDELINES.md) for detailed practices and tools.
