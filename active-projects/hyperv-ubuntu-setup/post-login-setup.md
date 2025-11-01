# Ubuntu Development Environment Setup

**Status**: ✅ Logged in successfully as astro-dev  
**Next**: Install development tools for ASTRO deployment

---

## 🛠️ Quick Development Setup (Run These Commands)

### 1. **Update System & Install Essentials**
```bash
# Update package lists
sudo apt update

# Install essential development tools
sudo apt install -y curl wget git nano vim unzip openssh-client

# Verify tools installed
which ssh
which scp
```

### 2. **Install WordPress CLI**
```bash
# Download WP-CLI
curl -O https://raw.githubusercontent.com/wp-cli/wp-cli/v2.10.0/wp-cli.phar

# Make executable and install
chmod +x wp-cli.phar
sudo mv wp-cli.phar /usr/local/bin/wp

# Verify installation
wp --version
```

### 3. **Check SSH Server Status**
```bash
# Verify SSH server is running (should show active)
sudo systemctl status ssh

# If not active, enable it:
# sudo systemctl enable --now ssh
```

### 4. **Get VM IP Address**
```bash
# Get IP address for SSH access from Windows
ip addr show
```

**Note the IP address - you'll need it for SSH access from Windows!**

---

## 🔑 SSH Key Setup

### Copy SSH Key from Windows
```bash
# Create SSH directory
mkdir -p ~/.ssh
chmod 700 ~/.ssh

# Create SSH key file (we'll copy content from Windows)
nano ~/.ssh/ownersnetwork_automation_key
```

**In nano editor:**
1. **Copy content** from Windows key file: `C:\Users\james\.ssh\ownersnetwork_automation_key`
2. **Paste into nano** (right-click in terminal)
3. **Save**: Ctrl+X, then Y, then Enter
4. **Set permissions**: `chmod 600 ~/.ssh/ownersnetwork_automation_key`

---

## 🧪 Test Deployment Workflow

### Test SSH Connection to ASTRO Staging
```bash
ssh -i ~/.ssh/ownersnetwork_automation_key ownersnetwork@ownersnetwork.ssh.wpengine.net "echo 'Ubuntu SSH test successful'"
```

### Test SCP File Transfer (SBEP Method)  
```bash
echo "Test from Ubuntu" > test-deploy.txt
scp -O -P 22 -i ~/.ssh/ownersnetwork_automation_key test-deploy.txt ownersnetwork@ownersnetwork.ssh.wpengine.net:/tmp/
```

### Test WordPress Operations
```bash
ssh -i ~/.ssh/ownersnetwork_automation_key ownersnetwork@ownersnetwork.ssh.wpengine.net "cd /sites/ownersnetwork && wp cache status"
```

---

## ✅ Success Indicators

**When setup complete, you should be able to:**
- ✅ SSH to WordPress servers without hanging
- ✅ Use SCP for reliable file transfers  
- ✅ Execute WP-CLI commands without interruption
- ✅ **Resume ASTRO deployment work** with reliable tools

**Start with the system update and tool installation - let me know if any commands fail!**
