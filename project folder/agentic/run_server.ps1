# Load environment variables and start the FastAPI server
# Usage: .\run_server.ps1

# Load .env file
Get-Content .env | ForEach-Object {
    if ($_ -match '^\s*([^#][^=]*?)\s*=\s*(.*)$') {
        $name = $matches[1].Trim()
        $value = $matches[2].Trim()
        [Environment]::SetEnvironmentVariable($name, $value, "Process")
        Write-Host "Set $name" -ForegroundColor Green
    }
}

Write-Host "`nStarting Agentic AI Service on port 8002...`n" -ForegroundColor Cyan

# Start the server
uvicorn src.main:app --reload --port 8002
