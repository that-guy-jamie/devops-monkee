# PowerShell script to replace secret in git history
$secret = "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"
$replacement = "***REDACTED_SECRET***"

Get-ChildItem -Recurse -File -ErrorAction SilentlyContinue | 
    Where-Object { $_.Extension -in @(".py", ".ps1", ".md", ".txt", ".yaml", ".yml", ".json", ".env") } |
    Where-Object { $_.FullName -notlike "*\.git\*" } |
    ForEach-Object {
        try {
            $content = Get-Content $_.FullName -Raw -ErrorAction SilentlyContinue
            if ($content -and $content -match [regex]::Escape($secret)) {
                $newContent = $content -replace [regex]::Escape($secret), $replacement
                Set-Content -Path $_.FullName -Value $newContent -NoNewline -ErrorAction SilentlyContinue
            }
        } catch {
            # Silently continue
        }
    }

