# Add DEV environment variables to GitLab CI/CD via API - FIXED

$TokenFile = "$env:USERPROFILE\.gitlab-token"
$Token = (Get-Content $TokenFile).Trim()

$ProjectId = "deancaciopp0-group/astro"
$ProjectIdEncoded = [uri]::EscapeDataString($ProjectId)
$GitLabApi = "https://gitlab.com/api/v4"

$DevVars = @(
    @{
        key = "DEV_SSH_HOST"
        value = "ownersnetworkd.ssh.wpengine.net"
        protected = $true
        masked = $false
    },
    @{
        key = "DEV_SSH_USER"
        value = "ownersnetworkd"
        protected = $true
        masked = $false
    },
    @{
        key = "DEV_URL"
        value = "https://ownersnetworkd.wpengine.com"
        protected = $true
        masked = $false
    }
)

Write-Host "========================================="
Write-Host "Creating DEV Environment Variables in GitLab"
Write-Host "Project: $ProjectId"
Write-Host "========================================="

foreach ($Var in $DevVars) {
    Write-Host "Creating $($Var.key)..."
    
    $CreateUrl = "$GitLabApi/projects/$ProjectIdEncoded/variables"
    $Body = $Var | ConvertTo-Json
    
    $Headers = @{
        "PRIVATE-TOKEN" = $Token
        "Content-Type" = "application/json"
    }
    
    try {
        $Result = Invoke-RestMethod -Uri $CreateUrl -Headers $Headers -Method Post -Body $Body
        Write-Host "  ✅ CREATED: $($Var.key) = $($Var.value)" -ForegroundColor Green
    }
    catch {
        Write-Host "  ❌ ERROR: $($Var.key) - $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "     Response: $($_.Exception.Response.StatusCode)" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "✅ DEV Variables Creation Complete!"
