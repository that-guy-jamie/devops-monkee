# Plugin Architecture Proposal: Making Tools Replaceable

## Current State

DevOps Monkee currently has hardcoded governance tools:
- `Validator` - concrete class
- `Synchronizer` - concrete class  
- `Auditor` - concrete class
- `Governor` - concrete class

These are not replaceable or extensible.

## Goal: Baked-In Tool Building

Make tool building part of the framework core:
1. **Plugin Interface** - Define contracts for each tool type
2. **Plugin Registry** - Discover and load custom tools
3. **Default Tools** - Current tools as default implementations
4. **Tool Templates** - Scaffolding for building new tools
5. **Configuration** - Specify which tools to use

## Proposed Architecture

### 1. Tool Interfaces

```typescript
// src/interfaces/tool.ts
export interface IValidator {
  validate(projectPath: string, options?: any): Promise<ValidationResult>;
  getName(): string;
  getVersion(): string;
}

export interface ISynchronizer {
  sync(projectPath: string, options?: any): Promise<SyncResult>;
  getName(): string;
}

export interface IAuditor {
  audit(projectPath: string, options?: any): Promise<AuditResult>;
  getName(): string;
}

export interface IGovernor {
  govern(projectPath: string, options?: any): Promise<GovernanceStatus>;
  getName(): string;
}
```

### 2. Plugin Registry

```typescript
// src/core/plugin-registry.ts
export class PluginRegistry {
  private validators: Map<string, IValidator> = new Map();
  private synchronizers: Map<string, ISynchronizer> = new Map();
  private auditors: Map<string, IAuditor> = new Map();
  private governors: Map<string, IGovernor> = new Map();

  registerValidator(name: string, tool: IValidator): void;
  getValidator(name?: string): IValidator;
  // ... similar for other tools
}
```

### 3. Default Implementations

Current tools become default plugins:
- `DefaultValidator` implements `IValidator`
- `DefaultSynchronizer` implements `ISynchronizer`
- etc.

### 4. Configuration

```json
// .devops-monkee/config.json
{
  "tools": {
    "validator": {
      "type": "default", // or "custom", "plugin"
      "module": "./custom-validator.js" // optional for custom
    },
    "synchronizer": "default",
    "auditor": "default",
    "governor": "default"
  },
  "plugins": [
    "./plugins/my-custom-tool.js"
  ]
}
```

### 5. Tool Template Generator

```bash
devops-monkee tool:create validator my-custom-validator
# Generates:
# - src/tools/my-custom-validator.ts
# - tests/my-custom-validator.test.ts
# - docs/my-custom-validator.md
```

## Benefits

1. **Extensibility** - Users can build custom governance tools
2. **Replaceability** - Swap default tools with custom implementations
3. **Composability** - Mix and match tools from different sources
4. **Testing** - Mock tools for testing
5. **Community** - Others can build and share tools

## Implementation Phases

### Phase 1: Interface Extraction
- Create interfaces for each tool type
- Refactor existing tools to implement interfaces
- Maintain backward compatibility

### Phase 2: Plugin Registry
- Build plugin discovery and loading system
- Support local plugins and npm packages
- Configuration system

### Phase 3: Tool Templates
- CLI command to scaffold new tools
- Documentation templates
- Example implementations

### Phase 4: Community Tools
- Plugin marketplace/documentation
- Validation of plugin compatibility
- Version management for plugins

## Example: Custom Validator

```typescript
// user's custom-validator.ts
import { IValidator, ValidationResult } from 'devops-monkee';

export class CustomValidator implements IValidator {
  async validate(projectPath: string): Promise<ValidationResult> {
    // Custom validation logic
    return { score: 95, grade: 'A', issues: [], recommendations: [] };
  }
  
  getName() { return 'custom-validator'; }
  getVersion() { return '1.0.0'; }
}
```

Then use it:
```json
{
  "tools": {
    "validator": {
      "type": "custom",
      "module": "./custom-validator"
    }
  }
}
```

## Questions

1. Should this be in v1.1.0 or wait for v2.0?
2. Backward compatibility - ensure existing usage still works?
3. Plugin format - npm packages, local files, or both?
4. Validation - how strict should plugin interfaces be?

