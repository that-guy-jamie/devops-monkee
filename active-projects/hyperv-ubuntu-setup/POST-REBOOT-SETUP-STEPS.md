# Hyper-V Ubuntu Setup - Post-Reboot Steps

**Status**: Reboot complete, ready for Hyper-V configuration  
**Goal**: Create reliable Ubuntu development environment for ASTRO deployments

---

## 🔧 Step 1: Verify Hyper-V Installation

```powershell
# Check if Hyper-V is enabled (run in Admin PowerShell)
Get-WindowsOptionalFeature -FeatureName Microsoft-Hyper-V -Online

# Should show: State : Enabled
```

**If not enabled:**
```powershell
# Enable Hyper-V (requires another reboot)
Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V -All -Restart
```

---

## 🖥️ Step 2: Create Ubuntu VM

### A. Download Ubuntu Server
- **URL**: https://ubuntu.com/download/server
- **Version**: 24.04 LTS (Long Term Support)
- **Size**: ~1.5GB download
- **Save to**: `C:\Users\james\Downloads\ubuntu-24.04-server-amd64.iso`

### B. Create Virtual Machine
```powershell
# Open Hyper-V Manager
# Start → "Hyper-V Manager"

# Create New VM:
New-VM -Name "astro-dev-ubuntu" -MemoryStartupBytes 4GB -Generation 2 -SwitchName "Default Switch" -NewVHDPath "C:\Users\james\VMs\astro-dev-ubuntu.vhdx" -NewVHDSizeBytes 50GB
```

### C. Configure VM Settings
```powershell
# Set processor count
Set-VM -Name "astro-dev-ubuntu" -ProcessorCount 2

# Attach Ubuntu ISO
Add-VMDvdDrive -VMName "astro-dev-ubuntu" -Path "C:\Users\james\Downloads\ubuntu-24.04-server-amd64.iso"

# Configure boot order (boot from DVD first)
$dvd = Get-VMDvdDrive -VMName "astro-dev-ubuntu"
Set-VMFirmware -VMName "astro-dev-ubuntu" -FirstBootDevice $dvd
```

---

## 🐧 Step 3: Ubuntu Installation

### A. Start VM and Install
```powershell
# Start the VM
Start-VM -Name "astro-dev-ubuntu"

# Connect to VM console
vmconnect localhost "astro-dev-ubuntu"
```

### B. Installation Settings
- **Language**: English
- **Keyboard**: Your layout
- **Installation type**: Ubuntu Server (minimal)
- **Network**: Enable (should auto-configure)
- **Storage**: Use entire disk
- **Profile setup**:
  - **Name**: astro-dev
  - **Server name**: astro-dev-ubuntu  
  - **Username**: astro-dev
  - **Password**: [your choice - write it down!]
- **SSH Setup**: ✅ **ENABLE** Install OpenSSH server
- **Packages**: Skip additional packages for now

### C. Complete Installation
- **Reboot**: Remove ISO and reboot VM
- **First login**: Use astro-dev credentials
- **Network check**: `ip addr show` (note the IP address)

---

## 🛠️ Step 4: Development Tools Setup

### A. Essential Package Installation
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install development essentials
sudo apt install -y curl wget git nano vim unzip zip
sudo apt install -y openssh-client sshpass
sudo apt install -y python3 python3-pip nodejs npm
```

### B. WordPress CLI Installation
```bash
# Install WP-CLI
curl -O https://raw.githubusercontent.com/wp-cli/wp-cli/v2.10.0/wp-cli.phar
chmod +x wp-cli.phar
sudo mv wp-cli.phar /usr/local/bin/wp

# Verify installation
wp --version
```

### C. SSH Key Setup
```bash
# Create SSH directory
mkdir -p ~/.ssh
chmod 700 ~/.ssh

# We'll copy the Windows SSH key in next step
```

---

## 🔑 Step 5: SSH Key Transfer

### Method 1: Copy via Shared Folder (if enabled)
```bash
# Copy from mounted Windows drive
cp /mnt/windows-projects/.ssh/ownersnetwork_automation_key ~/.ssh/
chmod 600 ~/.ssh/ownersnetwork_automation_key
```

### Method 2: Manual Copy (if no shared folders)
```bash
# Create key file
nano ~/.ssh/ownersnetwork_automation_key

# Paste contents from Windows key file:
# Get-Content "C:\Users\james\.ssh\ownersnetwork_automation_key" 
# Copy output and paste into nano

# Set permissions
chmod 600 ~/.ssh/ownersnetwork_automation_key
```

---

## 🧪 Step 6: Test Deployment Workflow

### A. Test SSH Connection
```bash
ssh -i ~/.ssh/ownersnetwork_automation_key ownersnetwork@ownersnetwork.ssh.wpengine.net "echo 'Ubuntu SSH test successful'"
```

### B. Test SCP Transfer (SBEP Method)
```bash
# Create test file
echo "Test content" > test-deploy.txt

# Test SCP deployment
scp -O -P 22 -i ~/.ssh/ownersnetwork_automation_key test-deploy.txt ownersnetwork@ownersnetwork.ssh.wpengine.net:/tmp/

# Verify
ssh -i ~/.ssh/ownersnetwork_automation_key ownersnetwork@ownersnetwork.ssh.wpengine.net "cat /tmp/test-deploy.txt"
```

### C. Test WordPress Operations
```bash
# Test WP-CLI through SSH (the operations that hang on Windows)
ssh -i ~/.ssh/ownersnetwork_automation_key ownersnetwork@ownersnetwork.ssh.wpengine.net "cd /sites/ownersnetwork && wp cache flush"
```

---

## ✅ Success Criteria

**Setup Complete When:**
- [ ] Ubuntu VM boots and SSH server running
- [ ] SSH connection to staging/production works
- [ ] SCP file transfer works reliably  
- [ ] WP-CLI commands execute without hanging
- [ ] Can access Windows project files from Ubuntu

**Expected Result**: Reliable execution of all SBEP deployment methods that were problematic on Windows.

---

## 🎯 Next Phase: Resume ASTRO Work

Once Ubuntu VM is ready:
1. **Fix remaining ASTRO cache issues** using reliable Linux tools
2. **Complete pattern deployments** with consistent command execution  
3. **Verify all language fixes** are live on production
4. **Establish new development workflow** for future ASTRO updates

**This setup will solve our deployment reliability issues permanently.**
