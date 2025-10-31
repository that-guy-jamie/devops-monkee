# Contributing to DevOps Monkee

Thank you for your interest in contributing to DevOps Monkee! We welcome contributions from the community and are grateful for your help in making this project better.

## 🤝 Code of Conduct

This project follows our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you agree to uphold this code.

## 🚀 Quick Start

### Development Setup

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/your-username/devops-monkee.git
   cd devops-monkee
   ```

3. **Install dependencies**:
   ```bash
   npm install
   ```

4. **Set up development environment**:
   ```bash
   npm run build
   npm test
   ```

5. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

### Development Workflow

1. **Make your changes**
2. **Run tests**: `npm test`
3. **Run linting**: `npm run lint`
4. **Build the project**: `npm run build`
5. **Validate governance**: `npm run validate`
6. **Commit your changes** following conventional commits
7. **Push to your fork**
8. **Create a Pull Request**

## 📝 Development Guidelines

### Code Style

- **TypeScript**: Strict type checking enabled
- **ESLint**: Follow the configured linting rules
- **Prettier**: Code formatting is enforced
- **No Emojis in Code**: Emojis are forbidden in production code (allowed in documentation)

### Commit Messages

We use [Conventional Commits](https://conventionalcommits.org/) format:

```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Test additions/modifications
- `chore`: Maintenance tasks

Examples:
```
feat(governance): add new validation rule for SBEP compliance
fix(cli): resolve issue with sync command on Windows
docs(readme): update installation instructions
```

### Testing

- **Unit Tests**: Required for all new functionality
- **Integration Tests**: For CLI and API functionality
- **Test Coverage**: Aim for 85%+ coverage
- **Test Naming**: `describe('Component')` and `it('should do something')`

### Documentation

- **Code Comments**: Complex logic should be documented
- **README Updates**: Update relevant documentation for user-facing changes
- **API Documentation**: New public APIs must be documented
- **Changelog**: User-facing changes should be documented in CHANGELOG.md

## 🔧 Development Commands

```bash
# Install dependencies
npm install

# Run tests
npm test

# Run tests in watch mode
npm run test:watch

# Run linting
npm run lint

# Format code
npm run format

# Build the project
npm run build

# Validate governance compliance
npm run validate

# Generate documentation
npm run docs

# Run all checks (lint + test + build)
npm run ci
```

## 🏗️ Architecture Guidelines

### Project Structure

```
devops-monkee/
├── src/
│   ├── cli.ts                 # Command-line interface
│   ├── index.ts              # Main exports
│   ├── governance/           # Core governance components
│   │   ├── validator.ts      # Compliance validation
│   │   ├── synchronizer.ts   # Version synchronization
│   │   ├── auditor.ts        # Quality auditing
│   │   └── governor.ts       # Governance oversight
│   └── utils/                # Shared utilities
├── tests/                    # Test files
├── docs/                     # Documentation
├── templates/               # Project templates
└── dist/                    # Built output (generated)
```

### SBEP Protocol Compliance

All contributions must maintain SBEP protocol compliance:

- **Self-Governing**: Code changes should not break governance rules
- **Documentation First**: Changes must be well-documented
- **Safety First**: Include appropriate error handling and validation
- **Quality Standards**: Meet established code quality metrics

### Exception Policies

For edge cases, follow these exception policies:
- **EP-TOOL-001**: Tool failure exceptions
- **EP-VAL-001**: Validation engine exceptions
- **EP-SYNC-001**: Synchronization failures

## 📋 Pull Request Process

### Before Submitting

1. **Self-Review**: Ensure your code follows the guidelines
2. **Test Thoroughly**: All tests pass, new functionality tested
3. **Documentation**: Updated relevant docs
4. **Changelog**: Added entry if user-facing change
5. **Governance**: Passes SBEP validation (`npm run validate`)

### PR Template

Please use the PR template and fill out:
- **Description**: What changes and why
- **Type of Change**: Bug fix, feature, documentation, etc.
- **Testing**: How you tested the changes
- **Breaking Changes**: Any breaking changes?
- **Screenshots**: UI changes (if applicable)

### Review Process

1. **Automated Checks**: CI must pass
2. **Code Review**: At least one maintainer review
3. **Testing**: Reviewer may request additional tests
4. **Approval**: Maintainers approve and merge

## 🎯 Types of Contributions

### Code Contributions
- Bug fixes
- New features
- Performance improvements
- Code refactoring

### Documentation
- README updates
- API documentation
- Tutorials and guides
- Code comments

### Testing
- Unit tests
- Integration tests
- End-to-end tests
- Test framework improvements

### Governance
- SBEP protocol improvements
- Validation rule enhancements
- Exception policy updates
- Quality metric refinements

## 🚨 Issue Reporting

### Bug Reports
- Use the bug report template
- Include steps to reproduce
- Provide environment details
- Attach relevant logs

### Feature Requests
- Use the feature request template
- Describe the problem you're solving
- Explain your proposed solution
- Consider alternative approaches

### Security Issues
- **DO NOT** create public issues for security vulnerabilities
- Email security@devops-monkee.dev instead
- See our [Security Policy](SECURITY.md) for details

## 🌟 Recognition

Contributors are recognized through:
- **GitHub Contributors**: Listed in repository contributors
- **Changelog Credits**: Mentioned in release notes
- **Community Recognition**: Featured in community updates
- **Maintainer Status**: Top contributors may be invited to join the maintainer team

## 📞 Getting Help

- **Discussions**: Use GitHub Discussions for questions
- **Documentation**: Check our comprehensive docs
- **Community**: Join our community chat
- **Support**: Contact support@devops-monkee.dev

## 📝 License

By contributing to DevOps Monkee, you agree that your contributions will be licensed under the same MIT License that covers the project.

---

Thank you for contributing to DevOps Monkee! Your efforts help make AI development more reliable, scalable, and professional. 🚀
