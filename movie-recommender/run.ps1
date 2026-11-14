$ErrorActionPreference = "Stop"
Set-Location -LiteralPath $PSScriptRoot
$env:PYTHONUTF8 = "1"
$pythonExe = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
if (!(Test-Path -LiteralPath $pythonExe)) { throw "Run setup.ps1 first." }
if ($args.Count -eq 0) {
    & $pythonExe recommender.py recommend --user 1
} else {
    & $pythonExe recommender.py @args
}
exit $LASTEXITCODE
