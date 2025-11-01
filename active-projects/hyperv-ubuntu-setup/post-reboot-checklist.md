# Post-Reboot Hyper-V Setup Checklist

**After Windows reboot with Hyper-V enabled**

---

## ✅ Immediate Steps

### 1. Verify Hyper-V Installation
```powershell
# Check Hyper-V is enabled
Get-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V
# Should show "State: Enabled"
```

### 2. Launch Hyper-V Manager
- **Start Menu** → "Hyper-V Manager" 
- Should open without errors

### 3. Download Ubuntu Server ISO
- **URL**: https://ubuntu.com/download/server
- **Version**: Ubuntu Server 24.04.3 LTS
- **Size**: ~1.5GB download

---

## 🖥️ VM Creation Steps

### 1. Create New VM
```
Hyper-V Manager → Action → New → Virtual Machine
- Name: astro-dev-ubuntu
- Generation: 2
- Memory: 4096 MB (4GB)
- Network: Default Switch
- Hard Disk: 40GB (dynamic)
```

### 2. Configure VM
```
VM Settings:
- Processors: 2 CPUs
- Secure Boot: Disabled (for Ubuntu compatibility)
- DVD Drive: Mount Ubuntu ISO
```

### 3. Ubuntu Installation
```
Boot VM → Install Ubuntu Server
- Language: English
- Network: DHCP (should auto-configure)
- Storage: Use entire disk
- User: astro-dev
- Install SSH server: YES
```

---

## ⚙️ Post-Install Configuration

### 1. Get VM IP Address
```bash
# Inside Ubuntu VM
ip addr show
# Note the IP address (usually 172.x.x.x)
```

### 2. SSH from Windows
```powershell
# From Windows to Ubuntu VM
ssh astro-dev@[VM-IP-ADDRESS]
```

### 3. Install Development Tools
```bash
# Essential tools
sudo apt update && sudo apt upgrade -y
sudo apt install -y git curl wget nano vim unzip zip
sudo apt install -y build-essential

# WordPress CLI
curl -O https://raw.githubusercontent.com/wp-cli/wp-cli/v2.10.0/wp-cli.phar
chmod +x wp-cli.phar
sudo mv wp-cli.phar /usr/local/bin/wp
```

### 4. SSH Key Setup
```bash
# Create .ssh directory
mkdir -p ~/.ssh
chmod 700 ~/.ssh

# Copy SSH key from Windows (you'll need to transfer this)
# C:\Users\james\.ssh\ownersnetwork_automation_key → ~/.ssh/ownersnetwork_automation_key
chmod 600 ~/.ssh/ownersnetwork_automation_key

# Test SSH to staging
ssh -i ~/.ssh/ownersnetwork_automation_key ownersnetwork@ownersnetwork.ssh.wpengine.net "echo 'Ubuntu VM SSH test'"
```

---

## 📂 Project Access Strategy

### Option 1: Shared Folders (Easiest)
```bash
# Mount Windows projects directory 
sudo mkdir /mnt/projects
sudo mount -t drvfs 'C:\Users\james\Desktop\Projects' /mnt/projects
ln -s /mnt/projects ~/projects
```

### Option 2: Git Clone (Isolated)
```bash
# Clone ASTRO project into Ubuntu
git clone [repo-url] ~/astro-dev
cd ~/astro-dev
```

### Option 3: File Sync (Hybrid)
```bash
# Sync specific files as needed
rsync -av /mnt/projects/astro/src-themes/ ~/astro-staging/
```

---

## 🎯 Test Deployment Workflow

### Verify All Functions Work
```bash
# 1. SSH to production
ssh -i ~/.ssh/ownersnetwork_automation_key theastro1@theastro1.ssh.wpengine.net "echo 'Production SSH OK'"

# 2. SCP file transfer
scp -O -P 22 -i ~/.ssh/ownersnetwork_automation_key test.txt theastro1@theastro1.ssh.wpengine.net:/tmp/

# 3. WP-CLI through SSH  
ssh -i ~/.ssh/ownersnetwork_automation_key theastro1@theastro1.ssh.wpengine.net "cd /sites/theastro1 && wp cache flush"

# 4. Database operations
ssh -i ~/.ssh/ownersnetwork_automation_key theastro1@theastro1.ssh.wpengine.net "cd /sites/theastro1 && wp db search 'test'"
```

### Expected Results
- ✅ **All commands execute immediately** (no hanging)
- ✅ **Reliable output capture** (stdout/stderr work normally)  
- ✅ **SBEP compliance** (native scp -O support)
- ✅ **Consistent behavior** across sessions

---

## 🚀 Development Workflow

### 1. Windows (Primary)
- **Cursor editor** for code development
- **File management** and documentation
- **Git operations** and version control

### 2. Ubuntu VM (Deployment)
- **SSH operations** to staging/production
- **Database content updates** using WP-CLI
- **Cache management** and verification
- **Deployment script execution**

### 3. Coordination
- **File sharing** via mounted projects directory
- **Command execution** piped from Windows to Ubuntu if needed
- **Best of both worlds**: Windows development + Linux deployment

---

## 📊 Expected Impact on ASTRO Project

### Problems Solved
- ✅ **No more hanging commands** during deployment
- ✅ **Reliable SSH/SCP operations** for theme/content updates  
- ✅ **Better cache management** with direct WP Engine tools
- ✅ **Consistent SBEP compliance** using native Linux methods

### Workflow Improvements
- ✅ **Faster deployment cycles** (minutes, not hours)
- ✅ **Reliable verification** using curl and native tools
- ✅ **Better debugging** with standard Linux troubleshooting
- ✅ **Scalable approach** for other projects in `/projects/`

---

## 🎯 Success Criteria

**VM Setup Complete When:**
- [ ] Ubuntu VM boots and SSH works
- [ ] Can access Windows projects directory
- [ ] SSH to staging/production works from VM
- [ ] SCP deployment completes without errors
- [ ] WP-CLI operations execute reliably
- [ ] WordPress cache flush takes effect immediately

**Ready to resume ASTRO deployment with reliable tooling!** 🚀
