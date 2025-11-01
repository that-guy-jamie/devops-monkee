# Remove Extraneous Files from Git Tracking

## Problem
The repository currently tracks many files outside the `devops-monkee/` directory:
- SBEP_Core/
- Tools/
- active-projects/
- audit-monkee/
- ads-monkee/
- etc.

These should NOT be in the public devops-monkee repository.

## Solution: Remove from Tracking (Keep Local Files)

Run this command to remove all files except devops-monkee/ from git tracking:

```powershell
cd c:/Users/james/Desktop/Projects

# Remove all tracked files except devops-monkee/ and root-level docs
git ls-files | Where-Object { 
    $_ -notmatch "^devops-monkee/" -and 
    $_ -ne ".gitignore" -and 
    $_ -ne "README.md" -and 
    $_ -ne "CONTRIBUTING.md" -and 
    $_ -ne "REPOSITORY-ORGANIZATION.md" -and 
    $_ -ne "SBEP-MANIFEST.md" 
} | ForEach-Object { git rm --cached $_ }
```

Then commit and push:
```powershell
git commit -m "Remove extraneous files - keep only devops-monkee for public repo"
git push github main
```

## Alternative: Keep Root-Level SBEP Docs?

If you want to keep the root-level SBEP documentation files (README.md, SBEP-MANIFEST.md, etc.) in the public repo, that's fine. They're generic protocol docs.

The files to definitely remove:
- All active-projects/ subdirectories (proprietary client work)
- Tools/ directory
- audit-monkee/
- ads-monkee/
- SBEP_Core/ (if it contains proprietary configs)

## After Cleanup

Once only devops-monkee/ files are tracked, you can:
1. Push to GitHub: `git push github main`
2. Make repository public on GitHub settings page

