@echo off
setlocal
call "%~dp0environment.cmd"
if exist "%~dp0.venv\Scripts\python.exe" goto install
if exist "%~dp0runtime\python.exe" (
    "%~dp0runtime\python.exe" -m venv "%~dp0.venv"
) else (
    py -3.11 -m venv "%~dp0.venv"
)
if errorlevel 1 (
    echo Install Python 3.11 with the Windows Python launcher, then retry.
    exit /b 1
)
:install
if exist "%~dp0wheelhouse\scikit_learn-1.5.2-cp311-cp311-win_amd64.whl" (
    "%~dp0.venv\Scripts\python.exe" -m pip install --no-index --find-links "%~dp0wheelhouse" -r "%~dp0requirements.txt"
) else (
    "%~dp0.venv\Scripts\python.exe" -m pip install -r "%~dp0requirements.txt"
)
if errorlevel 1 exit /b 1
"%~dp0.venv\Scripts\python.exe" "%~dp0spam_detector.py" train
exit /b %errorlevel%
