$ErrorActionPreference = "Stop"
Set-Location -LiteralPath $PSScriptRoot
$env:PYTHONUTF8 = "1"
$env:TEMP = Join-Path $PSScriptRoot ".tmp"
$env:TMP = $env:TEMP
New-Item -ItemType Directory -Force $env:TEMP | Out-Null
$pythonExe = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
if (!(Test-Path -LiteralPath $pythonExe)) { throw "Run setup.ps1 first." }
& $pythonExe -m streamlit run app.py @args
exit $LASTEXITCODE
