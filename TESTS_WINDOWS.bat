@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Lancez d'abord DEMARRER_WINDOWS.bat.
  pause
  exit /b 1
)
".venv\Scripts\python.exe" -m pytest -q
pause
