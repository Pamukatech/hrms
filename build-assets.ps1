# Rebuild the Tailwind CSS stylesheet.
# Usage:  powershell -ExecutionPolicy Bypass -File .\build-assets.ps1
#
# Uses the standalone Tailwind CSS v4 CLI (no Node/npm required).

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

$tailwind = Join-Path $root 'tools\tailwindcss.exe'
if (-not (Test-Path $tailwind)) {
    throw "Tailwind CLI not found at $tailwind. Download tailwindcss-windows-x64.exe from GitHub releases into .\tools\."
}

& $tailwind -i tailwind/input.css -o static/css/app.css --minify

Write-Host 'Built static/css/app.css' -ForegroundColor Green
