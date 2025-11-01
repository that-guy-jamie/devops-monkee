# Hyper-V Network Switch Setup for Internet Access

**Problem**: Only Internal switches available - no internet access  
**Solution**: Create External switch bridged to physical network adapter

---

## 🔧 Create External Network Switch

### 1. **Find Your Network Adapter**
```powershell
# List network adapters (find your main internet connection)
Get-NetAdapter | Where-Object {$_.Status -eq "Up"}
```

**Look for your main network adapter** (usually Ethernet or Wi-Fi)

### 2. **Create External Switch**
```powershell
# Create External switch bridged to your network adapter
# Replace "Ethernet" with your adapter name from step 1
New-VMSwitch -Name "External-Internet" -NetAdapterName "Ethernet" -AllowManagementOS $true
```

**Or if you're on Wi-Fi:**
```powershell
# For Wi-Fi adapter (check the exact name from Get-NetAdapter)
New-VMSwitch -Name "External-Internet" -NetAdapterName "Wi-Fi" -AllowManagementOS $true
```

### 3. **Configure VM to Use External Switch**
```powershell
# Remove current network adapter
Remove-VMNetworkAdapter -VMName "astro-dev-ubuntu" -Name "Network Adapter"

# Add new adapter with External switch
Add-VMNetworkAdapter -VMName "astro-dev-ubuntu" -SwitchName "External-Internet"

# Start VM
Start-VM -Name "astro-dev-ubuntu"
```

---

## 🧪 Alternative: Quick Test Without Internet

**If you want to test SSH functionality immediately (while we figure out networking):**

We can set up SSH keys and test ASTRO deployment **right now** - external SSH connections should work even without Ubuntu internet access.

**Ubuntu has basic tools already:**
- `ssh` ✅
- `scp` ✅  
- Basic shell tools ✅

**We can:**
1. **Set up SSH key** (manual copy)
2. **Test connection** to theastro1.ssh.wpengine.net
3. **Verify deployment reliability**
4. **Fix Ubuntu internet later** for additional tools

**Which approach do you prefer:**
- **A)** Fix networking first (run the commands above)
- **B)** Test SSH deployment immediately with existing tools

Either way gets us to reliable ASTRO deployment capability!
