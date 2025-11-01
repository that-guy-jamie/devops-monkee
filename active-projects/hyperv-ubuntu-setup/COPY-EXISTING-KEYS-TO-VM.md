# Copy Existing Windows SSH Keys to Ubuntu VM

## Problem
WP Engine portal keeps rejecting new keys for unknown reasons.

## Solution
Copy your existing working Windows SSH keys to the Ubuntu VM.

## Your Existing Windows Keys (that work with WP Engine)
Located in: `C:\Users\james\.ssh\`

- `ownersnetwork_automation_key` (private)
- `ownersnetwork_automation_key.pub` (public)

## Steps to Copy Keys

### Option A: Direct Copy/Paste (Simplest)

1. **On Windows**, open PowerShell and run:
   ```powershell
   Get-Content C:\Users\james\.ssh\ownersnetwork_automation_key
   ```
   Copy the entire output (including `-----BEGIN` and `-----END` lines)

2. **In Ubuntu VM**, create the private key file:
   ```bash
   nano ~/.ssh/ownersnetwork_automation_key
   ```
   Paste the key content, save with `Ctrl+X`, `Y`, `Enter`

3. **On Windows**, get the public key:
   ```powershell
   Get-Content C:\Users\james\.ssh\ownersnetwork_automation_key.pub
   ```
   Copy the output

4. **In Ubuntu VM**, create the public key file:
   ```bash
   nano ~/.ssh/ownersnetwork_automation_key.pub
   ```
   Paste the content, save with `Ctrl+X`, `Y`, `Enter`

5. **Set proper permissions in Ubuntu VM:**
   ```bash
   chmod 600 ~/.ssh/ownersnetwork_automation_key
   chmod 644 ~/.ssh/ownersnetwork_automation_key.pub
   ```

6. **Test immediately:**
   ```bash
   ssh -i ~/.ssh/ownersnetwork_automation_key ownersnetwork@ownersnetwork.ssh.wpengine.net "echo 'SSH: OK'"
   ```

### Option B: Use Shared Folder (If Available)

If you can mount the Windows C: drive in the VM, you could copy directly.

## After Keys Are Copied

Create SSH config for easy access:

```bash
cat > ~/.ssh/config << 'EOF'
Host astro1
  HostName astro1.ssh.wpengine.net
  User astro1
  IdentityFile ~/.ssh/ownersnetwork_automation_key

Host ownersnetwork
  HostName ownersnetwork.ssh.wpengine.net
  User ownersnetwork
  IdentityFile ~/.ssh/ownersnetwork_automation_key

Host ownersnetworkd
  HostName ownersnetworkd.ssh.wpengine.net
  User ownersnetworkd
  IdentityFile ~/.ssh/ownersnetwork_automation_key
EOF

chmod 600 ~/.ssh/config
```

Then you can use short commands:
```bash
ssh astro1 "wp cache flush"
ssh ownersnetwork "wp post list"
```

## This Bypasses the WP Engine Portal Issue Entirely

Since the key is already authorized on WP Engine (from your Windows setup), copying it to Ubuntu should work immediately!

