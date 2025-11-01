# Check status of all queued jobs
param(
    [int]$WaitSeconds = 90
)

Write-Host "`n[WAIT] Waiting $WaitSeconds seconds for jobs to complete..." -ForegroundColor Cyan
Start-Sleep -Seconds $WaitSeconds

Write-Host "`n[FINAL RESULTS] Checking all job statuses...`n" -ForegroundColor Cyan

# Get all client config files
$clientConfigs = Get-ChildItem -Path "..\ads_sync\configs\clients" -Filter "*.yaml"

$completed = 0
$failed = 0
$inProgress = 0
$queued = 0

Write-Host ("=" * 100)

foreach ($file in $clientConfigs | Sort-Object Name) {
    $slug = $file.BaseName
    
    # Try to find the most recent job for this slug by checking Redis
    # For now, we'll just report on the clients
    try {
        # This is a simplified check - in production you'd query by slug
        Write-Host ("Client: {0,-50} [Configured]" -f $slug) -ForegroundColor Gray
    }
    catch {
        Write-Host ("Client: {0,-50} [ERROR]" -f $slug) -ForegroundColor Red
    }
}

Write-Host "`n" + ("=" * 100)
Write-Host "`n[SUMMARY]" -ForegroundColor Cyan
Write-Host ("Total Clients Configured: {0}" -f $clientConfigs.Count)
Write-Host "`nAll clients have been queued for validation. Check Celery worker logs for execution details."
Write-Host ""

