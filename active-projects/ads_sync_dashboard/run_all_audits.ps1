# Run validation audits for all configured clients
# This script uses the ads_sync_dashboard API to queue jobs for all clients

$apiUrl = "http://localhost:8000"

Write-Host "`n🚀 RUNNING AUDITS FOR ALL CLIENTS" -ForegroundColor Cyan -BackgroundColor Black
Write-Host "=" * 60 -ForegroundColor Cyan

# Get list of all clients from the dashboard
Write-Host "`n📋 Discovering clients..." -ForegroundColor Yellow
$clientsPath = "..\ads_sync\configs\clients"
$clientFiles = Get-ChildItem -Path $clientsPath -Filter "*.yaml"

if ($clientFiles.Count -eq 0) {
    Write-Host "❌ No client configuration files found in $clientsPath" -ForegroundColor Red
    exit 1
}

Write-Host "✓ Found $($clientFiles.Count) client(s)" -ForegroundColor Green

# Array to store job IDs
$jobs = @()

# Queue validation job for each client
foreach ($file in $clientFiles) {
    $slug = $file.BaseName
    Write-Host "`n📤 Queuing audit for: $slug" -ForegroundColor Cyan
    
    $body = @{
        slug = $slug
        command = "validate"
    } | ConvertTo-Json
    
    try {
        $response = Invoke-WebRequest -Uri "$apiUrl/api/runbooks/execute" `
            -Method POST `
            -Body $body `
            -ContentType 'application/json' `
            -UseBasicParsing
        
        $jobData = $response.Content | ConvertFrom-Json
        $jobs += @{
            slug = $slug
            job_id = $jobData.job_id
            status = "queued"
        }
        
        Write-Host "  ✓ Job queued: $($jobData.job_id)" -ForegroundColor Green
    }
    catch {
        Write-Host "  ❌ Failed to queue job: $_" -ForegroundColor Red
    }
}

# Wait for all jobs to complete
Write-Host "`n⏳ Waiting for jobs to complete..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

# Check status of all jobs
Write-Host "`n📊 JOB RESULTS:" -ForegroundColor Cyan -BackgroundColor Black
Write-Host "=" * 60 -ForegroundColor Cyan

$completedCount = 0
$failedCount = 0

foreach ($job in $jobs) {
    try {
        $statusResponse = Invoke-WebRequest -Uri "$apiUrl/api/jobs/$($job.job_id)/status" `
            -UseBasicParsing
        $statusData = $statusResponse.Content | ConvertFrom-Json
        
        Write-Host "`n📌 Client: $($job.slug)" -ForegroundColor White
        Write-Host "   Job ID: $($job.job_id)"
        $statusColor = "Yellow"
        if ($statusData.status -eq "finished") { $statusColor = "Green" }
        elseif ($statusData.status -eq "failed") { $statusColor = "Red" }
        Write-Host "   Status: $($statusData.status)" -ForegroundColor $statusColor
        
        if ($statusData.status -eq "finished") {
            $completedCount++
            Write-Host "   ✓ Audit complete" -ForegroundColor Green
            
            # Show summary from output
            if ($statusData.result -match "\[OK\].*Config file valid") {
                Write-Host "   ✓ Config valid" -ForegroundColor Green
            }
            if ($statusData.result -match "\[MISSING\].*Master CSV") {
                Write-Host "   ⚠ No existing data (ready for init)" -ForegroundColor Yellow
            }
        }
        elseif ($statusData.status -eq "failed") {
            $failedCount++
            Write-Host "   ❌ Error: $($statusData.error)" -ForegroundColor Red
        }
        else {
            Write-Host "   ⏳ Still running..." -ForegroundColor Yellow
        }
    }
    catch {
        Write-Host "   ❌ Failed to get status: $_" -ForegroundColor Red
        $failedCount++
    }
}

# Summary
Write-Host "`n" + ("=" * 60) -ForegroundColor Cyan
Write-Host "📈 SUMMARY" -ForegroundColor Cyan -BackgroundColor Black
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "Total Clients:    $($jobs.Count)"
Write-Host "Completed:        $completedCount" -ForegroundColor Green
$failedColor = if ($failedCount -gt 0) { "Red" } else { "Green" }
Write-Host "Failed:           $failedCount" -ForegroundColor $failedColor
Write-Host "=" * 60 -ForegroundColor Cyan

if ($completedCount -eq $jobs.Count) {
    Write-Host "`n🎉 ALL AUDITS COMPLETED SUCCESSFULLY!" -ForegroundColor Green -BackgroundColor Black
} else {
    Write-Host "`n⚠ Some audits did not complete. Review errors above." -ForegroundColor Yellow
}

Write-Host ""

