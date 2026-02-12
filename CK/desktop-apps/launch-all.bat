@echo off
REM ============================================================
REM AMTL Desktop Apps -- Launch All
REM ============================================================
REM 1. Starts all backend services via services.ps1
REM 2. Opens Electron desktop wrappers for core apps
REM ============================================================

setlocal
cd /d "%~dp0"

set BASE=%~dp0..\..
set ELECTRON=%~dp0node_modules\.bin\electron.cmd
set SHARED=%~dp0shared\main.js

echo.
echo  ================================================
echo   AMTL Desktop Apps -- Launch All
echo  ================================================
echo.

REM Step 1: Start backend services
echo [1/3] Starting backend services...
if exist "%BASE%\services.ps1" (
    powershell -ExecutionPolicy Bypass -File "%BASE%\services.ps1" start all
    echo   Backends starting. Waiting 10 seconds...
    timeout /t 10 /nobreak >nul
) else (
    echo   WARNING: services.ps1 not found at %BASE%\services.ps1
    echo   Backend services may need to be started manually.
)

REM Step 2: Check Electron is installed
if not exist "%ELECTRON%" (
    echo [2/3] Installing Electron...
    cd /d "%~dp0"
    npm install
    cd /d "%~dp0"
)

echo [2/3] Electron ready.

REM Step 3: Launch core desktop apps
echo [3/3] Launching desktop apps...
echo.

REM Core apps (always launch)
echo   Launching Elaine...
start "" "%ELECTRON%" "%SHARED%" "--config=%~dp0apps\elaine\config.json"

echo   Launching Workshop...
start "" "%ELECTRON%" "%SHARED%" "--config=%~dp0apps\workshop\config.json"

echo   Launching Ripple CRM...
start "" "%ELECTRON%" "%SHARED%" "--config=%~dp0apps\ripple\config.json"

echo.
echo  ================================================
echo   Core apps launched: Elaine, Workshop, Ripple
echo  ================================================
echo.
echo   To launch individual apps:
echo     npm run start:elaine
echo     npm run start:writer
echo     npm run start:peterman
echo     etc.
echo.
echo   To launch ALL apps (including on-demand):
echo     launch-all.bat --all
echo.

if "%~1"=="--all" (
    echo Launching all remaining apps...
    start "" "%ELECTRON%" "%SHARED%" "--config=%~dp0apps\touchstone\config.json"
    start "" "%ELECTRON%" "%SHARED%" "--config=%~dp0apps\writer\config.json"
    start "" "%ELECTRON%" "%SHARED%" "--config=%~dp0apps\learning\config.json"
    start "" "%ELECTRON%" "%SHARED%" "--config=%~dp0apps\peterman\config.json"
    start "" "%ELECTRON%" "%SHARED%" "--config=%~dp0apps\genie\config.json"
    start "" "%ELECTRON%" "%SHARED%" "--config=%~dp0apps\costanza\config.json"
    start "" "%ELECTRON%" "%SHARED%" "--config=%~dp0apps\author-studio\config.json"
    start "" "%ELECTRON%" "%SHARED%" "--config=%~dp0apps\junk-drawer\config.json"
    start "" "%ELECTRON%" "%SHARED%" "--config=%~dp0apps\supervisor\config.json"
    echo All 12 desktop apps launched.
)
