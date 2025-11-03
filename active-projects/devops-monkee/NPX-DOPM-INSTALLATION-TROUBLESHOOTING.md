# Troubleshooting npx dopm Installation Issues

This guide addresses common problems when installing or using `devops-monkee` (dopm) via npx.

## Quick Installation

The recommended installation method is via npm:

```bash
npm install -g devops-monkee
```

After installation, you can use any of these commands:
- `dopm` (shortest)
- `sbep` 
- `devops-monkee`

## Common Issues and Solutions

### 1. npx Command Not Found

**Problem**: `npx` command is not recognized.

**Solutions**:

#### Verify Node.js and npm Installation
```bash
node -v
npm -v
```

If these don't work, install Node.js from [nodejs.org](https://nodejs.org/).

#### Check npx Availability
```bash
npx -v
```

If npx is not available:
```bash
npm install -g npx
```

#### Verify PATH Configuration

**Windows:**
- Ensure `C:\Program Files\nodejs\` is in your PATH
- Or use: `C:\Users\<username>\AppData\Roaming\npm`

**macOS/Linux:**
- Ensure `/usr/local/bin` is in your PATH
- Check with: `echo $PATH`

### 2. Using npx to Run devops-monkee Without Global Install

If you want to use `npx` instead of global installation:

```bash
npx devops-monkee init .
```

**Note**: Using npx will download and execute the package temporarily each time, which may be slower.

### 3. Windows-Specific Issues

**Problem**: npx doesn't work in PowerShell or CMD.

**Solutions**:

#### Use cmd /c for Windows
```bash
cmd /c npx devops-monkee init .
```

#### Use Full Path
```bash
C:\Program Files\nodejs\npx.cmd devops-monkee init .
```

#### Use npm exec (Alternative)
```bash
npm exec devops-monkee init .
```

### 4. Cache Issues

**Problem**: Corrupted npm cache causing installation failures.

**Solution**: Clear npm cache
```bash
npm cache clean --force
```

Then retry installation:
```bash
npm install -g devops-monkee
```

### 5. Proxy/Network Issues

**Problem**: Behind corporate firewall or using proxy.

**Solutions**:

#### Configure npm Proxy
```bash
npm config set proxy http://your-proxy-server:port
npm config set https-proxy http://your-proxy-server:port
```

#### Remove Proxy Settings (if not needed)
```bash
npm config rm proxy
npm config rm https-proxy
```

### 6. Permission Issues

**Problem**: Permission denied when installing globally.

**Solutions**:

#### macOS/Linux: Use sudo (not recommended for security)
```bash
sudo npm install -g devops-monkee
```

#### Better: Fix npm permissions (recommended)
```bash
mkdir ~/.npm-global
npm config set prefix '~/.npm-global'
export PATH=~/.npm-global/bin:$PATH
```

Add the export line to your `~/.bashrc` or `~/.zshrc` for persistence.

#### Windows: Run PowerShell/CMD as Administrator
Right-click → "Run as Administrator"

### 7. Outdated npm Version

**Problem**: Old npm version causing compatibility issues.

**Solution**: Update npm
```bash
npm install -g npm@latest
```

Verify:
```bash
npm -v
```

### 8. Package Not Found

**Problem**: `npm ERR! 404 Not Found` when trying to install.

**Solutions**:

#### Verify Package Name
The correct package name is `devops-monkee` (with hyphen).

#### Check npm Registry
```bash
npm config get registry
```

Should show: `https://registry.npmjs.org/`

If not, reset it:
```bash
npm config set registry https://registry.npmjs.org/
```

#### Search Package
```bash
npm search devops-monkee
```

## Recommended Installation Method

**For Regular Use**: Global installation is recommended
```bash
npm install -g devops-monkee
```

This allows you to use:
```bash
dopm init .
sbep init .
devops-monkee init .
```

**For One-Time Use**: Use npx
```bash
npx devops-monkee init .
```

## Verification

After installation, verify it works:

```bash
# Check version
dopm --version
# or
sbep --version
# or
devops-monkee --version

# Check help
dopm --help
```

## Additional Resources

- **npm Package**: https://www.npmjs.com/package/devops-monkee
- **GitHub Repository**: https://github.com/that-guy-jamie/devops-monkee

## Still Having Issues?

If none of these solutions work:

1. Check the [npm CLI issues](https://github.com/npm/cli/issues)
2. Check the [devops-monkee GitHub issues](https://github.com/that-guy-jamie/devops-monkee/issues)
3. Verify Node.js version compatibility (Node.js 16+ recommended)
4. Try using `npm exec` instead of `npx`:
   ```bash
   npm exec devops-monkee init .
   ```

