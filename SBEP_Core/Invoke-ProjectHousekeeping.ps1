# Invoke-ProjectHousekeeping.ps1
# SBEP v2.0 - Standard Housekeeping Script
# 
# Purpose: Organize completed work, archive finished workorders, and clean up temporary files
# When to run: After completing major tasks, before committing, or when workspace feels cluttered
# Who runs it: AI Agents (automated) or Developers (manual)

[CmdletBinding()]
param(
    [Parameter(Mandatory=$false)]
    [string]$ProjectRoot = "C:\Users\james\Desktop\Projects",
    
    [Parameter(Mandatory=$false)]
    [switch]$DryRun,
    
    [Parameter(Mandatory=$false)]
    [switch]$SkipWorkorders,
    
    [Parameter(Mandatory=$false)]
    [switch]$SkipTempFiles
)

$ErrorActionPreference = "Continue"

Write-Host "=== SBEP v2.0 Project Housekeeping ===" -ForegroundColor Cyan
Write-Host "Project Root: $ProjectRoot" -ForegroundColor Gray
if ($DryRun) {
    Write-Host "DRY RUN MODE - No files will be moved" -ForegroundColor Yellow
}
Write-Host ""

$movedFiles = 0
$archivedFiles = 0
$foldersCreated = 0

# Helper function to move files safely
function Move-FileIfExists {
    param(
        [string]$Source,
        [string]$Destination,
        [string]$Description
    )
    
    if (Test-Path $Source) {
        if ($DryRun) {
            Write-Host "[DRY RUN] Would move: $Description" -ForegroundColor Yellow
        } else {
            try {
                Move-Item -Path $Source -Destination $Destination -Force -ErrorAction Stop
                Write-Host "[MOVED] $Description" -ForegroundColor Green
                $script:movedFiles++
            } catch {
                Write-Host "[ERROR] Failed to move $Description : $_" -ForegroundColor Red
            }
        }
    }
}

# Helper function to create directory if needed
function Ensure-Directory {
    param([string]$Path)
    
    if (!(Test-Path $Path)) {
        if ($DryRun) {
            Write-Host "[DRY RUN] Would create directory: $Path" -ForegroundColor Yellow
        } else {
            New-Item -ItemType Directory -Path $Path -Force | Out-Null
            Write-Host "[CREATED] Directory: $Path" -ForegroundColor Green
            $script:foldersCreated++
        }
    }
}

#region Phase 1: Archive Completed Workorders
if (!$SkipWorkorders) {
    Write-Host "`n--- Phase 1: Archive Completed Workorders ---" -ForegroundColor Cyan
    
    # Global Workorders
    $workordersPath = Join-Path $ProjectRoot "Workorders"
    $workordersArchive = Join-Path $workordersPath "Archive"
    
    if (Test-Path $workordersPath) {
        Ensure-Directory $workordersArchive
        
        # Archive completed workorders (look for COMPLETE in filename or content)
        Get-ChildItem -Path $workordersPath -File -Filter "*.md" | ForEach-Object {
            if ($_.Name -like "*COMPLETE*" -or $_.Name -like "*SUMMARY*") {
                $content = Get-Content $_.FullName -Raw -ErrorAction SilentlyContinue
                if ($content -match "Status.*Complete|✅.*Complete|COMPLETE") {
                    Move-FileIfExists $_.FullName $workordersArchive "Workorder: $($_.Name)"
                    $script:archivedFiles++
                }
            }
        }
        
        # Archive CSV files related to completed work
        Get-ChildItem -Path $workordersPath -File -Filter "*.csv" | ForEach-Object {
            Move-FileIfExists $_.FullName $workordersArchive "Data file: $($_.Name)"
            $script:archivedFiles++
        }
    }
    
    # Project-specific workorder archives
    $projects = @("ads_sync", "ads_sync_dashboard", "ads-monkee", "astro", "google-ads-manager")
    foreach ($project in $projects) {
        $projectPath = Join-Path $ProjectRoot $project
        if (Test-Path $projectPath) {
            $projectArchive = Join-Path $projectPath "archive"
            
            # Look for completion documents
            Get-ChildItem -Path $projectPath -File -Filter "*COMPLETE*.md" -ErrorAction SilentlyContinue | ForEach-Object {
                Ensure-Directory $projectArchive
                Move-FileIfExists $_.FullName $projectArchive "Project completion: $project\$($_.Name)"
                $script:archivedFiles++
            }
            
            Get-ChildItem -Path $projectPath -File -Filter "*SUMMARY*.md" -ErrorAction SilentlyContinue | ForEach-Object {
                $content = Get-Content $_.FullName -Raw -ErrorAction SilentlyContinue
                if ($content -match "Status.*Complete|✅.*Complete") {
                    Ensure-Directory $projectArchive
                    Move-FileIfExists $_.FullName $projectArchive "Project summary: $project\$($_.Name)"
                    $script:archivedFiles++
                }
            }
        }
    }
}
#endregion

#region Phase 2: Organize Temporary Files
if (!$SkipTempFiles) {
    Write-Host "`n--- Phase 2: Organize Temporary Files ---" -ForegroundColor Cyan
    
    $tempDir = Join-Path $ProjectRoot ".tmp"
    Ensure-Directory $tempDir
    
    # Common temporary file patterns
    $tempPatterns = @(
        "dir.txt", "test.txt", "output.txt", "temp.txt",
        "*-dir.txt", "*-output.txt", "*-temp.txt",
        "*.tmp", "*.log" # Be careful with logs - some are important
    )
    
    foreach ($pattern in $tempPatterns) {
        Get-ChildItem -Path $ProjectRoot -File -Filter $pattern -ErrorAction SilentlyContinue | ForEach-Object {
            # Skip important log files
            if ($_.Name -notlike "*session*" -and $_.Name -notlike "*error*" -and $_.Name -notlike "*deploy*") {
                Move-FileIfExists $_.FullName $tempDir "Temp file: $($_.Name)"
            }
        }
    }
    
    # HTML output files (usually test outputs)
    Get-ChildItem -Path $ProjectRoot -File -Filter "*-output.html" -ErrorAction SilentlyContinue | ForEach-Object {
        Move-FileIfExists $_.FullName $tempDir "HTML output: $($_.Name)"
    }
    
    # Command/script scratch files
    Get-ChildItem -Path $ProjectRoot -File -Filter "*-commands.txt" -ErrorAction SilentlyContinue | ForEach-Object {
        Move-FileIfExists $_.FullName $tempDir "Command file: $($_.Name)"
    }
}
#endregion

#region Phase 3: Organize Archive Structure
Write-Host "`n--- Phase 3: Organize Archive Structure ---" -ForegroundColor Cyan

$archivePath = Join-Path $ProjectRoot "Archive"
if (Test-Path $archivePath) {
    # Ensure subdirectories exist
    $archiveSubdirs = @("workorders", "projects", "housekeeping", "scripts")
    foreach ($subdir in $archiveSubdirs) {
        Ensure-Directory (Join-Path $archivePath $subdir)
    }
    
    # Organize housekeeping zips
    Get-ChildItem -Path $archivePath -File -Filter "*housekeeping*.zip" -ErrorAction SilentlyContinue | ForEach-Object {
        Move-FileIfExists $_.FullName (Join-Path $archivePath "housekeeping") "Housekeeping archive: $($_.Name)"
    }
    
    # Organize other zips to projects
    Get-ChildItem -Path $archivePath -File -Filter "*.zip" -ErrorAction SilentlyContinue | ForEach-Object {
        if ($_.Name -notlike "*housekeeping*") {
            Move-FileIfExists $_.FullName (Join-Path $archivePath "projects") "Project archive: $($_.Name)"
        }
    }
}
#endregion

#region Summary
Write-Host "`n=== Housekeeping Summary ===" -ForegroundColor Cyan
Write-Host "Files moved: $movedFiles" -ForegroundColor Green
Write-Host "Files archived: $archivedFiles" -ForegroundColor Green
Write-Host "Folders created: $foldersCreated" -ForegroundColor Green

if ($DryRun) {
    Write-Host "`nThis was a DRY RUN. No files were actually moved." -ForegroundColor Yellow
    Write-Host "Run without -DryRun to perform actual housekeeping." -ForegroundColor Yellow
}

Write-Host "`nHousekeeping complete!" -ForegroundColor Cyan
#endregion

