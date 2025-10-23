#!/usr/bin/env pwsh
<#
.SYNOPSIS
    SBEP v2.0 Project Initialization Script

.DESCRIPTION
    Initializes a project with Source-Bound Execution Protocol (SBEP) v2.0 compliance.
    Creates /sds/ directory, copies templates, generates documentation index, and performs
    housekeeping by archiving obsolete files.

.PARAMETER ProjectPath
    Full path to the project directory to initialize

.PARAMETER Rollback
    Rollback a previous SBEP initialization

.PARAMETER Timestamp
    Timestamp of the initialization to rollback (format: yyyyMMdd-HHmmss)

.PARAMETER SkipHousekeeping
    Skip the housekeeping/archival step

.EXAMPLE
    .\SBEP-INIT.ps1 -ProjectPath C:\Users\james\Desktop\Projects\astro

.EXAMPLE
    .\SBEP-INIT.ps1 -ProjectPath C:\Users\james\Desktop\Projects\astro -Rollback -Timestamp 20251015-143022

.NOTES
    Version: 2.0
    Author: SBEP Implementation Team
    Created: 2025-10-15
#>

param(
    [Parameter(Mandatory=$true, Position=0)]
    [string]$ProjectPath,
    
    [Parameter(Mandatory=$false)]
    [switch]$Rollback,
    
    [Parameter(Mandatory=$false)]
    [string]$Timestamp,
    
    [Parameter(Mandatory=$false)]
    [switch]$SkipHousekeeping
)

# Color output functions
function Write-Success { param([string]$Message) Write-Host "[OK] $Message" -ForegroundColor Green }
function Write-Info { param([string]$Message) Write-Host "[INFO] $Message" -ForegroundColor Cyan }
function Write-Warning { param([string]$Message) Write-Host "[WARN] $Message" -ForegroundColor Yellow }
function Write-Error-Custom { param([string]$Message) Write-Host "[ERROR] $Message" -ForegroundColor Red }
function Write-Header { param([string]$Message) Write-Host "`n$('=' * 60)" -ForegroundColor Cyan; Write-Host "  $Message" -ForegroundColor Cyan; Write-Host "$('=' * 60)`n" -ForegroundColor Cyan }

# Resolve paths
$ProjectPath = Resolve-Path $ProjectPath -ErrorAction Stop
$ProjectName = Split-Path $ProjectPath -Leaf
$SBEPCorePath = Split-Path $PSScriptRoot -Parent | Join-Path -ChildPath "SBEP_Core"
$ArchivePath = Split-Path $ProjectPath -Parent | Join-Path -ChildPath "archive"
$CurrentDate = Get-Date -Format "MMddyyyy"
$CurrentTimestamp = Get-Date -Format "yyyyMMdd-HHmmss"

Write-Header "SBEP v2.0 Project Initialization"
Write-Info "Project: $ProjectName"
Write-Info "Path: $ProjectPath"
Write-Info "Timestamp: $CurrentTimestamp"

# Handle Rollback
if ($Rollback) {
    if (-not $Timestamp) {
        Write-Error-Custom "Rollback requires -Timestamp parameter"
        exit 1
    }
    
    $rollbackFile = Join-Path $ProjectPath ".sbep-rollback-$Timestamp.json"
    
    if (-not (Test-Path $rollbackFile)) {
        Write-Error-Custom "Rollback file not found: $rollbackFile"
        exit 1
    }
    
    Write-Info "Rolling back SBEP initialization from $Timestamp..."
    
    $rollbackData = Get-Content $rollbackFile | ConvertFrom-Json
    
    # Remove created directories
    foreach ($dir in $rollbackData.created_directories) {
        if (Test-Path $dir) {
            Remove-Item $dir -Recurse -Force
            Write-Success "Removed: $dir"
        }
    }
    
    # Remove created files
    foreach ($file in $rollbackData.created_files) {
        if (Test-Path $file) {
            Remove-Item $file -Force
            Write-Success "Removed: $file"
        }
    }
    
    Write-Success "Rollback complete"
    exit 0
}

# Verify SBEP_Core exists
if (-not (Test-Path $SBEPCorePath)) {
    Write-Error-Custom "SBEP_Core directory not found at: $SBEPCorePath"
    Write-Info "Please run this script from C:\Users\james\Desktop\Projects\SBEP_Core\"
    exit 1
}

# Initialize rollback tracking
$rollbackData = @{
    timestamp = $CurrentTimestamp
    project = $ProjectName
    project_path = $ProjectPath
    created_directories = @()
    created_files = @()
    archived_files = @()
}

# Phase 1: Create /sds/ Directory
Write-Header "Phase 1: Creating Source Documentation Store (/sds/)"

$sdsPath = Join-Path $ProjectPath "sds"

if (Test-Path $sdsPath) {
    Write-Warning "/sds/ already exists. Skipping creation."
} else {
    New-Item -ItemType Directory -Path $sdsPath -Force | Out-Null
    $rollbackData.created_directories += $sdsPath
    Write-Success "Created: $sdsPath"
}

# Phase 2: Copy Templates
Write-Header "Phase 2: Installing SBEP Templates"

# Copy SBEP-MANDATE
$mandateSource = Join-Path $SBEPCorePath "SBEP-MANDATE-TEMPLATE.md"
$mandateDest = Join-Path $sdsPath "SBEP-MANDATE.md"

if (Test-Path $mandateDest) {
    Write-Warning "SBEP-MANDATE.md already exists. Skipping."
} else {
    Copy-Item $mandateSource $mandateDest -Force
    $rollbackData.created_files += $mandateDest
    Write-Success "Installed: SBEP-MANDATE.md"
    
    # Customize template placeholders (basic replacement)
    $mandateContent = Get-Content $mandateDest -Raw
    $mandateContent = $mandateContent -replace '\{PROJECT_NAME\}', $ProjectName
    $mandateContent = $mandateContent -replace '\{ISO_DATE\}', (Get-Date -Format "yyyy-MM-dd")
    Set-Content $mandateDest $mandateContent -NoNewline
    Write-Success "Customized SBEP-MANDATE.md"
}

# Phase 3: Generate Documentation Index
Write-Header "Phase 3: Generating Documentation Index"

$indexDest = Join-Path $sdsPath "SBEP-INDEX.yaml"

Write-Info "Scanning project for documentation..."

# Scan for markdown files
$markdownFiles = Get-ChildItem -Path $ProjectPath -Filter *.md -Recurse -File | 
    Where-Object { 
        $_.FullName -notlike "*node_modules*" -and 
        $_.FullName -notlike "*archive*" -and
        $_.FullName -notlike "*vendor*"
    }

Write-Info "Found $($markdownFiles.Count) markdown files"

# Build documentation categories
$coreFiles = $markdownFiles | Where-Object { $_.Name -match '^(README|CHANGELOG)\.md$' }
$docsFiles = $markdownFiles | Where-Object { $_.DirectoryName -like "*\docs*" }
$opsFiles = $markdownFiles | Where-Object { $_.DirectoryName -like "*\ops*" }
$workorderFiles = $markdownFiles | Where-Object { $_.DirectoryName -like "*\workorders*" }

# Load template
$indexTemplate = Get-Content (Join-Path $SBEPCorePath "SBEP-INDEX-TEMPLATE.yaml") -Raw

# Customize index
$indexContent = $indexTemplate -replace '\{PROJECT_NAME\}', $ProjectName
$indexContent = $indexContent -replace '\{ISO_DATE\}', (Get-Date -Format "yyyy-MM-dd")

# Write index
Set-Content $indexDest $indexContent -NoNewline
$rollbackData.created_files += $indexDest
Write-Success "Generated: SBEP-INDEX.yaml"
Write-Info "Index contains template structure. Manual curation recommended."

# Phase 4: Housekeeping (Archive Obsolete Files)
if (-not $SkipHousekeeping) {
    Write-Header "Phase 4: Housekeeping and Archival"
    
    Write-Info "Identifying obsolete files..."
    
    # Common patterns for obsolete files (customize per project)
    $obsoletePatterns = @(
        "*cheatsheet*.md",
        "*deprecated*.md",
        "*old*.md",
        "*backup*.md",
        "*.old",
        "*.bak",
        "*.tmp",
        "*-old.*"
    )
    
    $obsoleteFiles = @()
    foreach ($pattern in $obsoletePatterns) {
        $found = Get-ChildItem -Path $ProjectPath -Filter $pattern -Recurse -File -ErrorAction SilentlyContinue |
            Where-Object { 
                $_.FullName -notlike "*node_modules*" -and 
                $_.FullName -notlike "*archive*" -and
                $_.FullName -notlike "*vendor*" -and
                $_.FullName -notlike "*.git*"
            }
        $obsoleteFiles += $found
    }
    
    if ($obsoleteFiles.Count -eq 0) {
        Write-Info "No obsolete files identified. Skipping archival."
    } else {
        Write-Info "Found $($obsoleteFiles.Count) obsolete files to archive"
        
        # Create archive directory if needed
        if (-not (Test-Path $ArchivePath)) {
            New-Item -ItemType Directory -Path $ArchivePath -Force | Out-Null
            Write-Success "Created global archive: $ArchivePath"
        }
        
        # Create temporary staging directory
        $stagingPath = Join-Path $env:TEMP "sbep-housekeeping-$CurrentTimestamp"
        New-Item -ItemType Directory -Path $stagingPath -Force | Out-Null
        
        # Create manifest
        $manifest = @{
            project = $ProjectName
            archive_date = (Get-Date -Format "yyyy-MM-dd HH:mm:ss")
            archived_by = "SBEP-INIT.ps1"
            reason = "SBEP v2.0 housekeeping"
            files = @()
        }
        
        # Copy files to staging with relative paths
        foreach ($file in $obsoleteFiles) {
            $relativePath = $file.FullName.Substring($ProjectPath.Length + 1)
            $targetPath = Join-Path $stagingPath $relativePath
            $targetDir = Split-Path $targetPath -Parent
            
            if (-not (Test-Path $targetDir)) {
                New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
            }
            
            Copy-Item $file.FullName $targetPath -Force
            
            $manifest.files += @{
                original_path = $relativePath
                size_bytes = $file.Length
                last_modified = $file.LastWriteTime.ToString("yyyy-MM-dd HH:mm:ss")
            }
            
            # Delete original
            Remove-Item $file.FullName -Force
            $rollbackData.archived_files += $file.FullName
            
            Write-Info "Archived: $relativePath"
        }
        
        # Write manifest
        $manifest | ConvertTo-Json -Depth 10 | Set-Content (Join-Path $stagingPath "MANIFEST.json")
        
        # Compress to zip
        $archiveZip = Join-Path $ArchivePath "$ProjectName-housekeeping-$CurrentDate.zip"
        
        # Remove existing archive if present
        if (Test-Path $archiveZip) {
            Remove-Item $archiveZip -Force
            Write-Warning "Replaced existing archive: $archiveZip"
        }
        
        Compress-Archive -Path "$stagingPath\*" -DestinationPath $archiveZip -Force
        Write-Success "Created archive: $archiveZip"
        Write-Success "Archived $($obsoleteFiles.Count) files"
        
        # Cleanup staging
        Remove-Item $stagingPath -Recurse -Force
    }
} else {
    Write-Info "Housekeeping skipped (SkipHousekeeping flag)"
}

# Phase 5: Create Rollback Snapshot
Write-Header "Phase 5: Creating Rollback Snapshot"

$rollbackFile = Join-Path $ProjectPath ".sbep-rollback-$CurrentTimestamp.json"
$rollbackData | ConvertTo-Json -Depth 10 | Set-Content $rollbackFile
Write-Success "Rollback snapshot: .sbep-rollback-$CurrentTimestamp.json"

# Phase 6: Verification Report
Write-Header "Initialization Complete"

Write-Success "Project $ProjectName is now SBEP v2.0 compliant"
Write-Info ""
Write-Info "Created:"
Write-Info "  - $sdsPath/"
Write-Info "  - $sdsPath/SBEP-MANDATE.md"
Write-Info "  - $sdsPath/SBEP-INDEX.yaml"

if (-not $SkipHousekeeping -and $obsoleteFiles -and $obsoleteFiles.Count -gt 0) {
    Write-Info ""
    Write-Info "Archived:"
    Write-Info "  - $($obsoleteFiles.Count) obsolete files"
    Write-Info "  - Archive: /archive/$ProjectName-housekeeping-$CurrentDate.zip"
}

Write-Info ""
Write-Info "Next Steps:"
Write-Info "  1. Review and customize sds/SBEP-MANDATE.md"
Write-Info "  2. Curate sds/SBEP-INDEX.yaml (mark exists: true for found docs)"
Write-Info "  3. Add project-specific documentation references"
Write-Info "  4. Test agent compliance with new structure"
Write-Info ""
Write-Info "To rollback:"
Write-Info "  .\SBEP-INIT.ps1 -ProjectPath '$ProjectPath' -Rollback -Timestamp $CurrentTimestamp"
Write-Info ""

Write-Success "SBEP v2.0 initialization successful!"

