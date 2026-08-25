@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  py -3.12 -m venv .venv 2>nul || python -m venv .venv
  if errorlevel 1 goto :fail
)
".venv\Scripts\python.exe" -c "import PIL, cryptography, webview" >nul 2>&1
if errorlevel 1 (
  ".venv\Scripts\python.exe" -m pip install --disable-pip-version-check -r requirements.txt
  if errorlevel 1 goto :fail
)
set "CIFTLIKPRO_DATA_DIR=%LOCALAPPDATA%\CiftlikPro"
".venv\Scripts\python.exe" app\desktop_launcher.py
if errorlevel 1 goto :fail
goto :eof
:fail
echo.
echo CiftlikPro baslatilamadi. Yukaridaki hata mesajini kontrol edin.
pause
