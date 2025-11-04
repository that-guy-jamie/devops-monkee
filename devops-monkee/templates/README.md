# Tool Sharing Templates

This directory contains **examples** showing how to share tools across your team using the `devops-monkee` package.

## Pattern for Sharing Tools

### 1. Create Your Tool

Create a tool file that exports reusable functionality:

```typescript
// my-team-tool.ts
import { validatePath, sanitizeLog } from 'devops-monkee';

export class MyTeamTool {
  async doSomething(safe: string): Promise<void> {
    const validatedPath = validatePath(safe, process.cwd());
    // Your logic here
  }
}

export default MyTeamTool;
```

### 2. Publish as npm Package

Create a separate npm package for your team's tools:

```json
{
  "name": "@your-org/shared-tools",
  "version": "1.0.0",
  "main": "dist/index.js",
  "exports": {
    ".": "./dist/index.js",
    "./tools/my-tool": "./dist/tools/my-tool.js"
  }
}
```

### 3. Team Members Import

```typescript
import { MyTeamTool } from '@your-org/shared-tools';
import { validatePath } from 'devops-monkee'; // Base utilities

const tool = new MyTeamTool();
await tool.doSomething(userInput);
```

## Best Practices

1. **Use Base Utilities**: Import utilities from `devops-monkee` instead of reimplementing
2. **Security First**: Always use `validatePath`, `sanitizeLog`, `secureExec`
3. **Type Safety**: Export TypeScript types for your tools
4. **Documentation**: Include JSDoc comments
5. **Testing**: Write tests for shared tools

## Example Files

- `example-tool.ts` - Basic tool template showing the pattern

## Why This Pattern?

- **Prevents Duplication**: One implementation, many users
- **Security**: Shared utilities prevent common mistakes
- **Consistency**: Same tools across all projects
- **Maintainability**: Update once, benefits all

---

**Remember**: These are examples showing the pattern. Create your own tools following this structure.

