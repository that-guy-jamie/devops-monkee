# Get detailed results for all completed validation jobs
# Usage: .\get_all_results.ps1

Write-Host "`n[FETCHING RESULTS] Retrieving validation results for all clients`n" -ForegroundColor Cyan

# Get all client config files
$clientConfigs = Get-ChildItem -Path "..\ads_sync\configs\clients" -Filter "*.yaml" | Sort-Object Name

$results = @()
$completed = 0
$failed = 0
$pending = 0

Write-Host "Processing $($clientConfigs.Count) clients..." -ForegroundColor Yellow
Write-Host ("=" * 120) -ForegroundColor Gray

foreach ($file in $clientConfigs) {
    $slug = $file.BaseName
    
    # Queue a fresh validation job for this client
    try {
        $body = @{
            slug = $slug
            command = "validate"
        } | ConvertTo-Json
        
        $response = Invoke-WebRequest -Uri "http://localhost:8000/api/runbooks/execute" -Method POST -Body $body -ContentType "application/json" -UseBasicParsing -ErrorAction Stop
        $jobData = $response.Content | ConvertFrom-Json
        $jobId = $jobData.job_id
        
        # Wait a moment for job to complete
        Start-Sleep -Milliseconds 500
        
        # Get the result
        $resultResponse = Invoke-WebRequest -Uri "http://localhost:8000/api/jobs/$jobId/result" -UseBasicParsing -ErrorAction Stop
        $result = $resultResponse.Content | ConvertFrom-Json
        
        if ($result.exit_code -eq 0) {
            $completed++
            $statusIcon = "[OK]"
            $statusColor = "Green"
        }
        else {
            $failed++
            $statusIcon = "[FAIL]"
            $statusColor = "Red"
        }
        
        Write-Host ("{0,-50} {1}" -f $slug, $statusIcon) -ForegroundColor $statusColor
        
        # Parse the output for key information
        if ($result.stdout -match "Config file valid") {
            Write-Host "  - Config: Valid" -ForegroundColor Green
        }
        if ($result.stdout -match "State file loaded \(watermark: (.+?)\)") {
            $watermark = $matches[1]
            Write-Host "  - State: Initialized (watermark: $watermark)" -ForegroundColor Cyan
        }
        if ($result.stdout -match "MISSING.*Master CSV") {
            Write-Host "  - Data: No master CSV yet (needs init)" -ForegroundColor Yellow
        }
        
        $results += @{
            slug = $slug
            status = "completed"
            exit_code = $result.exit_code
            output = $result.stdout
        }
    }
    catch {
        $pending++
        Write-Host ("{0,-50} [PENDING]" -f $slug) -ForegroundColor Yellow
        Write-Host "  - $($_.Exception.Message)" -ForegroundColor Gray
        
        $results += @{
            slug = $slug
            status = "pending"
            error = $_.Exception.Message
        }
    }
    
    Write-Host ""
}

Write-Host ("=" * 120) -ForegroundColor Gray
Write-Host "`n[SUMMARY]" -ForegroundColor Cyan
Write-Host ("Total Clients:     {0}" -f $clientConfigs.Count)
Write-Host ("Validated:         {0}" -f $completed) -ForegroundColor Green
Write-Host ("Failed:            {0}" -f $failed) -ForegroundColor Red
Write-Host ("Pending:           {0}" -f $pending) -ForegroundColor Yellow

Write-Host "`n[NEXT STEPS]" -ForegroundColor Cyan
Write-Host "1. Run 'init' command for clients to pull historical data"
Write-Host "2. Set up daily 'append' jobs for incremental updates"
Write-Host "3. Generate reports once data is populated"
Write-Host ""

# Export results to JSON
$resultsJson = $results | ConvertTo-Json -Depth 10
$resultsJson | Out-File -FilePath ".\validation_results.json" -Encoding UTF8
Write-Host "[EXPORT] Results saved to validation_results.json" -ForegroundColor Green
Write-Host ""

