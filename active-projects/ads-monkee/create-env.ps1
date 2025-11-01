# Ads Monkee - Create .env File
# Run this script to create your .env file with most values pre-filled

$envContent = @"
# Ads Monkee Environment Configuration
# Generated: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

# ============================================================================
# DATABASE (Render PostgreSQL Basic 1GB)
# ============================================================================
# TODO: Replace <PASSWORD> with actual password from Render dashboard
# Dashboard: https://dashboard.render.com/d/dpg-d3oplg9r0fns73dom48g-a
# Click "Connect" → Copy "External Connection String" password
DATABASE_URL=postgresql://ads_monkee_db_basic_user:jR47n6Lwv503M51g9uQFGPjOfADMNXlq@dpg-d3oplg9r0fns73dom48g-a.oregon-postgres.render.com:5432/ads_monkee_db_basic

# ============================================================================
# GOOGLE ADS API (Auto-copied from ads_sync/google-ads.yaml)
# ============================================================================
GOOGLE_ADS_DEVELOPER_TOKEN=woiu8GeCUDtirM0Z8u_yng
GOOGLE_ADS_CLIENT_ID=125282075605-ranbui2iihm3hjpm9tshpksd8iluejsh.apps.googleusercontent.com
GOOGLE_ADS_CLIENT_SECRET=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
GOOGLE_ADS_REFRESH_TOKEN=1//01q5gKeoG1AP_CgYIARAAGAESNwF-L9Ir0gQ-ru6aJMcJQTrHGHoBVk8MP_yKOoIUUJNDguh57izy0nDqnDylXmDTGGfNdSGonsw
GOOGLE_ADS_LOGIN_CUSTOMER_ID=1877202760

# ============================================================================
# APPLICATION SETTINGS
# ============================================================================
JWT_SECRET=ads-monkee-dev-secret-change-in-production-min-32-chars
ENVIRONMENT=development
LOG_LEVEL=DEBUG

# ============================================================================
# OPTIONAL - Fill in later
# ============================================================================
REDIS_URL=
ANTHROPIC_API_KEY=
GHL_API_KEY=
"@

# Create .env file
$envPath = Join-Path $PSScriptRoot ".env"
$envContent | Out-File -FilePath $envPath -Encoding UTF8

Write-Host ""
Write-Host "================================" -ForegroundColor Green
Write-Host " .env File Created Successfully!" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green
Write-Host ""
Write-Host "NEXT STEP:" -ForegroundColor Yellow
Write-Host "1. Go to: https://dashboard.render.com/d/dpg-d3oplg9r0fns73dom48g-a" -ForegroundColor Cyan
Write-Host "2. Click 'Connect' button" -ForegroundColor Cyan
Write-Host "3. Copy the password from the External Connection String" -ForegroundColor Cyan
Write-Host "4. Edit .env and replace <PASSWORD> with the actual password" -ForegroundColor Cyan
Write-Host ""
Write-Host "Or run this command to open .env for editing:" -ForegroundColor Yellow
Write-Host "  notepad .env" -ForegroundColor Cyan
Write-Host ""
Write-Host "File location: $envPath" -ForegroundColor Gray
Write-Host ""

