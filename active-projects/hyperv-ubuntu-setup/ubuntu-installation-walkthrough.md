# Ubuntu Installation Walkthrough - Step by Step

**Current Status**: In Ubuntu installer terminal  
**Goal**: Get to SSH server enable option

---

## 🖥️ Installation Screens (In Order)

### 1. **Language Selection**
- Select: **English** (or your preferred language)
- Press **Enter**

### 2. **Installer Update** (if prompted)
- Select: **Continue without updating** (faster)
- Press **Enter**

### 3. **Keyboard Configuration**  
- **Layout**: English (US) or your layout
- **Variant**: English (US) or keep default
- Press **Done**

### 4. **Choose Type of Install**
- Select: **Ubuntu Server** (should be default)
- Press **Done**

### 5. **Network Configuration**
- **Usually auto-configures** (shows IP address)
- If shows IP address: Press **Done** 
- If no IP: Check "Enable this network interface" and press **Done**

### 6. **Configure Proxy** (if shown)
- Leave **blank** (no proxy)
- Press **Done**

### 7. **Configure Ubuntu Archive Mirror**
- Use **default mirror** (fastest)
- Press **Done**

### 8. **Guided Storage Configuration**
- Select: **Use an entire disk** 
- Select: **VHDX Virtual disk** (should be only option)
- Press **Done**

### 9. **Storage Layout Confirmation**
- Review shows ~50GB disk
- Press **Done**
- **Confirm destructive action**: Yes (it's a new virtual disk)

### 10. **Profile Setup** ⚠️ **IMPORTANT**
- **Your name**: `astro-dev`
- **Your server's name**: `astro-dev-ubuntu`  
- **Pick a username**: `astro-dev`
- **Choose a password**: [create and **WRITE DOWN**]
- **Confirm your password**: [same password]
- Press **Done**

### 11. **SSH Setup** 🎯 **CRITICAL STEP**
- **Install OpenSSH server**: ✅ **Check this box!**
- **Import SSH identity**: Leave unchecked (we'll add keys later)
- Press **Done**

### 12. **Featured Server Snaps** (optional packages)
- **Skip all** (we'll install what we need manually)
- Press **Done**

---

## ⏳ Installation Progress

After the SSH step:
- **Installation begins** (takes 5-10 minutes)
- **Shows progress** with package installation
- **"Installation complete"** message appears
- **Reboot now**: Yes

**After reboot:**
- **Login prompt** appears  
- **Username**: `astro-dev`
- **Password**: [the one you created]

---

## 🎯 What You'll See Next

Once logged in, you should see:
```bash
astro-dev@astro-dev-ubuntu:~$ 
```

**That's our target!** Then we can:
1. Install development tools
2. Set up SSH keys  
3. Test reliable ASTRO deployment workflow

**Keep following the installer screens until you reach the SSH server option - that's the crucial step for our deployment workflow!**
