# SBEP Tool Building Guidelines

**Part of SBEP Constitution v2.2** - Tool building and sharing standards

## Overview

The SBEP protocol includes provisions for building, sharing, and managing tools across projects and teams. This document defines the standards and practices for tool development.

## Tool Building Principles

### 1. Security First
All tools must use SBEP security utilities:
- Path validation to prevent traversal attacks
- Log sanitization to prevent secret leakage
- Secure command execution to prevent injection

### 2. Reusability
Tools should be:
- **Generic**: Work across multiple projects
- **Configurable**: Accept parameters for customization
- **Documented**: Include JSDoc comments and examples

### 3. Type Safety
Tools must be:
- Written in TypeScript
- Export proper types
- Validate inputs

## Tool Structure

### Standard Tool Template

```typescript
/**
 * Tool Name
 * 
 * Description of what this tool does
 * 
 * @category CategoryName
 * @version 1.0.0
 * @author Your Name
 */

import { validatePath, sanitizeLog, secureExec } from 'devops-monkee';

export interface ToolOptions {
  // Define your options
}

export class MyTool {
  /**
   * Main tool function
   */
  async execute(options: ToolOptions): Promise<Result> {
    // Use SBEP utilities
    const safePath = validatePath(options.path, process.cwd());
    const safeLog = sanitizeLog(options.message);
    
    // Your tool logic
    
    return result;
  }
}

export default MyTool;
```

## Tool Categories

Tools should be categorized for organization:

- **Validation**: Tools that validate or check things
- **Transformation**: Tools that modify or transform data
- **Generation**: Tools that generate code or files
- **Analysis**: Tools that analyze or audit
- **Integration**: Tools that integrate with external services
- **Utility**: General-purpose helper tools

## Tool Registration

### Using Tool Manager (v1.3.0)

```typescript
import { ToolManager } from 'devops-monkee';

const manager = new ToolManager();

await manager.registerTool({
  name: 'my-tool',
  version: '1.0.0',
  description: 'Does something useful',
  author: 'Your Name',
  category: 'Utility',
  entryPoint: './tools/my-tool.ts',
  dependencies: ['some-package'],
  tags: ['validation', 'security']
});
```

### Manual Registration

Create a `.sbep/tools-registry.json`:

```json
{
  "tools": [
    {
      "name": "my-tool",
      "version": "1.0.0",
      "description": "Does something useful",
      "author": "Your Name",
      "category": "Utility",
      "entryPoint": "./tools/my-tool.ts",
      "dependencies": [],
      "tags": ["validation"]
    }
  ],
  "lastUpdated": "2025-11-03T00:00:00.000Z",
  "version": "1.0.0"
}
```

## Tool Sharing

### Pattern 1: npm Package (Recommended)

Create a separate npm package for your team's tools:

```json
{
  "name": "@your-org/shared-tools",
  "version": "1.0.0",
  "main": "dist/index.js",
  "exports": {
    ".": "./dist/index.js",
    "./tool-name": "./dist/tool-name.js"
  },
  "dependencies": {
    "devops-monkee": "^1.2.0"
  }
}
```

### Pattern 2: Git Submodule

Include tools as a git submodule in your projects.

### Pattern 3: Template Repository

Maintain a template repository with commonly used tools.

## Tool Validation

Before sharing a tool, validate it:

```typescript
import { ToolManager } from 'devops-monkee';

const manager = new ToolManager();
const validation = await manager.validateTool('./tools/my-tool.ts');

if (!validation.valid) {
  console.error('Tool validation failed:', validation.issues);
}
```

## Tool Discovery

Find available tools:

```typescript
// List all tools
const tools = await manager.listTools();

// Find by category
const validationTools = await manager.listTools('Validation');

// Find by name
const tool = await manager.findTool('my-tool');
```

## Best Practices

### 1. Use SBEP Utilities
Always use shared utilities from `devops-monkee`:
- `validatePath()` - Path validation
- `sanitizeLog()` - Log sanitization
- `secureExec()` - Secure execution

### 2. Document Everything
Include:
- JSDoc comments
- Usage examples
- Type definitions
- Error handling

### 3. Test Tools
Write tests for your tools:
- Unit tests for logic
- Integration tests for workflows
- Security tests for vulnerabilities

### 4. Version Control
- Use semantic versioning
- Document breaking changes
- Maintain changelog

### 5. Security Review
Before sharing:
- Review for security issues
- Check for secret exposure
- Validate input handling
- Audit dependencies

## Tool Building Workflow

1. **Design**: Plan tool functionality and interface
2. **Build**: Implement using SBEP utilities
3. **Test**: Write comprehensive tests
4. **Validate**: Run tool validation
5. **Document**: Add JSDoc and examples
6. **Register**: Add to tool registry
7. **Share**: Publish to npm or repository
8. **Maintain**: Update and improve over time

## Constitutional Requirements

Per SBEP Constitution v2.2:

1. **All tools must use SBEP security utilities**
2. **Tools must be documented with JSDoc**
3. **Tools must pass validation before sharing**
4. **Breaking changes require version bump**
5. **Security review required before public release**

## Examples

See `templates/example-tool.ts` for a complete example.

## Related Documentation

- [SBEP Security Guidelines](./SBEP-SECURITY-GUIDELINES.md)
- [Tool Sharing Templates](../templates/README.md)
- [API Reference](./api/)

---

**Part of SBEP Constitution v2.2** - Tool building standards ensure consistency and security across all shared tools.

