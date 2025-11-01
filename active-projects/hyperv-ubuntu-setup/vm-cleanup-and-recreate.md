# VM Cleanup and Recreation

**Issue**: VHD file already exists from previous VM  
**Solution**: Complete cleanup then recreate

---

## 🧹 Complete Cleanup (Run These Commands)

```powershell
# 1. Remove existing VM completely
Remove-VM -Name "astro-dev-ubuntu" -Force

# 2. Delete the VHD file 
Remove-Item "C:\Users\james\VMs\astro-dev-ubuntu.vhdx" -Force

# 3. Create VMs directory if it doesn't exist
New-Item -ItemType Directory -Path "C:\Users\james\VMs" -Force

# 4. Now recreate VM with same settings
New-VM -Name "astro-dev-ubuntu" -MemoryStartupBytes 4GB -Generation 2 -SwitchName "Default Switch" -NewVHDPath "C:\Users\james\VMs\astro-dev-ubuntu.vhdx" -NewVHDSizeBytes 50GB

# 5. Configure VM
Set-VM -Name "astro-dev-ubuntu" -ProcessorCount 2
Set-VMFirmware -VMName "astro-dev-ubuntu" -EnableSecureBoot Off

# 6. Add Ubuntu ISO
Add-VMDvdDrive -VMName "astro-dev-ubuntu" -Path "C:\Users\james\Downloads\ubuntu-24.04.3-live-server-amd64.iso"

# 7. Set boot order
$dvd = Get-VMDvdDrive -VMName "astro-dev-ubuntu"
Set-VMFirmware -VMName "astro-dev-ubuntu" -FirstBootDevice $dvd

# 8. Start VM
Start-VM -Name "astro-dev-ubuntu"

# 9. Connect to console
vmconnect localhost "astro-dev-ubuntu"
```

---

## 💡 Simpler Password Recommendation

**This time, use a simpler password to avoid login issues:**

**During Ubuntu installation:**
- **Username**: `astro-dev`  
- **Password**: `astro123` (simple, no special characters)

**Why simpler password:**
- Eliminates keyboard layout confusion
- No special character interpretation issues  
- Easier to type during console login
- We can make it more secure later if needed

**The SSH server setup is the critical part - password complexity is less important for a development VM.**
