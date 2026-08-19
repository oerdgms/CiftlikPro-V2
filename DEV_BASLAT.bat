@echo off
setlocal
chcp 65001 >nul
title CiftlikPro V3.9.7 DEV Test
cd /d "%~dp0"

set "CIFTLIKPRO_DATA_DIR=%LOCALAPPDATA%\CiftlikPro_DEV"
set "CIFTLIKPRO_DEV_PORT=8954"

set "PYEXE="
where py >nul 2>nul && set "PYEXE=py"
if not defined PYEXE (
  where python >nul 2>nul && set "PYEXE=python"
)

if not defined PYEXE (
  echo.
  echo [HATA] Bu bilgisayarda Python bulunamadi.
  echo DEV test modu icin Python 3.11 veya 3.12 gerekiyor.
  echo Kurulu CiftlikPro'ya hicbir degisiklik yapilmadi.
  echo.
  pause
  exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
  echo [1/3] DEV ortami ilk kez hazirlaniyor...
  %PYEXE% -m venv .venv
  if errorlevel 1 goto :fail
)

set "VPY=.venv\Scripts\python.exe"

"%VPY%" -c "import PIL, cryptography" >nul 2>nul
if errorlevel 1 (
  echo [2/3] Gerekli kutuphaneler kuruluyor. Bu sadece ilk acilista biraz surebilir...
  "%VPY%" -m pip install --disable-pip-version-check -r requirements-dev.txt
  if errorlevel 1 goto :fail
) else (
  echo [2/3] Kutuphaneler hazir.
)

echo [3/3] CiftlikPro DEV 8954 portunda baslatiliyor...
echo Normal kurulum 8953, DEV test 8954 portunu kullanir.
echo.
"%VPY%" app\dev_launcher.py
exit /b %errorlevel%

:fail
echo.
echo [HATA] DEV ortam baslatilamadi. Yukaridaki hata mesajini ekran goruntusu olarak bana gonderebilirsiniz.
echo Kurulu CiftlikPro ve asil verileriniz degistirilmedi.
echo.
pause
exit /b 1
