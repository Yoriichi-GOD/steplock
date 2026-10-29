@echo off
setlocal
cd /d "%~dp0"
set "STEPLOCK_PYTHON=python"
set "STEPLOCK_SETUP="
if exist ".venv\Scripts\python.exe" set "STEPLOCK_PYTHON=.venv\Scripts\python.exe"
if not exist ".venv\Scripts\python.exe" set "STEPLOCK_SETUP=--setup"
if not exist "frontend\dist\index.html" set "STEPLOCK_SETUP=--setup"
"%STEPLOCK_PYTHON%" scripts\dev.py %STEPLOCK_SETUP% --open
if errorlevel 1 pause
