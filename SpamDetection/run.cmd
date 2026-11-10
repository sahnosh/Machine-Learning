@echo off
call "%~dp0environment.cmd"
"%~dp0.venv\Scripts\python.exe" "%~dp0gui.py"
if errorlevel 1 pause
