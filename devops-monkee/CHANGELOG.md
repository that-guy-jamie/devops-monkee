# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2025-11-03

### Added
- **Repository Synchronization**: Synchronizer now detects remote repository updates
  - Checks git remotes for available updates
  - Compares local vs remote branches
  - Reports commits behind/ahead
  - Integration with version synchronization workflow
- **Security Utilities**:
  - Path validation utilities to prevent path traversal attacks
  - Log sanitization to automatically redact sensitive information
  - Secure command execution utilities for git operations
- **SBEP Security Guidelines**: Comprehensive security best practices documentation
- **Security Best Practices**: Integrated into SECURITY.md and CONTRIBUTING.md
- **Tool Building Guidelines**: SBEP constitutional standards for tool building (Part of Constitution v2.2)
- **Tool Management Foundation**: ToolManager class foundation for v1.3.0
- **Tool Sharing Templates**: Examples showing how to share tools across teams
- **API Documentation**: TypeDoc configuration for comprehensive API reference

### Enhanced
- **Synchronizer**: Enhanced with repository status checking and remote update detection
- **CI/CD Pipeline**: Added dependency vulnerability scanning (`npm audit`) before publish
- **File Operations**: All file operations now use validated paths
- **Logging**: Automatic sanitization of sensitive information in logs
- **Input Validation**: Path traversal protection for all file operations

### Security
- Path traversal protection for all file operations
- Safe YAML parsing with schema validation
- Secure command execution utilities
- Dependency audit in release workflow
- Comprehensive security guidelines and best practices

## [1.1.1] - 2025-11-01

### Changed
- Updated package.json with OSS hardening
- Added CI/CD release workflow with npm provenance
- Added community files (CONTRIBUTING.md, SECURITY.md, issue templates)
- Updated contact information and funding configuration

## [1.1.0] - 2025-10-31

Initial public release with core SBEP governance functionality.

