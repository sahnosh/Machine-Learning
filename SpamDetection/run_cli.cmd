@echo off
call "%~dp0environment.cmd"
"%~dp0.venv\Scripts\python.exe" "%~dp0spam_detector.py" %*
