# Fix database password in .env
$envFile = ".env"
$content = Get-Content $envFile -Raw

# Update password
$content = $content -replace '5Vb4oTUe7R8jWmfFCNEDDZuLgWNxfKGr', 'jR47n6Lwv503M51g9uQFGPjOfADMNXlq'

# Write back
$content | Set-Content $envFile -NoNewline

Write-Host "Database password updated successfully!" -ForegroundColor Green

