# Transfer SSH Key from Windows to Ubuntu VM via HTTP

## Quick Method: Python HTTP Server

### Step 1: On Windows PowerShell (outside Cursor)

```powershell
# Go to your SSH directory
cd C:\Users\james\.ssh

# Start a simple HTTP server (Python should be installed)
python -m http.server 8000
```

Leave this running. It will serve your SSH keys folder on port 8000.

### Step 2: In Ubuntu VM Terminal

```bash
# Download the private key from Windows
curl -o ~/.ssh/ownersnetwork_automation_key http://192.168.1.240:8000/ownersnetwork_automation_key

# Download the public key
curl -o ~/.ssh/ownersnetwork_automation_key.pub http://192.168.1.240:8000/ownersnetwork_automation_key.pub

# Set proper permissions
chmod 600 ~/.ssh/ownersnetwork_automation_key
chmod 644 ~/.ssh/ownersnetwork_automation_key.pub
```

**Note:** Replace `192.168.1.240` with your Windows machine's IP if different.

### Step 3: Test WP Engine Access

```bash
ssh -i ~/.ssh/ownersnetwork_automation_key ownersnetwork@ownersnetwork.ssh.wpengine.net "echo 'SSH: OK'"
```

### Step 4: Stop the HTTP Server

Go back to Windows PowerShell and press `Ctrl+C` to stop the server.

## If Python Not Available

Alternative using Windows File Sharing (more complex, skip if HTTP works).

