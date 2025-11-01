# Network Disaster Postmortem

## What Happened
Attempted to create/reconfigure Hyper-V External VMSwitch, which killed the host workstation's internet connection.

## Root Cause
**External VMSwitch creation binds to physical network adapters**, essentially taking them over for Hyper-V use. When this process:
- Fails due to permissions
- Is interrupted
- Has configuration errors

...it can leave the physical adapter in a disabled/broken state, killing host internet.

## What We Did Wrong
1. Attempted to create External switch without fully understanding the risk
2. Didn't verify Default Switch was properly configured first
3. Didn't test netplan config inside Ubuntu VM before modifying host networking

## The Correct Approach

### For VM Internet Access:
1. **Use Default Switch** (already exists, provides NAT)
2. **Fix Ubuntu netplan config** inside the VM
3. **NEVER create External switches** unless absolutely necessary and with full backup plan

### Default Switch provides:
- NAT-based internet to VMs
- Host machine unaffected
- DHCP automatically assigned
- No physical adapter binding required

### To fix Ubuntu VM networking:
```bash
# Inside Ubuntu VM
sudo nano /etc/netplan/00-installer-config.yaml

# Should contain:
network:
  version: 2
  ethernets:
    eth0:
      dhcp4: true

sudo netplan apply
```

## Prevention Rules
1. ✅ **DO**: Use Default Switch for VMs
2. ✅ **DO**: Fix networking inside the VM via netplan
3. ✅ **DO**: Test with `ping 8.8.8.8` inside VM
4. ❌ **DON'T**: Create External VMSwitches without explicit user approval
5. ❌ **DON'T**: Bind to physical adapters
6. ❌ **DON'T**: Modify host networking to fix VM issues

## Recovery
- Host reboot restored internet (physical adapter reset)
- VM still needs netplan configuration
- Default Switch is sufficient for our needs

## Status
- ✅ Host internet: RESTORED (after reboot)
- ⏳ VM internet: PENDING (needs netplan fix)
- ✅ Lesson learned: Don't touch host networking

