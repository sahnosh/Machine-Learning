$ErrorActionPreference = "Stop"
Set-Location -LiteralPath $PSScriptRoot
New-Item -ItemType Directory -Force .cache, .tmp | Out-Null
$env:PIP_CACHE_DIR = Join-Path $PSScriptRoot ".cache"
$env:TEMP = Join-Path $PSScriptRoot ".tmp"
$env:TMP = $env:TEMP
$env:PYTHONUTF8 = "1"
if (!(Test-Path .venv\Scripts\python.exe)) {
    python -m venv .venv
    if ($LASTEXITCODE -ne 0) { throw "Environment creation failed" }
}
& .\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
if ($LASTEXITCODE -ne 0) { throw "Dependency installation failed" }
Write-Host "Ready. Run: powershell -ExecutionPolicy Bypass -File .\run.ps1"
