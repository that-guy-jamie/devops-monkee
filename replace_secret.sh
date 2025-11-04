#!/bin/sh
find . -type f \( -name "*.py" -o -name "*.ps1" -o -name "*.md" -o -name "*.txt" -o -name "*.yaml" -o -name "*.yml" -o -name "*.json" \) -exec sed -i 's/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/***REDACTED_SECRET***/g' {} +

