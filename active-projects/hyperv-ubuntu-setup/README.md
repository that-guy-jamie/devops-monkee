# Hyper-V Ubuntu Development Environment Setup

**Purpose**: Eliminate Windows terminal execution issues and create reliable WordPress deployment environment  
**Target**: Local Ubuntu VM via Hyper-V for ASTRO project development  
**Benefits**: Native SSH/SCP tools, reliable terminal execution, better SBEP compliance

---

## 🎯 Why Hyper-V Ubuntu Solves Our Problems

### Current Issues with Windows Environment
- ❌ `run_terminal_cmd` hanging and interruption issues
- ❌ SSH command execution inconsistencies  
- ❌ SCP subsystem failures on WP Engine
- ❌ Complex PowerShell syntax requirements
- ❌ Unreliable output capture methods

### Ubuntu VM Benefits
- ✅ **Native bash/SSH execution** (no wrapper scripts needed)
- ✅ **Reliable scp -O commands** (direct SBEP compliance)
- ✅ **Consistent terminal behavior** (no hanging/interruption)
- ✅ **Standard Linux tooling** (curl, grep, find work normally)
- ✅ **Better development workflow** (native git, npm, etc.)

---

## 🚀 Hyper-V Ubuntu Setup Guide

### Pre-Reboot Setup
1. **Enable Hyper-V Feature** (requires reboot):
   ```powershell
   # Run as Administrator
   Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V -All
   ```

2. **Download Ubuntu Server** (while machine reboots):
   - Ubuntu Server 24.04 LTS ISO
   - URL: https://ubuntu.com/download/server

### Post-Reboot Setup

#### 1. Create Ubuntu VM
```powershell
# In Hyper-V Manager
New-VM -Name "astro-dev-ubuntu" -MemoryStartupBytes 4GB -Generation 2 -SwitchName "Default Switch"
Set-VM -Name "astro-dev-ubuntu" -ProcessorCount 2
Add-VMDvdDrive -VMName "astro-dev-ubuntu" -Path "path\to\ubuntu-server.iso"
```

#### 2. Ubuntu Installation
- **Minimal install** (no GUI needed)
- **Enable SSH server** during install
- **User**: `astro-dev`
- **Hostname**: `astro-dev-ubuntu`

#### 3. Essential Tools Installation
```bash
# SSH into VM after install
sudo apt update && sudo apt upgrade -y
sudo apt install -y curl wget git nano vim unzip
sudo apt install -y openssh-client
```

#### 4. WordPress CLI Tools
```bash
# Install WP-CLI for direct WordPress management
curl -O https://raw.githubusercontent.com/wp-cli/wp-cli/v2.10.0/wp-cli.phar
chmod +x wp-cli.phar
sudo mv wp-cli.phar /usr/local/bin/wp
```

#### 5. SSH Key Setup
```bash
# Copy SSH key from Windows host
mkdir -p ~/.ssh
chmod 700 ~/.ssh

# Copy from Windows: C:\Users\james\.ssh\ownersnetwork_automation_key
# To Ubuntu: ~/.ssh/ownersnetwork_automation_key
chmod 600 ~/.ssh/ownersnetwork_automation_key
```

---

## 📁 Project Structure Differences

### `/projects/` (Main Windows Projects)
- **Location**: `C:\Users\james\Desktop\Projects\`
- **Purpose**: Primary development workspace with all ASTRO project files
- **Access**: Windows file system, Cursor editor access
- **Use**: Source code, documentation, primary project management

### Local Project (This Setup Guide)
- **Location**: `C:\Users\james\Desktop\Projects\hyperv-ubuntu-setup\`
- **Purpose**: Environment setup and VM configuration documentation
- **Scope**: Single-purpose setup project, not part of main ASTRO development
- **Outcome**: Enable better access to main `/projects/` work

### Ubuntu VM Projects
- **Location**: `/home/astro-dev/projects/` (mounted from Windows)
- **Purpose**: Linux-native access to Windows project files
- **Method**: Shared folder or git clone from main projects
- **Advantage**: Native Linux tooling for deployment

---

## 🔧 Integration Strategy

### Option 1: Shared Folders (Recommended)
```bash
# Mount Windows Projects folder into Ubuntu VM
# Hyper-V Enhanced Session Mode allows folder sharing
sudo mount -t drvfs 'C:\Users\james\Desktop\Projects' /mnt/windows-projects
ln -s /mnt/windows-projects ~/projects
```

### Option 2: Git Clone Method
```bash
# Clone ASTRO project repository into Ubuntu
cd ~
git clone [astro-repo-url] astro-ubuntu
cd astro-ubuntu
```

### Option 3: Hybrid Approach
- **Windows**: Primary development, file editing (Cursor)
- **Ubuntu VM**: Deployment execution, SSH operations
- **Sync**: rsync or git between environments

---

## 🎯 Development Workflow

### Windows (Primary Development)
- Edit files in Cursor
- Documentation and planning
- Code review and testing

### Ubuntu VM (Deployment Execution)
- SSH to staging/production
- SCP file transfers using SBEP methods
- WP-CLI database operations
- Reliable terminal command execution

### Result
- **Best of both worlds**: Windows development experience + Linux deployment reliability
- **SBEP compliance**: Native Linux tools follow SBEP patterns exactly
- **No more terminal issues**: Reliable command execution

---

## 📋 Post-Setup Verification

After VM setup, test core functionality:

```bash
# Test SSH connection to staging
ssh -i ~/.ssh/ownersnetwork_automation_key ownersnetwork@ownersnetwork.ssh.wpengine.net "echo 'Ubuntu VM SSH test successful'"

# Test SCP deployment
scp -O -P 22 -i ~/.ssh/ownersnetwork_automation_key test-file.txt ownersnetwork@ownersnetwork.ssh.wpengine.net:/tmp/

# Test WP-CLI through SSH
ssh -i ~/.ssh/ownersnetwork_automation_key ownersnetwork@ownersnetwork.ssh.wpengine.net "cd /sites/ownersnetwork && wp cache status"
```

---

## ⚡ Immediate Benefits for ASTRO Project

1. **Reliable deployments** using exact SBEP methods
2. **Faster iteration cycles** (no command hanging)
3. **Better cache management** (direct WP Engine integration)
4. **Native Linux scripting** for complex operations
5. **Consistent tool behavior** across sessions

**This will transform the development experience and eliminate the deployment issues we've been fighting.**

---

## 🚀 Next Steps After Reboot

1. **Complete Hyper-V install and VM creation**
2. **Set up Ubuntu with development tools** 
3. **Configure shared folder access to Windows projects**
4. **Test ASTRO deployment workflow from Ubuntu**
5. **Document the new reliable development process**

**Go ahead with the reboot - I'll have the complete Hyper-V setup ready when you're back!**

