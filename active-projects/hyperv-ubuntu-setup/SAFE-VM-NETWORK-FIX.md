# Safe VM Network Fix (No Host Network Changes)

## Step 1: Start the VM

**Option A - Hyper-V Manager (Easiest):**
1. Open Hyper-V Manager from Start Menu
2. Right-click "astro-dev-ubuntu"
3. Click "Start"
4. Double-click VM to open console window

**Option B - Admin PowerShell:**
```powershell
Start-VM -Name "astro-dev-ubuntu"
```

## Step 2: Login to Ubuntu
- Username: `astro-dev`
- Password: `astro123`

## Step 3: Configure Network (Inside Ubuntu VM)

Run these commands in the Ubuntu terminal:

```bash
# Check current network config
ip addr show

# Edit netplan config
sudo nano /etc/netplan/00-installer-config.yaml
```

### The file should contain:
```yaml
network:
  version: 2
  ethernets:
    eth0:
      dhcp4: true
```

**If it's different, replace the contents with the above.**

Save and exit nano:
- Press `Ctrl+X`
- Press `Y` to confirm
- Press `Enter` to save

### Apply the configuration:
```bash
# Apply network config
sudo netplan apply

# Wait 5 seconds, then test
ping -c 4 8.8.8.8
```

## Step 4: Verify Internet Access

```bash
# Test DNS resolution
ping -c 4 google.com

# Test package manager
sudo apt update
```

## Expected Results
- `ping 8.8.8.8` should show replies (not "Network is unreachable")
- `ping google.com` should resolve and show replies
- `sudo apt update` should connect and fetch package lists

## Troubleshooting

### If still no internet:
```bash
# Check what interface name actually exists
ip link show

# It might be called something other than eth0
# Common names: eth0, enp0s3, ens33

# If your interface is named differently, update netplan:
sudo nano /etc/netplan/00-installer-config.yaml
# Change "eth0" to match your actual interface name
```

### Check DHCP assignment:
```bash
# See if you got an IP address
ip addr show

# Should show something like: 172.x.x.x (Default Switch range)
```

## Why This is Safe
- ✅ Only changes config INSIDE the VM
- ✅ Default Switch already exists on host
- ✅ No physical adapter binding
- ✅ Host internet completely unaffected
- ✅ VM gets NAT-based internet through Default Switch

## Once Working
Come back and let me know - we'll then set up SSH keys for remote access.

