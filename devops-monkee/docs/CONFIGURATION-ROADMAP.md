# Configuration System Roadmap

## Goal: Full Configurability Without Forking

Users should be able to customize SBEP without forking the entire codebase.

## Phase 1: Project-Level Overrides (Priority)

### Configuration File Structure

```json
// .devops-monkee/config.json (in project root)
{
  "constitution": {
    "source": "./custom-constitution.md",
    "validateStructure": true
  },
  "validation": {
    "schema": "./custom-validation-schema.json",
    "validator": "./custom-validator.js"
  },
  "standards": {
    "documentation": {
      "minQuality": 70,
      "requiredSections": ["Purpose", "Usage"]
    },
    "safety": {
      "rollbackRequired": true,
      "exceptionPolicy": "./custom-exceptions.md"
    }
  }
}
```

### Validator Changes Needed

```typescript
// src/governance/validator.ts
export class Validator {
  private async loadSchema(projectPath: string): Promise<ValidationSchema> {
    const configPath = path.join(projectPath, '.devops-monkee', 'config.json');
    
    if (await fs.pathExists(configPath)) {
      const config = await fs.readJson(configPath);
      if (config.validation?.schema) {
        const customSchema = path.join(projectPath, config.validation.schema);
        if (await fs.pathExists(customSchema)) {
          return await fs.readJson(customSchema);
        }
      }
    }
    
    // Fall back to default
    return VALIDATION_SCHEMA;
  }
}
```

### CLI Support

```bash
# Use project's custom configuration
devops-monkee validate ./project --use-project-config

# Or always check for project config (default behavior)
devops-monkee validate ./project  # auto-detects .devops-monkee/config.json
```

## Phase 2: Constitution Loading

```typescript
// Load custom constitution from project or use default
async loadConstitution(projectPath: string): Promise<string> {
  const config = await this.loadConfig(projectPath);
  
  if (config.constitution?.source) {
    const customPath = path.join(projectPath, config.constitution.source);
    if (await fs.pathExists(customPath)) {
      return await fs.readFile(customPath, 'utf-8');
    }
  }
  
  // Fall back to default
  return await fs.readFile(path.join(__dirname, '../../CONSTITUTION.md'), 'utf-8');
}
```

## Phase 3: Custom Tool Registration

```typescript
// Support custom validators
async loadValidator(projectPath: string): Promise<IValidator> {
  const config = await this.loadConfig(projectPath);
  
  if (config.validation?.validator) {
    const customValidatorPath = path.join(projectPath, config.validation.validator);
    if (await fs.pathExists(customValidatorPath)) {
      const CustomValidator = require(customValidatorPath);
      return new CustomValidator();
    }
  }
  
  return new Validator();
}
```

## Implementation Checklist

- [ ] Configuration file format design
- [ ] Config loader utility
- [ ] Validator schema override support
- [ ] Constitution loading from project
- [ ] Custom validator class loading
- [ ] CLI flag support
- [ ] Documentation updates
- [ ] Backward compatibility tests
- [ ] Example configurations

## Benefits

1. **No Forking Required** - Customize via config files
2. **Version Compatibility** - Keep using latest SBEP while customizing
3. **Easy Updates** - SBEP updates don't break your customizations
4. **Team Sharing** - Commit `.devops-monkee/config.json` to repo
5. **Gradual Customization** - Start with defaults, customize incrementally

## Example: Healthcare Organization

```json
{
  "constitution": {
    "source": "./constitution-healthcare.md"
  },
  "validation": {
    "schema": "./validation-healthcare.json"
  },
  "standards": {
    "safety": {
      "weight": 0.50,
      "requirements": [
        "HIPAA compliance check",
        "Data encryption validation"
      ]
    }
  }
}
```

This allows healthcare orgs to customize without forking, while still getting SBEP updates.

