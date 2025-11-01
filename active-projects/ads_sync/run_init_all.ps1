# PowerShell script to run init for all clients
# Usage: .\run_init_all.ps1

$poetryPath = "C:\Users\james\AppData\Roaming\Python\Python313\Scripts\poetry.exe"

# Get all client configs except heather-murphy-group (already done)
$clients = Get-ChildItem -Path "configs\clients" -Filter "*.yaml" | 
    Where-Object { $_.BaseName -ne "heather-murphy-group" } |
    Sort-Object Name

$total = $clients.Count
$successful = 0
$failed = 0
$startTime = Get-Date

Write-Host "`n======================================================================" -ForegroundColor Cyan
Write-Host "  INITIALIZING DATA PULL FOR $total CLIENTS" -ForegroundColor Cyan
Write-Host "======================================================================`n" -ForegroundColor Cyan
Write-Host "Pulling 1 year of historical campaign data..." -ForegroundColor Yellow
Write-Host "Start Time: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')`n"

$results = @()

for ($i = 0; $i -lt $clients.Count; $i++) {
    $client = $clients[$i]
    $slug = $client.BaseName
    $num = $i + 1
    
    Write-Host "`n======================================================================" -ForegroundColor Gray
    Write-Host "[$num/$total] $slug" -ForegroundColor White
    Write-Host "======================================================================" -ForegroundColor Gray
    
    $clientStart = Get-Date
    
    try {
        # Run init command
        & $poetryPath run python ads_sync_cli.py init $slug 2>&1 | Tee-Object -Variable output
        
        if ($LASTEXITCODE -eq 0) {
            $elapsed = ((Get-Date) - $clientStart).TotalSeconds
            
            # Try to extract row count
            $rowCount = 0
            foreach ($line in $output) {
                if ($line -match "After deduplication: (\d+) rows") {
                    $rowCount = [int]$matches[1]
                    break
                }
            }
            
            Write-Host "[SUCCESS] $slug - $rowCount rows in $($elapsed.ToString('F1'))s" -ForegroundColor Green
            $successful++
            
            $results += [PSCustomObject]@{
                Client = $slug
                Status = "Success"
                Rows = $rowCount
                Time = $elapsed
            }
        }
        else {
            $elapsed = ((Get-Date) - $clientStart).TotalSeconds
            Write-Host "[FAILED] $slug - Exit code: $LASTEXITCODE" -ForegroundColor Red
            $failed++
            
            $results += [PSCustomObject]@{
                Client = $slug
                Status = "Failed"
                Rows = 0
                Time = $elapsed
            }
        }
    }
    catch {
        $elapsed = ((Get-Date) - $clientStart).TotalSeconds
        Write-Host "[ERROR] $slug - $($_.Exception.Message)" -ForegroundColor Red
        $failed++
        
        $results += [PSCustomObject]@{
            Client = $slug
            Status = "Error"
            Rows = 0
            Time = $elapsed
        }
    }
}

$totalElapsed = ((Get-Date) - $startTime).TotalMinutes

Write-Host "`n======================================================================" -ForegroundColor Cyan
Write-Host "  EXECUTION SUMMARY" -ForegroundColor Cyan
Write-Host "======================================================================`n" -ForegroundColor Cyan

Write-Host "Total Clients:     $total"
Write-Host "Successful:        $successful" -ForegroundColor Green
Write-Host "Failed:            $failed" -ForegroundColor $(if ($failed -gt 0) { "Red" } else { "Gray" })
Write-Host "`nTotal Rows:        $(($results | Where-Object {$_.Status -eq 'Success'} | Measure-Object -Property Rows -Sum).Sum)"
Write-Host "Avg Time/Client:   $(($results | Where-Object {$_.Status -eq 'Success'} | Measure-Object -Property Time -Average).Average.ToString('F1'))s"
Write-Host "Total Time:        $($totalElapsed.ToString('F1')) minutes"
Write-Host "`nEnd Time: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"

Write-Host "`n======================================================================`n" -ForegroundColor Cyan

# Export results
$results | Export-Csv -Path "init_results.csv" -NoTypeInformation
Write-Host "[EXPORT] Results saved to init_results.csv`n" -ForegroundColor Green

