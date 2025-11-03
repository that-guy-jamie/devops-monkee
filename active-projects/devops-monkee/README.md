# DevOps Monkee 🐒 — SBEP governance layer for AI agents

[![npm version](https://img.shields.io/npm/v/devops-monkee.svg)](https://www.npmjs.com/package/devops-monkee) [![npm downloads](https://img.shields.io/npm/dm/devops-monkee.svg)](https://www.npmjs.com/package/devops-monkee)

[![CI](https://github.com/that-guy-jamie/devops-monkee/actions/workflows/release.yml/badge.svg)](../../actions)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Opinionated CLI + API implementing the **SBEP** protocol (Source-Bound Execution Protocol) for governance, audits, and version sync across AI-agent projects.

- **CLI aliases:** `devops-monkee`, `sbep`, `dopm`

- **Node:** 18+ · **License:** MIT · **Docs:** see below

## Install

```bash
# project local (recommended)
npm i -D devops-monkee

# or global CLI
npm i -g devops-monkee
```

## Quick Start (CLI)

```bash
# one-shot compliance pass
dopm abide .

# focused checks
dopm abide . -validate   # SBEP compliance
dopm abide . -audit      # Quality audit
dopm abide . -docs       # Documentation check
dopm abide . -test       # Testing verification
dopm abide . -sync       # Version sync + repository status
```

## Programmatic API (ESM)

```ts
import { Validator, Synchronizer, Auditor, Governor } from "devops-monkee";

const validator = new Validator();
const results = await validator.validate(process.cwd());

const sync = new Synchronizer();
await sync.sync(process.cwd());
```

## Shared Utility Tools

Import security and utility tools for use across your projects:

```ts
import { 
  validatePath, 
  sanitizeLog, 
  secureExec 
} from "devops-monkee";

// Path validation (prevents path traversal)
const safePath = validatePath(userInput, baseDirectory);

// Log sanitization (redacts secrets)
const safeLog = sanitizeLog(errorMessage);

// Secure command execution (prevents injection)
const result = await secureExec('git', ['status'], { cwd: projectPath });
```

**Available Tools:**
- **Path Validation**: `validatePath`, `validateAndCheckPath`, `sanitizeFilename`
- **Log Sanitization**: `sanitizeLog`, `sanitizeError`, `mightContainSecrets`
- **Secure Execution**: `secureExec`, `isCommandAllowed`

## Documentation

- [What is SBEP?](./docs/WHAT-IS-SBEP.md) - Understanding the Source-Bound Execution Protocol
- [Usage Examples](./docs/USAGE-EXAMPLES.md) - Practical examples and use cases
- [SBEP Security Guidelines](./docs/SBEP-SECURITY-GUIDELINES.md) - Security best practices
- [Installation Troubleshooting](./NPX-DOPM-INSTALLATION-TROUBLESHOOTING.md)
- [SBEP Test Implementation Guide](./DEVOPS-MONKEE-TEST-IMPLEMENTATION-PROMPT.md)

## Resources

- **npm Package**: https://www.npmjs.com/package/devops-monkee
- **GitHub Repository**: https://github.com/that-guy-jamie/devops-monkee
- **Issues**: https://github.com/that-guy-jamie/devops-monkee/issues

## Requirements

- Node.js >= 18.0.0

## Sponsor & Support

**Let OneClickSEO help you thrive in the post-modern technology era.**

Move beyond traditional development constraints with tools designed for today's AI-driven workflows. If DevOps Monkee helps your team, consider supporting its development.

- **Sponsorship inquiries:** jamie@oneclick.agency
- **GitHub Sponsors:** [coming soon](https://github.com/sponsors/that-guy-jamie)

## Contact

Questions, ideas, or feedback? Email **jamie@oneclick.agency**.

- Bug reports: open a GitHub issue → https://github.com/that-guy-jamie/devops-monkee/issues  
- Security issues: see [SECURITY.md](SECURITY.md) or email **jamie@oneclick.agency**.

## License

MIT
