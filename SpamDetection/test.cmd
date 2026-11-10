@echo off
call "%~dp0environment.cmd"
"%~dp0.venv\Scripts\python.exe" -m unittest discover -s "%~dp0tests" -v
pause
