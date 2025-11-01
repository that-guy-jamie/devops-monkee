# Update .env file with actual credentials
$envFile = ".env"

# Read the template
$content = Get-Content $envFile -Raw

# Update DATABASE_URL (from existing connection)
$content = $content -replace 'DATABASE_URL=postgresql://user:password@localhost:5432/ads_monkee', 'DATABASE_URL=postgresql://ads_monkee_db_basic_user:5Vb4oTUe7R8jWmfFCNEDDZuLgWNxfKGr@dpg-d3oplg9r0fns73dom48g-a.oregon-postgres.render.com:5432/ads_monkee_db_basic?sslmode=require'

# Update REDIS_URL (from infrastructure doc)
$content = $content -replace 'REDIS_URL=redis://localhost:6379', 'REDIS_URL=redis://red-d3oougmmcj7s739fh2og:6379'
$content = $content -replace 'CELERY_BROKER_URL=redis://localhost:6379/0', 'CELERY_BROKER_URL=redis://red-d3oougmmcj7s739fh2og:6379/0'
$content = $content -replace 'CELERY_RESULT_BACKEND=redis://localhost:6379/0', 'CELERY_RESULT_BACKEND=redis://red-d3oougmmcj7s739fh2og:6379/0'

# Update Google Ads credentials
$content = $content -replace 'GOOGLE_ADS_DEVELOPER_TOKEN=your_developer_token_here', 'GOOGLE_ADS_DEVELOPER_TOKEN=woiu8GeCUDtirM0Z8u_yng'
$content = $content -replace 'GOOGLE_ADS_CLIENT_ID=your_client_id.apps.googleusercontent.com', 'GOOGLE_ADS_CLIENT_ID=125282075605-ranbui2iihm3hjpm9tshpksd8iluejsh.apps.googleusercontent.com'
$content = $content -replace 'GOOGLE_ADS_CLIENT_SECRET=your_client_secret', 'GOOGLE_ADS_CLIENT_SECRET=***REDACTED_SECRET***'
$content = $content -replace 'GOOGLE_ADS_REFRESH_TOKEN=your_refresh_token', 'GOOGLE_ADS_REFRESH_TOKEN=1//01q5gKeoG1AP_CgYIARAAGAESNwF-L9Ir0gQ-ru6aJMcJQTrHGHoBVk8MP_yKOoIUUJNDguh57izy0nDqnDylXmDTGGfNdSGonsw'
$content = $content -replace 'GOOGLE_ADS_LOGIN_CUSTOMER_ID=123-456-7890', 'GOOGLE_ADS_LOGIN_CUSTOMER_ID=1877202760'

# Update LLM configuration
$content = $content -replace 'OPENAI_API_KEY=sk-your-openai-key-here', 'OPENAI_API_KEY=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'

# Update JWT secret (generate random)
$jwtSecret = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 32 | ForEach-Object {[char]$_})
$content = $content -replace 'JWT_SECRET=your-random-secret-key-min-32-chars', "JWT_SECRET=$jwtSecret"

# Write back to file
$content | Set-Content $envFile -NoNewline

Write-Host ".env file updated successfully!" -ForegroundColor Green
Write-Host "DATABASE_URL: Render PostgreSQL (Oregon)" -ForegroundColor Cyan
Write-Host "REDIS_URL: Render Redis (Oregon)" -ForegroundColor Cyan
Write-Host "GOOGLE_ADS_API: Configured" -ForegroundColor Cyan
Write-Host "OPENAI_API_KEY: Configured" -ForegroundColor Cyan
Write-Host "JWT_SECRET: Generated" -ForegroundColor Cyan

