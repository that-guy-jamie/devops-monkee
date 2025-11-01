# Hyper-V Boot Issue Fix

**Problem**: VM shows "No operating system was loaded" with boot errors  
**Cause**: Common Generation 2 VM + Ubuntu compatibility issue  
**Solution**: Disable Secure Boot and fix DVD attachment

---

## 🔧 Fix Commands (Run in Admin PowerShell)

```powershell
# 1. Stop the VM first
Stop-VM -Name "astro-dev-ubuntu" -Force

# 2. Add DVD with correct path  
Add-VMDvdDrive -VMName "astro-dev-ubuntu" -Path "C:\Users\james\Downloads\ubuntu-24.04.3-live-server-amd64.iso"

# 3. DISABLE Secure Boot (Generation 2 VMs have this issue with Ubuntu)
Set-VMFirmware -VMName "astro-dev-ubuntu" -EnableSecureBoot Off

# 4. Set boot order (DVD first for installation)
$dvd = Get-VMDvdDrive -VMName "astro-dev-ubuntu"
Set-VMFirmware -VMName "astro-dev-ubuntu" -FirstBootDevice $dvd

# 5. Start VM again
Start-VM -Name "astro-dev-ubuntu"

# 6. Connect to see Ubuntu installer
vmconnect localhost "astro-dev-ubuntu"
```

---

## 🎯 What Should Happen

After running these commands, you should see:
- **Ubuntu installer boot screen** (purple/orange)
- **"Try or Install Ubuntu Server"** menu
- **Select**: "Install Ubuntu Server" 
- **Press**: Enter

**This will get you to the actual Ubuntu installer where we can configure SSH server.**

---

## 🚨 If Still Having Issues

**Alternative: Use Generation 1 VM** (more compatible):
```powershell
# Remove current VM and create Generation 1
Remove-VM -Name "astro-dev-ubuntu" -Force
Remove-Item "C:\Users\james\VMs\astro-dev-ubuntu.vhdx" -Force

# Create Generation 1 VM (more stable with Ubuntu)
New-VM -Name "astro-dev-ubuntu-gen1" -MemoryStartupBytes 4GB -Generation 1 -SwitchName "Default Switch" -NewVHDPath "C:\Users\james\VMs\astro-dev-ubuntu-gen1.vhdx" -NewVHDSizeBytes 50GB

# Set processors
Set-VM -Name "astro-dev-ubuntu-gen1" -ProcessorCount 2

# Add DVD
Set-VMDvdDrive -VMName "astro-dev-ubuntu-gen1" -Path "C:\Users\james\Downloads\ubuntu-24.04.3-live-server-amd64.iso"

# Start VM
Start-VM -Name "astro-dev-ubuntu-gen1"
vmconnect localhost "astro-dev-ubuntu-gen1"
```

**Generation 1 VMs have fewer boot issues with Ubuntu.**
