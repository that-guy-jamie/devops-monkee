# SBEP Addendum: SCP Deployment Workflow

## Purpose
Canonical documentation for secure file transfer using SCP over SSH Gateway with the `-O` flag for SBEP-compliant deployments.

## Standard SCP Command Pattern

### Basic Syntax
```bash
scp -O -P 22 -i "path/to/private_key" source_file user@host:/destination/path
```

### SSH Gateway Configuration
When using SSH Gateway (recommended for production environments):

```bash
# Example: Upload to WP Engine via SSH Gateway
scp -O -P 22 -i "C:\Users\username\.ssh\automation_key" \
  local_file.php \
  environment@environment.ssh.wpengine.net:/sites/environment/target/path/
```

### Key Parameters
- **`-O`**: Uses the legacy SCP protocol (required for compatibility)
- **`-P 22`**: Specifies SSH port (standard port 22)
- **`-i`**: Specifies private key file path
- **Host Format**: `{environment}@{environment}.ssh.wpengine.net`
- **Target Path**: `/sites/{environment}/{wp-path}/`

## Pre-Deployment Checklist
- [ ] SSH key authentication configured and tested
- [ ] Target environment and paths verified
- [ ] File permissions appropriate for web server
- [ ] Backup of existing files (if overwriting)
- [ ] Deployment logged per EP-DEP-001 if manual

## Post-Deployment Verification
- [ ] Files transferred successfully
- [ ] File permissions correct (typically 644 for files, 755 for directories)
- [ ] Web application functionality verified
- [ ] No broken links or missing assets
- [ ] Cache cleared if applicable

## Security Considerations
- Always use key-based authentication (never passwords)
- Restrict SSH key permissions to deployment-specific paths
- Log all manual deployments with full command audit trail
- Rotate SSH keys periodically (quarterly recommended)

## Emergency Procedures
If standard deployment scripts fail:
1. Follow EP-DEP-001 exception policy
2. Use SCP commands documented above
3. Create detailed incident log
4. Schedule post-incident review to restore automated deployments

## Related Documentation
- EP-DEP-001: Manual Deployment Exception Policy
- SBEP-MANIFEST.md: Core protocol requirements
- Individual project `sds/SBEP-MANDATE.md`: Project-specific procedures