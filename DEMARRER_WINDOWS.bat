@echo off
setlocal
cd /d "%~dp0"
echo ============================================
echo        TRANSFORMER ATTENTION LAB
echo ============================================
echo.
if not exist ".venv\Scripts\python.exe" (
  echo Creation de l'environnement Python 3.11...
  py -3.11 -m venv .venv
  if errorlevel 1 goto :error
)
echo Installation des bibliotheques...
".venv\Scripts\python.exe" -m pip install -r requirements-dev.txt
if errorlevel 1 goto :error
echo Lancement de l'application...
echo Ouvrez http://localhost:8501 si le navigateur ne s'ouvre pas.
".venv\Scripts\python.exe" -m streamlit run app.py
if errorlevel 1 goto :error
exit /b 0
:error
echo.
echo Une erreur a ete detectee. Consultez le message ci-dessus.
pause
exit /b 1
