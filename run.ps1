# Start the Payroll System (dev server)
# Usage:  powershell -ExecutionPolicy Bypass -File .\run.ps1

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

$python = Join-Path $root '.venv\Scripts\python.exe'

if (-not (Test-Path $python)) {
    Write-Host 'Creating virtual environment (.venv)...' -ForegroundColor Cyan
    python -m venv .venv
    & $python -m pip install --upgrade pip
    & $python -m pip install -r requirements.txt
}

if (-not (Test-Path (Join-Path $root 'hrms.db'))) {
    Write-Host 'Seeding demo data (admin@demo.co.ke / password)...' -ForegroundColor Cyan
    & $python -m app.seed
}

if (-not (Test-Path (Join-Path $root 'static\css\app.css'))) {
    Write-Host 'CSS missing - building Tailwind stylesheet...' -ForegroundColor Yellow
    & (Join-Path $root 'build-assets.ps1')
}

Write-Host ''
Write-Host 'Payroll System running at http://127.0.0.1:8000' -ForegroundColor Green
Write-Host 'Demo login: admin@demo.co.ke / password' -ForegroundColor Green
Write-Host ''

& $python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
