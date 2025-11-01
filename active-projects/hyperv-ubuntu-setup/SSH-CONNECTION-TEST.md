# SSH Connection Test - Manual Steps Required

## Current Status
- ✅ Ubuntu VM running with IP: 192.168.1.240
- ✅ SSH server installed and enabled
- ⏳ SSH connection test requires interactive input

## Issue
SSH password authentication requires interactive input that doesn't work well with automated commands.

## Manual Test (Do This Now)

Open a **NEW PowerShell window** and run:

```powershell
ssh astro-dev@192.168.1.240
```

When prompted:
1. Type `yes` and press Enter (to accept host key)
2. Enter password: `astro123`
3. You should land in Ubuntu shell
4. Run `hostname` to verify (should show: astro-dev-ubuntu)
5. Run `exit` to return to Windows

## Once SSH Works

We'll set up SSH keys so you don't need passwords:

### In Ubuntu VM:
```bash
# Generate SSH key for WP Engine
ssh-keygen -t ed25519 -C "astro-dev-wpengine" -f ~/.ssh/wpengine_key -N ""

# Display public key
cat ~/.ssh/wpengine_key.pub
```

### Then:
1. Add the public key to WP Engine (astro1 environment)
2. Test: `ssh -i ~/.ssh/wpengine_key astro1@astro1.ssh.wpengine.net "echo 'WP Engine: OK'"`

## Next: Set Up Development Environment

Once SSH works, we'll install:
- Git
- Make
- WP-CLI (for WordPress management)
- Any other development tools needed

## Why This VM?

This Ubuntu VM gives us:
- ✅ Reliable bash scripting (no Windows PowerShell quirks)
- ✅ Native SSH/SCP tools
- ✅ Make and standard Linux tooling
- ✅ Direct SSH access to WP Engine without escaping issues
- ✅ Can run the astro project's Makefile directly

This solves the "Windows terminal unreliability" issues we've been fighting.

