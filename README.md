# Source-Bound Execution Protocol (SBEP) v2.0

**The Documentation-First AI Agent Operating Standard**

## What is SBEP?

SBEP (Source-Bound Execution Protocol) is a comprehensive operating protocol for AI agents that emphasizes documentation-first approaches, accountability, and autonomous problem-solving. It transforms AI agents from simple assistants into capable, self-directed collaborators who can navigate complex codebases and complete sophisticated tasks independently.

## Core Principles

### 1. Read The F***ing Manual (RTFM)
Before asking for help or claiming inability, agents must:
- Consult project documentation
- Check centralized API docs
- Try multiple approaches
- Provide evidence of attempts

### 2. Autonomy with Accountability
- Agents can make architectural decisions
- All changes must be documented
- Rollback plans required for destructive operations
- Safety-first approach to modifications

### 3. Documentation-Driven Development
- Every project has standardized documentation structure
- Cross-project knowledge sharing is mandatory
- Patterns and solutions are reused across projects

## Quick Start

### For AI Agents
1. Read `SBEP-MANIFEST.md` (the complete protocol)
2. Navigate to your project's `sds/SBEP-MANDATE.md` 
3. Review `sds/SBEP-INDEX.yaml` for documentation inventory
4. Begin task execution following SBEP guidelines

### For Project Setup
1. Copy `SBEP_Core/SBEP-MANDATE-TEMPLATE.md` to `{your-project}/sds/SBEP-MANDATE.md`
2. Copy `SBEP_Core/SBEP-INDEX-TEMPLATE.yaml` to `{your-project}/sds/SBEP-INDEX.yaml`
3. Customize both files for your project
4. Create the standard project structure

## Repository Structure

```
SBEP-Protocol/
├── SBEP-MANIFEST.md          # Core protocol specification
├── SBEP_Core/                # Core documentation and tools
│   ├── SBEP-MANDATE-TEMPLATE.md
│   ├── SBEP-INDEX-TEMPLATE.yaml
│   ├── HOUSEKEEPING-SOP.md
│   └── tools/
├── SBEP_Addenda/             # Additional specifications
└── examples/                 # Implementation examples
```

## Implementation Guide

### Standard Project Structure
Every SBEP-compliant project should have:

```
{project}/
├── sds/                      # Source Documentation Store
│   ├── SBEP-MANDATE.md     # Project-specific agent instructions
│   └── SBEP-INDEX.yaml     # Documentation inventory
├── .tmp/                     # Temporary files
├── README.md                 # Project overview
├── CHANGELOG.md             # Change history
├── docs/                    # Architecture guides
├── ops/                     # Deployment scripts
└── archive/                 # Deprecated files (never delete)
```

### Key Features

**Terminal Command Execution**
- Robust wrapper system for reliable command execution
- Handles Windows PowerShell complexities
- Guarantees output capture and error handling

**Housekeeping Automation**
- Never delete files (archive instead)
- Automated cleanup scripts
- Proper temp file management

**Cross-Project Learning**
- Standardized documentation patterns
- Reusable code patterns
- Knowledge sharing between projects

## Benefits

### For Development Teams
- **Faster Onboarding**: New agents instantly understand project structure
- **Consistent Quality**: Standardized approaches across all projects
- **Knowledge Retention**: Documentation-first approach prevents knowledge loss
- **Reduced Maintenance**: Self-documenting, organized codebases

### For AI Agents
- **Clear Operating Instructions**: No ambiguity about how to approach tasks
- **Expanded Capabilities**: Framework for tackling complex, multi-step projects
- **Safety Guardrails**: Built-in protections against destructive operations
- **Efficiency**: Reuse patterns and solutions across projects

## Version History

- **v2.2** (2025-10-20): Hardened terminal execution for Windows PowerShell
- **v2.1** (2025-10-18): Added housekeeping automation and temp file management
- **v2.0** (2025-10-15): Global rollout with centralized API documentation
- **v1.0**: Initial RTFM-first approach

## Contributing

To contribute to SBEP:

1. All changes must be documented in `SBEP_Core/SBEP-POLICY-CHANGELOG.md`
2. Updates to core protocol require version increment in `SBEP-MANIFEST.md`
3. New templates or tools go in `SBEP_Core/`
4. Examples and case studies go in `examples/`

## License

This protocol is designed for internal use and knowledge sharing. Adapt freely for your organization's needs.

## Support

- Core Documentation: `SBEP-MANIFEST.md`
- Implementation Help: `SBEP_Core/README.md`
- Troubleshooting: `SBEP_Core/HOUSEKEEPING-SOP.md`

---

**"Read, Try, Then Ask"** - The SBEP Way