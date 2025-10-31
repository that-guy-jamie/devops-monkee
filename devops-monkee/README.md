# DevOps Monkee - SBEP Governance Layer

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.2-blue.svg)](https://www.typescriptlang.org/)

**A governance framework for AI agent development that ensures quality, safety, and professionalism.**

DevOps Monkee implements the **SBEP (Source-Bound Execution Protocol)** - a framework for governing AI agent behavior and ensuring development quality.

**Developed by the OneClickSEO Team for [OneClickSEO.com](https://oneclickseo.com)**

## 🎯 What is DevOps Monkee?

DevOps Monkee is the governance layer for the **SBEP Protocol** - a comprehensive framework for AI agent operations. It provides:

- **Automated Validation**: Continuous compliance checking against SBEP standards
- **Version Synchronization**: Single source of truth for protocol versions
- **Quality Assurance**: Documentation and code quality metrics
- **Governance Tools**: Change management and exception policy enforcement
- **Developer Experience**: CLI tools for seamless SBEP integration

## 🚀 Key Features

### ✅ Automated Governance
- **Self-Governing Protocol**: SBEP validates and maintains itself
- **Constitutional Framework**: Immutable principles with amendment procedures
- **Quality Metrics**: Objective documentation and code quality standards

### ✅ Enterprise-Ready
- **Version Authority**: Single source of truth for all protocol versions
- **Exception Policies**: Structured handling of edge cases and failures
- **Security Compliance**: Built-in security and data protection checks

### ✅ Developer-Friendly
- **CLI Tools**: Intuitive command-line interface for all operations
- **Auto-Fix**: Automatic remediation of common compliance issues
- **Comprehensive Documentation**: Extensive guides and examples

## 📦 Installation

DevOps Monkee is now live and available on npm!

```bash
# Install globally for CLI usage
npm install -g devops-monkee

# Or install locally in your project
npm install --save-dev devops-monkee
```

**Package Details:**
- **Version**: 1.0.0
- **License**: MIT
- **npm**: https://www.npmjs.com/package/devops-monkee
- **GitHub**: https://github.com/that-guy-jamie/devops-monkee
- **GitLab**: https://gitlab.com/deancaciopp0-group/sbep-protocol

### Requirements
- **Node.js**: >= 18.0.0
- **TypeScript**: >= 5.0.0 (for development)
- **PowerShell**: 5.1+ (for Windows environments)

## 🛠️ Quick Start

### 1. Initialize SBEP Governance

Initialize SBEP governance for a new project:

```bash
# Initialize governance for current project
devops-monkee init .

# Or specify a different path
devops-monkee init /path/to/your/project
```

This creates:
- `sds/` directory with SBEP documentation
- `VERSION-MANIFEST.json` for version tracking
- `.tmp/` and `archive/` directories
- Governance configuration files

### 2. Validate Compliance

Check SBEP compliance for your project:

```bash
# Validate current project
devops-monkee validate .

# Get detailed report
devops-monkee validate . --report validation-report.json

# Attempt auto-fixes
devops-monkee validate . --fix
```

### 3. Synchronize Versions

Ensure all version references are synchronized:

```bash
# Sync versions across all files
devops-monkee sync .

# Preview changes before applying
devops-monkee sync . --dry-run

# Force sync even with conflicts
devops-monkee sync . --force
```

### 4. Audit Quality

Perform comprehensive quality audits:

```bash
# Full quality audit
devops-monkee audit . --type comprehensive

# Security audit only
devops-monkee audit . --type security

# Save results to file
devops-monkee audit . --output audit-results.json
```

### 5. Check Governance Status

Get an overview of governance compliance:

```bash
devops-monkee status .
```

## 📚 SBEP Protocol Overview

### Core Principles

1. **Documentation First**: Documentation is the primary deliverable, not code
2. **Safety First**: All operations include rollback plans and validation
3. **Self-Governance**: The protocol validates and maintains itself
4. **Quality Standards**: Objective metrics for documentation and code quality

### Governance Components

- **Constitution**: Immutable principles governing SBEP evolution
- **Version Manifest**: Single source of truth for protocol versions
- **Validation Schema**: Rules for compliance checking
- **Change Management**: Procedures for protocol updates

### Exception Framework

Structured handling of edge cases:
- **EP-DEP-001**: Manual deployment exceptions
- **EP-TOOL-001**: Tool failure exceptions
- **EP-VAL-001**: Validation engine exceptions
- **EP-SYNC-001**: Synchronization failures

## 🔧 CLI Reference

### Commands

| Command | Description |
|---------|-------------|
| `validate` | Validate SBEP compliance |
| `sync` | Synchronize versions across files |
| `audit` | Perform quality and security audits |
| `govern` | Check governance violations |
| `init` | Initialize SBEP governance |
| `status` | Show governance status |

### Global Options

| Option | Description |
|--------|-------------|
| `-v, --verbose` | Enable verbose output |
| `-h, --help` | Show help information |
| `--version` | Show version number |

## 📖 Documentation

### Getting Started
- [Installation Guide](docs/installation.md)
- [Quick Start Tutorial](docs/quick-start.md)
- [Configuration](docs/configuration.md)

### Governance
- [SBEP Constitution](CONSTITUTION.md)
- [Governance Layer](GOVERNANCE-LAYER.md)
- [Change Management](CHANGE-MANAGEMENT.md)
- [Exception Policies](docs/exception-policies.md)

### API Reference
- [CLI API](docs/cli-api.md)
- [Programmatic API](docs/programmatic-api.md)
- [Validation Schema](VALIDATION-SCHEMA.json)
- [Version Manifest](VERSION-MANIFEST.json)

### Examples
- [Project Templates](templates/)
- [Integration Examples](docs/examples/)
- [Best Practices](docs/best-practices.md)

## 🔌 Programmatic Usage

Use DevOps Monkee programmatically in your applications:

```typescript
import { Validator, Synchronizer, Auditor, Governor } from 'devops-monkee';

// Validate a project
const validator = new Validator();
const results = await validator.validate('/path/to/project');

// Sync versions
const synchronizer = new Synchronizer();
await synchronizer.sync('/path/to/project');

// Run audits
const auditor = new Auditor();
const auditResults = await auditor.audit('/path/to/project', 'comprehensive');

// Check governance
const governor = new Governor();
const violations = await governor.checkCompliance('/path/to/project');
```

## 🤝 Contributing

We welcome contributions! See our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Clone the repository
git clone https://github.com/devops-monkee/devops-monkee.git
cd devops-monkee

# Install dependencies
npm install

# Run tests
npm test

# Build the project
npm run build

# Run linting
npm run lint
```

### Development Commands

```bash
# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Generate documentation
npm run docs

# Format code
npm run format

# Build and release
npm run release
```

## 📋 Requirements & Compatibility

### System Requirements
- **Node.js**: 18.0.0 or higher
- **Operating Systems**: Linux, macOS, Windows
- **Memory**: 256MB minimum, 512MB recommended

### SBEP Protocol Versions
- **Protocol**: 2.2.0
- **Governance**: 1.0.0
- **Validation**: 1.0.0

### Compatible Environments
- **CI/CD**: GitHub Actions, GitLab CI, Jenkins
- **Hosting**: Vercel, Netlify, Render, AWS
- **Containers**: Docker, Kubernetes

## 🐛 Troubleshooting

### Common Issues

**"Command not found"**
```bash
# Install globally
npm install -g devops-monkee

# Or use npx
npx devops-monkee --help
```

**Permission Errors**
```bash
# On Linux/macOS
sudo npm install -g devops-monkee

# On Windows (run as Administrator)
npm install -g devops-monkee
```

**Validation Failures**
```bash
# Run with verbose output
devops-monkee validate . --verbose

# Attempt auto-fixes
devops-monkee validate . --fix

# Check governance status
devops-monkee status .
```

### Getting Help

- 📖 [Documentation](https://docs.devops-monkee.dev)
- 🐛 [Issue Tracker](https://github.com/devops-monkee/devops-monkee/issues)
- 💬 [Discussions](https://github.com/devops-monkee/devops-monkee/discussions)
- 📧 [Email Support](mailto:support@devops-monkee.dev)

## 📈 Roadmap

### Version 1.1.0 (Q1 2026)
- [ ] Enhanced CI/CD integration
- [ ] Additional audit types
- [ ] Improved auto-fix capabilities

### Version 1.2.0 (Q2 2026)
- [ ] Multi-language support
- [ ] Advanced reporting features
- [ ] Plugin architecture

### Version 2.0.0 (Q3 2026)
- [ ] SBEP Protocol 3.0 support
- [ ] Advanced governance features
- [ ] Enterprise compliance tools

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

DevOps Monkee builds upon the SBEP Protocol framework, which was developed to standardize AI agent operations across complex development environments. Special thanks to the SBEP community for their contributions and feedback.

## 📞 Contact

- **Website**: [https://devops-monkee.dev](https://devops-monkee.dev)
- **GitHub**: [https://github.com/devops-monkee/devops-monkee](https://github.com/devops-monkee/devops-monkee)
- **Email**: [hello@devops-monkee.dev](mailto:hello@devops-monkee.dev)
- **Twitter**: [@devopsmonkee](https://twitter.com/devopsmonkee)

---

**Built with ❤️ for the AI agent development community**

*DevOps Monkee - Governing AI agents, one protocol at a time.*
