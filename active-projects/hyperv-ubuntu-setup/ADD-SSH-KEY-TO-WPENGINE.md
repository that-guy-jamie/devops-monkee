# Add SSH Key to WP Engine

## Public Key to Add

```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAICFVzno/06bR/31uK2PbtsT0bDCgkdZ/1HWSjxCuEkutE astro-dev-wpengine
```

## Steps to Add Key in WP Engine Portal

1. **Go to:** https://my.wpengine.com/
2. **Login** with your WP Engine credentials
3. **Click your username** (top right) → **SSH Keys**
4. **Click "Add SSH Key"**
5. **Paste the public key above** into the text field
6. **Give it a name:** `astro-dev-ubuntu-vm`
7. **Click "Add Key"**

## Which Environments Need This Key?

The key should automatically work for all your environments once added to your account:
- `astro1` (production)
- `ownersnetwork` (staging)
- `ownersnetworkd` (dev)

## After Adding the Key

Once added (takes ~5 minutes to propagate), test from Ubuntu VM:

```bash
# Test production
ssh astro1@astro1.ssh.wpengine.net "echo 'Production SSH: OK'"

# Test staging
ssh ownersnetwork@ownersnetwork.ssh.wpengine.net "echo 'Staging SSH: OK'"

# Test dev
ssh ownersnetworkd@ownersnetworkd.ssh.wpengine.net "echo 'Dev SSH: OK'"
```

## If Using SSH Config (Recommended)

Create `~/.ssh/config`:

```bash
cat > ~/.ssh/config << 'EOF'
Host astro1
  HostName astro1.ssh.wpengine.net
  User astro1
  IdentityFile ~/.ssh/wpengine_key
  StrictHostKeyChecking accept-new

Host ownersnetwork
  HostName ownersnetwork.ssh.wpengine.net
  User ownersnetwork
  IdentityFile ~/.ssh/wpengine_key
  StrictHostKeyChecking accept-new

Host ownersnetworkd
  HostName ownersnetworkd.ssh.wpengine.net
  User ownersnetworkd
  IdentityFile ~/.ssh/wpengine_key
  StrictHostKeyChecking accept-new
EOF

chmod 600 ~/.ssh/config
```

Then you can use short commands:
```bash
ssh astro1 "wp cache flush"
ssh ownersnetwork "wp post list"
scp file.html ownersnetworkd:/path/to/destination
```

Much cleaner!

