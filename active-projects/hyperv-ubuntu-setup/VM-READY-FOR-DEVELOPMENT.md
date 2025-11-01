# VM Ready for Development

## Status: VM is Functional ✅

### What Works
- ✅ Ubuntu 24.04.3 LTS installed
- ✅ Internet connectivity (apt update/upgrade working)
- ✅ SSH server running and functional (tested with `ssh localhost`)
- ✅ VM accessible via Hyper-V console
- ✅ IP: 192.168.1.240 on home network

### What Doesn't Work (Yet)
- ⏳ Windows PowerShell → VM SSH (hangs, likely Windows Firewall)
  - Can ping VM from Windows
  - SSH works within VM
  - Issue is Windows-side, not VM-side

### Workaround
**Use Hyper-V console directly** - we don't need Windows SSH for now.

## Next Steps: Development Environment Setup

Run these commands in the Ubuntu VM terminal:

### 1. Install Development Tools
```bash
# Install essential development tools
sudo apt install -y git make curl wget vim

# Install WP-CLI (WordPress command line)
curl -O https://raw.githubusercontent.com/wp-cli/builds/gh-pages/phar/wp-cli.phar
chmod +x wp-cli.phar
sudo mv wp-cli.phar /usr/local/bin/wp
wp --info
```

### 2. Create SSH Key for WP Engine
```bash
# Generate SSH key for WP Engine access
ssh-keygen -t ed25519 -C "astro-dev-wpengine" -f ~/.ssh/wpengine_key -N ""

# Display public key (to add to WP Engine)
cat ~/.ssh/wpengine_key.pub
```

### 3. Configure SSH for WP Engine
```bash
# Create SSH config
cat > ~/.ssh/config << 'EOF'
Host astro1
  HostName astro1.ssh.wpengine.net
  User astro1
  IdentityFile ~/.ssh/wpengine_key
  StrictHostKeyChecking accept-new

Host ownersnetwork
  HostName ownersnetwork.ssh.wpengine.net
  User ownersnetwork
  IdentityFile ~/.ssh/wpengine_key
  StrictHostKeyChecking accept-new

Host ownersnetworkd
  HostName ownersnetworkd.ssh.wpengine.net
  User ownersnetworkd
  IdentityFile ~/.ssh/wpengine_key
  StrictHostKeyChecking accept-new
EOF

chmod 600 ~/.ssh/config
```

### 4. Clone ASTRO Project
```bash
# Create projects directory
mkdir -p ~/projects
cd ~/projects

# Clone from GitHub (if using Git)
# Or we'll transfer files from Windows later
```

### 5. Test WP Engine Access
```bash
# After adding public key to WP Engine:
ssh astro1 "echo 'WP Engine Connection: OK'"
```

## Why This Works Better Than Windows

- ✅ Native bash (no PowerShell escaping issues)
- ✅ Reliable SSH/SCP (the memory we created about heredoc method)
- ✅ Make works natively
- ✅ All Linux tools available
- ✅ Can use project Makefiles directly
- ✅ No more "SSH + heredoc + WP-CLI" workarounds needed

## Windows Firewall Troubleshooting (Later)

If we want Windows → VM SSH later:

```powershell
# On Windows (as Administrator)
New-NetFirewallRule -DisplayName "Allow SSH to Hyper-V VM" -Direction Outbound -LocalPort 22 -Protocol TCP -Action Allow
```

But for now, Hyper-V console is sufficient.

## Ready for Production Work

Once SSH keys are set up and tested, this VM can:
1. Deploy to all WP Engine environments
2. Run project Makefiles
3. Execute reliable deployment scripts
4. Handle all WordPress management via WP-CLI

**The Windows terminal issues are solved.**

