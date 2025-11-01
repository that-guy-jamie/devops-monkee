# Testing Guide: Configuration System

## Quick Test in Your Project

### 1. Use Custom Validation Schema

Create a project-level config and custom schema:

```bash
# In your project directory
mkdir -p .devops-monkee

# Create config file
cat > .devops-monkee/config.json << EOF
{
  "validation": {
    "schema": "./custom-validation-schema.json"
  }
}
EOF

# Copy default schema to customize
cp node_modules/devops-monkee/VALIDATION-SCHEMA.json .devops-monkee/custom-validation-schema.json

# Edit custom-validation-schema.json - modify weights, rules, etc.
```

### 2. Test Configuration Loading

```bash
# Run validation - should detect and use custom schema
devops-monkee validate .

# Should see: "Using custom validation schema from: ./.devops-monkee/custom-validation-schema.json"
```

### 3. Test Custom Constitution

```bash
# Add to .devops-monkee/config.json
{
  "constitution": {
    "source": "./my-constitution.md"
  }
}
```

Create your custom constitution file and test.

## What to Test

### Configuration System
- [ ] Config file loads from `.devops-monkee/config.json`
- [ ] Custom validation schema is used
- [ ] Falls back to defaults if config/schema missing
- [ ] Validator uses custom schema correctly

### Interface Implementation
- [ ] Validator implements IValidator interface
- [ ] getName(), getVersion(), supportsAutoFix() work

### Error Handling
- [ ] Missing config file doesn't break (uses defaults)
- [ ] Invalid config file shows helpful error
- [ ] Missing custom schema file shows warning, uses default

## Example Test Project Structure

```
my-project/
├── .devops-monkee/
│   └── config.json          # Your custom config
├── custom-validation-schema.json  # Your custom schema
├── my-constitution.md        # Your custom constitution
├── README.md
├── sds/
│   └── SBEP-MANDATE.md
└── package.json
```

## Troubleshooting

**Config not loading?**
- Check file path: `.devops-monkee/config.json` (not `.devops-monkee/config.json`)
- Check JSON syntax is valid
- Check file permissions

**Custom schema not used?**
- Verify path in config.json is correct (relative to project root)
- Check file exists at that path
- Verify JSON is valid validation schema format

**Defaults still being used?**
- Check console for warnings/errors
- Verify config file is being read (check logs)
- Ensure file paths in config are correct

## Reporting Issues

If something doesn't work:
1. Note the exact command you ran
2. Note the expected vs actual behavior
3. Check console output for errors
4. Test with default config removed (should use defaults)

