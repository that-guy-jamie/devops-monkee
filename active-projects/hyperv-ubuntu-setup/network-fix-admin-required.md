# Fix Ubuntu VM Network - Admin PowerShell Required

**Issue**: VM has no internet access (DNS resolution fails)  
**Cause**: Only Internal network switches, need External switch  
**Solution**: Create External switch bridged to Wi-Fi adapter

---

## 🔧 Step-by-Step Network Fix

### 1. **Open PowerShell as Administrator**
- **Right-click** on PowerShell icon
- **Select**: "Run as Administrator"  
- **Should see**: `PS C:\Windows\system32>` (with elevated privileges)

### 2. **Stop VM and Check Current State**
```powershell
# Stop VM for network reconfiguration
Stop-VM -Name "astro-dev-ubuntu" -Force

# Verify VM is stopped
Get-VM -Name "astro-dev-ubuntu"

# Check current network adapter
Get-VMNetworkAdapter -VMName "astro-dev-ubuntu"
```

### 3. **Create External Network Switch**
```powershell
# Create External switch bridged to Wi-Fi (your main internet connection)
New-VMSwitch -Name "External-WiFi" -NetAdapterName "Wi-Fi" -AllowManagementOS $true

# Verify switch created
Get-VMSwitch
```

### 4. **Configure VM to Use External Switch**  
```powershell
# Remove current network adapter
Remove-VMNetworkAdapter -VMName "astro-dev-ubuntu" -Name "Network Adapter"

# Add new adapter with External switch
Add-VMNetworkAdapter -VMName "astro-dev-ubuntu" -SwitchName "External-WiFi"

# Start VM with new network configuration  
Start-VM -Name "astro-dev-ubuntu"
```

### 5. **Test Network Connectivity**
```powershell
# Connect to VM console
vmconnect localhost "astro-dev-ubuntu"
```

**In Ubuntu VM after network fix:**
```bash
# Test internet connectivity
ping -c 3 8.8.8.8

# Test DNS resolution
nslookup theastro.org

# Test SSH to ASTRO servers
ssh -i ~/.ssh/astro_ubuntu_key theastro1@theastro1.ssh.wpengine.net "echo 'Ubuntu SSH test'"
```

---

## ✅ Success Criteria

**Network fix successful when:**
- [ ] `ping 8.8.8.8` succeeds (internet connectivity)
- [ ] `nslookup theastro.org` resolves (DNS working)  
- [ ] SSH connection attempts reach servers (reliable deployment tools)

**Then we can immediately resume ASTRO deployment work with reliable Ubuntu tools!**

---

## ⚠️ If External Switch Fails

**Alternative approach:**
```powershell
# Use NAT networking instead
New-VMSwitch -Name "NAT-Switch" -SwitchType Internal
New-NetIPAddress -IPAddress 192.168.100.1 -PrefixLength 24 -InterfaceAlias "vEthernet (NAT-Switch)"  
New-NetNat -Name "NAT-Network" -InternalIPInterfaceAddressPrefix 192.168.100.0/24

# Configure VM for NAT
Set-VMNetworkAdapter -VMName "astro-dev-ubuntu" -SwitchName "NAT-Switch"
```

**Start with the External-WiFi switch approach first - it's the most straightforward.**
