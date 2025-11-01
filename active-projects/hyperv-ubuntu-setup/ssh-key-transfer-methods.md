# SSH Key Transfer to Ubuntu VM

**Problem**: Can't copy/paste SSH key content into VM terminal  
**Solution**: Multiple alternative methods

---

## 🔧 Method 1: Display Key and Type (Easiest)

### In Windows PowerShell (outside VM):
```powershell
# Display SSH key content in readable chunks
Get-Content "C:\Users\james\.ssh\ownersnetwork_automation_key"
```

### In Ubuntu VM:
```bash
# Create key file and type content line by line
nano ~/.ssh/ownersnetwork_automation_key

# Type the key content shown in Windows PowerShell
# SSH keys are typically 3-5 lines, easier to type than expected
```

---

## 🔧 Method 2: Echo Method (Character by Character)

### In Ubuntu VM:
```bash
# Create key file using echo (build it line by line)
echo "-----BEGIN OPENSSH PRIVATE KEY-----" > ~/.ssh/ownersnetwork_automation_key
echo "[first-line-of-key-from-windows]" >> ~/.ssh/ownersnetwork_automation_key
echo "[second-line-of-key-from-windows]" >> ~/.ssh/ownersnetwork_automation_key
# Continue for each line...
echo "-----END OPENSSH PRIVATE KEY-----" >> ~/.ssh/ownersnetwork_automation_key

# Set permissions
chmod 600 ~/.ssh/ownersnetwork_automation_key
```

---

## 🔧 Method 3: Test with Temporary Key

**Create a NEW SSH key pair for testing:**

### In Ubuntu VM:
```bash
# Generate new SSH key for testing
ssh-keygen -t rsa -b 2048 -f ~/.ssh/test_key -N ""

# Copy public key (we'll add to WP Engine later)
cat ~/.ssh/test_key.pub
```

Then manually add this public key to WP Engine SSH access.

---

## 💡 Method 4: Simple File Share

### In Windows (if Hyper-V Enhanced Session enabled):
1. **Copy SSH key to simple location**: `C:\temp\ssh_key.txt`
2. **VM might auto-mount** Windows drives
3. **Copy from mounted location** in Ubuntu

---

## 🚀 Recommended: Method 1 (Display and Type)

**Run this in Windows PowerShell to see the key:**
```powershell
Get-Content "C:\Users\james\.ssh\ownersnetwork_automation_key"
```

**SSH keys are usually only 3-5 lines - much shorter than they look. You can type them line by line into nano.**

**Which method do you want to try? The display-and-type is usually fastest for SSH keys.**
