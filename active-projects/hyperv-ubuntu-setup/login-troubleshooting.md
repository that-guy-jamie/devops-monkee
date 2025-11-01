# Ubuntu Login Issue Troubleshooting

**Problem**: Login incorrect with astro-dev / Country406!!as  
**Status**: Common Ubuntu installation issue - easily fixable

---

## 🔧 Troubleshooting Steps (Try in Order)

### 1. **Keyboard Layout Issue** (Most Common)
The password may have been typed with different keyboard layout during setup.

**Try typing the password very slowly and carefully:**
- Username: `astro-dev`
- Password: `Country406!!as` (type each character deliberately)

### 2. **Special Characters Issue**  
The `!!` in the password might be causing shell interpretation issues.

**Try these variations:**
- `Country406!!as` (original)
- `Country406!as` (single exclamation)
- Just press **Enter** with blank password (in case setup failed)

### 3. **Username Variations**
Sometimes Ubuntu creates slightly different usernames:

**Try these usernames:**
- `astro-dev` (what you entered)
- `astro` (truncated)
- `ubuntu` (default user)

### 4. **Reset Option**
If none work, we can reset using the installation recovery mode.

---

## 💡 Quick Fixes to Try Now

### A. Slow, Careful Re-entry
1. **Username**: Type `astro-dev` slowly
2. **Password**: Type `Country406!!as` one character at a time
3. Watch for any **unexpected characters** on screen

### B. Alternative Characters
Sometimes special characters behave differently:
- Instead of `!!` try typing them as separate exclamation marks
- Ensure **Caps Lock** is off

### C. Check Console Language
- Press **F1** or **F2** to try different console modes
- Some consoles handle special characters differently

---

## 🚨 If Still Not Working

### Reset Method (5 minutes):
1. **Shut down VM**: Close vmconnect window
2. **Stop VM**: `Stop-VM -Name "astro-dev-ubuntu" -Force`
3. **Delete and recreate VM** with simpler password
4. **Use simple password**: Like `astro123` (no special characters)

### Alternative: Single User Recovery
1. **Reboot VM**: Restart it
2. **When GRUB appears**: Press 'e' to edit boot
3. **Add single user mode**: Add `init=/bin/bash` to kernel line
4. **Boot directly to shell**: Bypasses login
5. **Reset password**: `passwd astro-dev`

---

## 🎯 Recommended Quick Fix

**Try this exact sequence:**
1. **Clear any text** in username field
2. **Type slowly**: `astro-dev`
3. **Press Tab** to move to password
4. **Type deliberately**: `C` `o` `u` `n` `t` `r` `y` `4` `0` `6` `!` `!` `a` `s`
5. **Press Enter**

**If that doesn't work, let me know and I'll give you the reset procedure - it's faster than troubleshooting password issues.**

**Which option would you like to try first?**
