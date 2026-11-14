$ErrorActionPreference = "Stop"
Set-Location -LiteralPath $PSScriptRoot
New-Item -ItemType Directory -Force .cache, .tmp, wheelhouse | Out-Null
$env:PIP_CACHE_DIR = Join-Path $PSScriptRoot ".cache"
$env:TEMP = Join-Path $PSScriptRoot ".tmp"
$env:TMP = $env:TEMP
$env:PYTHONUTF8 = "1"
if (!(Test-Path .venv\Scripts\python.exe)) {
    python -m venv .venv
    if ($LASTEXITCODE -ne 0) { throw "Python environment creation failed" }
}
$pythonExe = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
$requirementsFile = "requirements.txt"
if (Test-Path requirements-lock.txt) { $requirementsFile = "requirements-lock.txt" }
& $pythonExe -m pip install -r $requirementsFile
if ($LASTEXITCODE -ne 0) { throw "Dependency installation failed" }
& $pythonExe -m pip freeze | Set-Content -Encoding utf8 requirements-lock.txt
& $pythonExe -m pip download -r requirements-lock.txt -d wheelhouse
if ($LASTEXITCODE -ne 0) { throw "Saving offline packages failed" }
if (!(Test-Path data\ratings.csv)) {
    & $pythonExe download_data.py
    if ($LASTEXITCODE -ne 0) { throw "Dataset download failed" }
}
Write-Host "Setup complete. Run: .\run.ps1"
