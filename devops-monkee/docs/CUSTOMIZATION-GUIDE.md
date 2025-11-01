# SBEP Customization Guide

## Philosophy: Fully Configurable

SBEP is a **framework**, not a rigid set of rules. When you download DevOps Monkee, you should be able to customize everything to fit your organization's needs:

- **Constitution** - Modify core principles
- **Validation Rules** - Add/remove/change what gets validated
- **Standards** - Adjust quality thresholds
- **Workflows** - Customize processes
- **Tools** - Build or swap governance tools

## What You Can Customize

### 1. Constitution (`CONSTITUTION.md`)

The SBEP Constitution is **your starting point**, not a rigid requirement.

**Default:** DevOps Monkee includes a default constitution with core SBEP principles
**Customize:** Edit `CONSTITUTION.md` to match your organization's values

**Example:**
- Default: "Documentation First"
- Your org: "Documentation First, but allow exceptions for rapid prototyping"
- Just edit the file and update your validation rules accordingly

### 2. Validation Schema (`VALIDATION-SCHEMA.json`)

Define what gets validated and how it's scored.

**Default:** DevOps Monkee includes standard validation rules
**Customize:** 
- Change scoring weights
- Add custom validation checks
- Remove checks that don't apply
- Adjust thresholds (what's an A vs B grade?)

### 3. Validation Rules (`src/governance/validator.ts`)

The actual validation logic.

**Default:** Built-in validators
**Customize:**
- Extend the `Validator` class
- Add organization-specific checks
- Modify existing validation logic
- Create custom validators per project type

### 4. Quality Standards

**Default:** SBEP standard quality metrics
**Customize:**
- Adjust documentation requirements
- Change code quality thresholds
- Modify safety requirement levels
- Add domain-specific standards

### 5. Process Workflows

**Default:** SBEP-defined processes
**Customize:**
- Adapt success capture process to your needs
- Modify tool extraction workflows
- Customize documentation templates
- Create organization-specific processes

## How to Customize

### Option 1: Edit Files Directly (Current)

**Currently Works:**
1. Install `devops-monkee`
2. Edit `CONSTITUTION.md` in your project
3. Override `VALIDATION-SCHEMA.json` in your project
4. Validator will use your custom files (if implemented)

**Needs Implementation:**
- Configuration system to point to custom files
- Validator needs to load custom schema from project directory
- Constitution loading from project vs default

### Option 2: Fork and Modify

1. Fork `devops-monkee` on GitHub
2. Modify `CONSTITUTION.md` for your org
3. Update validation schema/rules
4. Build and use your customized version
5. **This always works - you own the code**

### Option 2: Configuration Override

Use configuration files to override defaults:

```json
// .devops-monkee/config.json
{
  "constitution": "./custom-constitution.md",
  "validation": {
    "schema": "./custom-validation-schema.json",
    "rules": "./custom-validator.js"
  },
  "standards": {
    "documentation": {
      "required": true,
      "minQuality": 70
    },
    "safety": {
      "rollbackRequired": true,
      "exceptionPolicy": "./custom-exceptions.md"
    }
  }
}
```

### Option 3: Plugin Architecture (Future)

Replace default implementations with custom ones:

```json
{
  "tools": {
    "validator": {
      "type": "custom",
      "module": "./my-custom-validator.js"
    },
    "constitution": {
      "source": "./my-constitution.md"
    }
  }
}
```

## Examples of Customization

### Example 1: Relaxed Documentation for Startups

**Custom Constitution:**
```markdown
# Our Organization's Constitution

## Modified Principles

### Documentation First (Startup Variant)
- Core documentation required
- Detailed docs optional for MVPs
- Full documentation before production release
```

### Example 2: Enhanced Security for Healthcare

**Custom Validation:**
```json
{
  "safety": {
    "weight": 0.40,  // Increased from 0.15
    "requirements": [
      "HIPAA compliance check",
      "Data encryption validation",
      "Audit trail verification"
    ]
  }
}
```

### Example 3: Tech Stack Specific

**Custom Validator:**
```typescript
// custom-validator.ts
import { Validator } from 'devops-monkee';

export class PythonValidator extends Validator {
  async validateQualityMetrics(projectPath: string) {
    // Python-specific quality checks
    // - Pylint compliance
    // - Type hint coverage
    // - Test coverage requirements
  }
}
```

## Best Practices

1. **Start with Defaults** - Use SBEP defaults as baseline
2. **Customize Incrementally** - Change one thing at a time
3. **Document Changes** - Record why you changed what you did
4. **Version Control** - Track your customizations
5. **Share Learnings** - If you find better patterns, contribute back (optional)

## What You Can't Customize (And Why)

**Core Framework:** The CLI interface, plugin system, basic structure
- These need to remain consistent for ecosystem compatibility

**But everything else is fair game:**
- Constitution ✓
- Validation rules ✓
- Quality standards ✓
- Processes ✓
- Tools ✓

## Customization Boundaries

### Recommended Customizations
- Constitution to match org values
- Validation weights/checks for your context
- Quality thresholds for your standards
- Process workflows for your needs

### Not Recommended (But Possible)
- Breaking plugin interfaces (loses compatibility)
- Removing core safety checks entirely (risky)
- Ignoring versioning (breaks sync)

### Always Supported
- Adding custom checks
- Adjusting weights/thresholds
- Modifying constitution
- Creating custom tools
- Building custom processes

## Configuration Priority

1. **Command-line flags** - Highest priority
2. **Project config** (`.devops-monkee/config.json`) - Second
3. **User config** (`~/.devops-monkee/config.json`) - Third
4. **Organization defaults** - Fourth
5. **SBEP defaults** - Fallback

## Validation of Customizations

SBEP can validate your customizations:

```bash
# Validate that your customizations are valid
devops-monkee validate:config

# Checks:
# - Configuration syntax is valid
# - Custom validators implement required interfaces
# - Constitution structure follows conventions
# - No breaking changes to core framework
```

## Contributing Customizations Back

While customizations are private to your org, you can optionally:
- Share improved validation patterns (anonymized)
- Contribute generic tool improvements
- Suggest framework enhancements

But this is **completely optional** - your customizations stay private.

## Current Implementation Status

**What Works Now:**
- ✅ Fork the repo and modify anything
- ✅ Edit validation schema JSON directly
- ✅ Extend Validator class in your own code

**What Needs Building:**
- ⚠️ Configuration system to load custom constitution/schema from project directory
- ⚠️ Validator to check for project-level overrides before using defaults
- ⚠️ CLI support for `--config` flag to specify custom files

**Current Workaround:**
- Fork the repo and modify the code directly
- Or extend classes programmatically
- Full configurability via config files coming in future version

## Summary

**SBEP is a framework you adapt, not a rigid set of rules you follow.**

The philosophy is clear: Download it, customize it, make it yours. The constitution, validation rules, standards, and processes are all meant to be adapted to your organization's needs.

**Currently:** Fork and modify (full control)
**Future:** Configuration-driven customization (easier)

The only requirement: Follow the **process** of customization (document it, version it, validate it).

