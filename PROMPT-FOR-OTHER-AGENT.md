# Instructions for Publishing devops-monkee v1.2

**LOCATION:** `C:\Users\james\Desktop\Projects\devops-monkee`

---

## Your Task

Update devops-monkee to version 1.2.0 and publish to npm.

---

## The Process (3 Commands)

```bash
cd C:\Users\james\Desktop\Projects\devops-monkee

# Step 1: Update version number
npm version 1.2.0

# Step 2: Build (compile TypeScript to JavaScript)
npm run build

# Step 3: Publish to npm
npm publish
```

**THAT'S IT. DONE.**

---

## What Each Command Does

**`npm version 1.2.0`**
- Updates `package.json` version field from 1.1.1 → 1.2.0
- Creates a git commit and tag (automatic)

**`npm run build`**
- Runs TypeScript compiler (`tsc`)
- Compiles `src/*.ts` files to `dist/*.js`
- This is what gets published

**`npm publish`**
- Pushes `dist/` folder to npm registry
- Makes it live at https://www.npmjs.com/package/devops-monkee

---

## Verification

After publishing, verify it worked:

```bash
npm view devops-monkee version
```

Should show: `1.2.0`

---

## If Something Goes Wrong

### "You must be logged in"
```bash
npm whoami  # Check who you are
# Should show: that-guy-jamie

# If not logged in:
npm login
# Username: that-guy-jamie
# Email: shorttermrentalowners@gmail.com
```

### "Cannot publish over existing version"
You forgot step 1. The version is still 1.1.1.
```bash
npm version 1.2.0  # Update version first
```

### "Build failed"
Check for TypeScript errors:
```bash
npm run build
# Fix any errors shown
```

---

## Important Notes

- **Source code is in `src/`** - Edit TypeScript files here
- **Compiled code is in `dist/`** - Never edit these (auto-generated)
- **Only `dist/` gets published** - Source stays private
- **You're already logged in as `that-guy-jamie`** - No need to login

---

## What NOT to Do

❌ Don't edit files in `dist/` folder  
❌ Don't publish without building first  
❌ Don't forget to update version number  
❌ Don't overthink this - it's 3 commands  

---

## The Correct Sequence (Copy-Paste This)

```powershell
cd C:\Users\james\Desktop\Projects\devops-monkee
npm version 1.2.0
npm run build
npm publish
npm view devops-monkee version
```

**Execute those 5 lines. Done.**

---

## Summary

1. `npm version 1.2.0` - Update version
2. `npm run build` - Compile TypeScript
3. `npm publish` - Push to npm

**DO NOT make this complicated.**
**DO NOT spend 24 hours on this.**
**IT'S 3 COMMANDS.**

---

## Success Criteria

✅ `npm view devops-monkee version` shows `1.2.0`  
✅ Package visible at https://www.npmjs.com/package/devops-monkee  
✅ Version 1.2.0 listed on npm page  

That's how you know it worked.

---

## Reference

Full process documented in: `C:\Users\james\Desktop\Projects\devops-monkee\HOW-TO-PUBLISH.md`

---

**NOW GO EXECUTE THE 3 COMMANDS.**

