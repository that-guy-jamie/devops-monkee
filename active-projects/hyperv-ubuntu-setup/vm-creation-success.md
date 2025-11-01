# VM Creation Success - Continue Setup

**Status**: ✅ VM Created Successfully  
**Name**: astro-dev-ubuntu  
**Memory**: 4GB  
**CPUs**: 2  
**Issue**: ISO path mismatch (easily fixed)

---

## 🔧 Fix ISO Path and Continue

```powershell
# Add DVD with correct ISO path
Add-VMDvdDrive -VMName "astro-dev-ubuntu" -Path "C:\Users\james\Downloads\ubuntu-24.04.3-live-server-amd64.iso"

# Set boot order (boot from DVD first for installation)
$dvd = Get-VMDvdDrive -VMName "astro-dev-ubuntu"
Set-VMFirmware -VMName "astro-dev-ubuntu" -FirstBootDevice $dvd

# Start VM for installation
Start-VM -Name "astro-dev-ubuntu"

# Connect to VM console for installation
vmconnect localhost "astro-dev-ubuntu"
```

---

## 🐧 Ubuntu Installation Quick Settings

**When the installer starts:**

### Installation Options:
- **Language**: English
- **Installer update**: Skip
- **Keyboard**: Your layout
- **Installation type**: Ubuntu Server
- **Network**: Enable (auto-configure)
- **Proxy**: None
- **Archive mirror**: Default
- **Storage**: Use entire disk → Done

### Profile Setup:
- **Your name**: astro-dev
- **Server name**: astro-dev-ubuntu
- **Username**: astro-dev  
- **Password**: [create and remember!]

### SSH Setup: ✅ **CRITICAL**
- **Install OpenSSH server**: ✅ **YES** (check this box!)

### Package Selection:
- **Skip all** optional packages for now

### Installation Complete:
- **Reboot now**: Yes
- **Remove installation medium**: Done automatically

---

## 📝 What We'll Get

**After installation completes:**
- Ubuntu server running in VM
- SSH server enabled (for remote access)
- Ready for development tool installation
- Direct access to native Linux SSH/SCP commands
- Solution to Windows terminal execution issues

**Next step after installation**: SSH into the Ubuntu VM and install development tools for ASTRO deployment work.
