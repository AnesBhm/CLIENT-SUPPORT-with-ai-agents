# Load environment variables and run CLI
# Usage: .\run_cli.ps1

# Load .env file
Get-Content .env | ForEach-Object {
    if ($_ -match '^\s*([^#][^=]*?)\s*=\s*(.*)$') {
        $name = $matches[1].Trim()
        $value = $matches[2].Trim()
        [Environment]::SetEnvironmentVariable($name, $value, "Process")
        Write-Host "Set $name" -ForegroundColor Green
    }
}

Write-Host "`nStarting CLI...`n" -ForegroundColor Cyan

# Run the CLI
python cli.py
