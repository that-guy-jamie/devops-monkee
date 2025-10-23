# SBEP Addendum: Reliable File Writes to WP Engine via SSH Gateway (SCP)

Context: On Windows hosts, long heredocs and wrapper-mediated writes can produce 0-byte files or hang. Direct SCP to the WP Engine SSH Gateway is the most reliable write path; direct SSH remains reliable for read-only checks and cache flushes.

Recommended Workflow
- Use SSH Gateway (not SFTP host) for SCP writes:
  - Host: <env>@<env>.ssh.wpengine.net (port 22)
  - Path: /sites/<env>/wp-content/...
- Use legacy protocol flag when the sftp subsystem closes unexpectedly:

```bash
scp -O -P 22 <local-file> <env>@<env>.ssh.wpengine.net:/sites/<env>/wp-content/<dest-path>
```

- Verify and flush cache via SSH:

```bash
ssh -p 22 <env>@<env>.ssh.wpengine.net "ls -la /sites/<env>/wp-content/<dest-dir> && wp cache flush && echo OK"
```

## Environment Management (CRITICAL)

**Always verify target environment before any write operations:**

```bash
# Check current environment
ssh -p 22 ownersnetwork@ownersnetwork.ssh.wpengine.net "echo 'STAGING: $(pwd)'"
ssh -p 22 theastro1@theastro1.ssh.wpengine.net "echo 'PRODUCTION: $(pwd)'"

# Verify before SCP (check the path in command output)
ssh -p 22 ownersnetwork@ownersnetwork.ssh.wpengine.net "ls -la /sites/ownersnetwork/wp-content/themes/" | head -3
```

**Environment-Specific Deployment Rules (Current Phase):**
- **Staging (`ownersnetwork`)**: Known issues, avoid if possible during development
- **Production (`theastro1`)**: Pre-production with solid backups, direct development OK during development phase
- **Post-Launch**: Switch to staging → production workflow with manual approval
- **Never mix environments**: Always verify SSH host and path before running SCP or deployment commands

Operational Notes
- Avoid heredocs for remote writes from this Windows host; prefer SCP.
- Direct SSH is reliable for WP-CLI read-only and cache flush.
- If CI is available (GitLab), prefer CI deploys for repeatable writes; SCP remains the manual fallback.
- Quirk: If a stray leading character appears at the prompt after completion, press Enter once before running the next command to ensure a clean line.

Scope
- This addendum augments SBEP-MANIFEST Terminal Command Execution for Windows environments interacting with WP Engine.


