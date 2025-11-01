# PowerShell script to run validation audits on all active clients
# Usage: .\run_all_active_clients.ps1

Write-Host "`n[AUTO-DISCOVERY] Running audits for all active clients`n" -ForegroundColor Cyan

# Get all client config files
$clientConfigs = Get-ChildItem -Path "..\ads_sync\configs\clients" -Filter "*.yaml"
Write-Host "[OK] Found $($clientConfigs.Count) clients`n"

# Queue all jobs
$jobs = @()
foreach ($file in $clientConfigs) {
    $slug = $file.BaseName
    Write-Host "Queuing: $slug" -ForegroundColor Yellow
    
    try {
        $body = @{
            slug = $slug
            command = "validate"
        } | ConvertTo-Json
        
        $response = Invoke-WebRequest -Uri "http://localhost:8000/api/runbooks/execute" -Method POST -Body $body -ContentType "application/json" -UseBasicParsing
        $jobData = $response.Content | ConvertFrom-Json
        
        $jobs += @{
            slug = $slug
            job_id = $jobData.job_id
        }
        
        Write-Host "  [OK] Job: $($jobData.job_id)" -ForegroundColor Green
    }
    catch {
        Write-Host "  [ERROR] Failed to queue: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    Write-Host ""
}

# Wait for jobs to process
Write-Host "`n[WAIT] Allowing jobs to process..." -ForegroundColor Cyan
Start-Sleep -Seconds 20

# Check results
Write-Host "`n[RESULTS]" -ForegroundColor Cyan
Write-Host ("=" * 100)

$completed = 0
$failed = 0

foreach ($job in $jobs) {
    try {
        $statusResponse = Invoke-WebRequest -Uri "http://localhost:8000/api/jobs/$($job.job_id)/status" -UseBasicParsing
        $statusData = $statusResponse.Content | ConvertFrom-Json
        
        $status = $statusData.status
        $statusColor = "White"
        
        if ($status -eq "finished") {
            $statusColor = "Green"
            $completed++
        }
        elseif ($status -eq "failed") {
            $statusColor = "Red"
            $failed++
        }
        elseif ($status -eq "in_progress") {
            $statusColor = "Yellow"
        }
        
        Write-Host ("Client: {0,-45} Status: {1}" -f $job.slug, $status) -ForegroundColor $statusColor
        
        if ($status -eq "finished") {
            Write-Host "  [OK] Config valid" -ForegroundColor Green
        }
        elseif ($status -eq "failed" -and $statusData.error) {
            Write-Host "  [ERROR] $($statusData.error)" -ForegroundColor Red
        }
    }
    catch {
        Write-Host ("Client: {0,-45} Status: ERROR" -f $job.slug) -ForegroundColor Red
        Write-Host "  [ERROR] Failed to get status: $($_.Exception.Message)" -ForegroundColor Red
        $failed++
    }
}

Write-Host "`n" + ("=" * 100)
Write-Host "`n[SUMMARY]" -ForegroundColor Cyan
Write-Host ("Total Clients:    {0}" -f $jobs.Count)
Write-Host ("Completed:        {0}" -f $completed) -ForegroundColor Green
Write-Host ("Failed:           {0}" -f $failed) -ForegroundColor Red
Write-Host ("In Progress:      {0}" -f ($jobs.Count - $completed - $failed)) -ForegroundColor Yellow
Write-Host ""

