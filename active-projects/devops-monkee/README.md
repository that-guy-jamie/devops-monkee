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

## Documentation

- [Installation Troubleshooting](./NPX-DOPM-INSTALLATION-TROUBLESHOOTING.md)
- [SBEP Test Implementation Guide](./DEVOPS-MONKEE-TEST-IMPLEMENTATION-PROMPT.md)
- [SBEP Security Guidelines](./docs/SBEP-SECURITY-GUIDELINES.md)

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
