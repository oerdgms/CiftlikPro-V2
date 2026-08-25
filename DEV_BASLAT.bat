@echo off
setlocal
cd /d "%~dp0"
set "CIFTLIKPRO_PORT=8965"
set "CIFTLIKPRO_DATA_DIR=%LOCALAPPDATA%\CiftlikPro_DEV"
echo CiftlikPro DEV baslatiliyor...
echo Veri: %CIFTLIKPRO_DATA_DIR%
echo Adres: http://127.0.0.1:%CIFTLIKPRO_PORT%/login
echo.
if not exist ".venv\Scripts\python.exe" (
  echo Ilk kullanim: DEV Python ortami hazirlaniyor...
  py -3.12 -m venv .venv 2>nul || python -m venv .venv
  if errorlevel 1 goto :fail
)
".venv\Scripts\python.exe" -c "import PIL, cryptography" >nul 2>&1
if errorlevel 1 (
  echo Gerekli kutuphaneler kuruluyor...
  ".venv\Scripts\python.exe" -m pip install --disable-pip-version-check Pillow cryptography
  if errorlevel 1 goto :fail
)
".venv\Scripts\python.exe" app\server.py
if errorlevel 1 goto :fail
goto :eof
:fail
echo.
echo DEV baslatilamadi. Yukaridaki hata mesajini bana gonderin.
pause
