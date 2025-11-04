# SBEP Repository Strategy: Internal vs External

## Overview

SBEP recommends a **dual-repository strategy** for organizations using the protocol:

- **Public Repository (e.g., GitHub)**: Open-source tools, public documentation, community-facing content
- **Private Repository (e.g., GitLab)**: Detailed project information, proprietary data, internal collaboration

## Recommended Setup

### Public Repository (External)
**Purpose**: Share open-source tools and public-facing documentation

**What Goes Here**:
- Open-source SBEP tools (like `devops-monkee`)
- Public documentation and guides
- Community-facing README files
- Public API documentation
- Open examples and templates

**Example**: 
- `github.com/your-org/devops-monkee` - The public tool repository

### Private Repository (Internal)
**Purpose**: Store detailed project information and internal collaboration

**What Goes Here**:
- Detailed project documentation
- Proprietary client information
- Internal workflows and processes
- Private configuration files
- Team collaboration notes
- SBEP compliance reports and audits
- Project-specific mandates and indexes

**Example**:
- `gitlab.com/your-org/sbep-protocol` - The private protocol repository

## Implementation Guide

### For New SBEP Users

1. **Create Public Repository** (if sharing tools)
   ```bash
   # Create a new GitHub repository for your public tool
   git init
   git remote add origin https://github.com/your-org/your-tool.git
   ```

2. **Create Private Repository** (for internal use)
   ```bash
   # Create a private GitLab/GitHub repository for detailed project info
   git init
   git remote add origin https://gitlab.com/your-org/sbep-protocol.git
   ```

3. **Configure Dual Remotes** (if working with both)
   ```bash
   # In your local repository
   git remote add github https://github.com/your-org/your-tool.git
   git remote add gitlab https://gitlab.com/your-org/sbep-protocol.git
   
   # Push public content to GitHub
   git push github main
   
   # Push internal content to GitLab
   git push gitlab main
   ```

### Workflow Pattern

```
┌─────────────────────────────────────────┐
│  Local Development                      │
│  (Complete project structure)           │
└─────────────┬───────────────────────────┘
              │
              ├──────────────────┬─────────────────┐
              │                  │                 │
              ▼                  ▼                 ▼
    ┌─────────────────┐ ┌──────────────┐ ┌──────────────┐
    │ Public GitHub    │ │Private GitLab │ │ Local Files  │
    │ (Open Source)    │ │(Internal)     │ │ (Working)     │
    │                  │ │               │ │               │
    │ - Tool code      │ │ - Detailed    │ │ - All files   │
    │ - Public docs    │ │   docs        │ │ - Private     │
    │ - README          │ │ - Client data │ │   configs     │
    │ - Examples       │ │ - Workflows   │ │ - Development │
    └─────────────────┘ └───────────────┘ └──────────────┘
```

## Is This Baked Into SBEP?

**No, this is a recommended pattern, not a requirement.**

SBEP itself doesn't mandate a specific repository structure. However, this dual-repository approach offers several benefits:

### Advantages

1. **Security**: Keeps proprietary information private
2. **Collaboration**: Enables team-specific internal workflows
3. **Public Sharing**: Allows open-source tools to be shared with the community
4. **Flexibility**: Teams can adapt to their specific needs
5. **Compliance**: Easier to maintain security and compliance boundaries

### Alternative Approaches

- **Single Public Repository**: If all your work is open-source
- **Single Private Repository**: If you're not sharing tools publicly
- **Monorepo Structure**: If you prefer everything in one place with strict access controls
- **Multiple Repositories**: Split by project, team, or other organizational needs

## Best Practices

### 1. Clear Separation of Concerns

- **Public**: Only include what you're comfortable sharing with the world
- **Private**: Include everything needed for internal team collaboration

### 2. .gitignore Strategy

Use `.gitignore` to prevent accidental exposure:

```gitignore
# In public repository
.env*
secrets/
*.key
proprietary-data/
client-configs/
internal-workflows/
```

### 3. Documentation Standards

- **Public docs**: Focus on usage, installation, examples
- **Private docs**: Include detailed architecture, internal processes, proprietary information

### 4. Regular Audits

Periodically review what's in your public repository to ensure:
- No proprietary data leaked
- No credentials or secrets
- Appropriate level of detail for public consumption

## For DevOps Monkee Users

When using `devops-monkee` to validate SBEP compliance:

1. **Public Repository**: Run `dopm abide` on your public repos to ensure compliance with SBEP standards
2. **Private Repository**: Can also run validation, but results stay internal
3. **Cross-Repository**: Maintain SBEP indexes in both repos as needed

## Example: Organization Setup

A typical setup demonstrates this pattern:

- **Public**: `github.com/that-guy-jamie/devops-monkee`
  - Open-source tool
  - Public documentation
  - Community examples

- **Private**: `gitlab.com/your-org/sbep-protocol`
  - Detailed project documentation
  - Internal workflows
  - Proprietary client information
  - Team collaboration

## Conclusion

The dual-repository strategy is a **recommended pattern** that provides flexibility, security, and collaboration benefits. It's not required by SBEP, but it's a proven approach for organizations balancing open-source contribution with internal project management.

Choose the repository structure that best fits your organization's needs, security requirements, and collaboration style.

