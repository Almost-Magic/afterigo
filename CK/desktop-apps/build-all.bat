@echo off
REM ============================================================
REM AMTL Desktop Apps -- Build All to Standalone .exe
REM ============================================================
REM Builds one Electron app, then clones it for all 12 CK apps.
REM Output goes to CK\desktop-apps\dist\<appname>\win-unpacked\
REM ============================================================

setlocal enabledelayedexpansion
cd /d "%~dp0"

echo.
echo  ================================================
echo   AMTL Desktop Apps -- Build All
echo  ================================================
echo.

REM Step 1: Check Node.js
where node >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ERROR: Node.js not found. Install from https://nodejs.org
    pause
    exit /b 1
)

REM Step 2: Install dependencies if needed
if not exist "node_modules\electron" (
    echo [1/5] Installing Electron and electron-builder...
    npm install --save-dev electron@latest electron-builder@latest
    if %ERRORLEVEL% neq 0 (
        echo ERROR: npm install failed.
        pause
        exit /b 1
    )
) else (
    echo [1/5] Dependencies already installed.
)

REM Step 3: Generate app configs and icons
echo [2/5] Generating app configs and icons...
node generate-apps.js
node generate-icons.js

REM Step 4: Build base app (elaine) with electron-builder
echo [3/5] Building base app (Elaine)...
node build.js elaine
if not exist "dist\elaine\win-unpacked\Elaine.exe" (
    echo ERROR: Base build failed. Check logs above.
    pause
    exit /b 1
)

REM Step 5: Clone for all other apps
echo [4/5] Cloning for remaining apps...
node clone-apps.js

REM Step 6: Create Desktop shortcuts
echo [5/5] Creating Desktop shortcuts...
powershell -ExecutionPolicy Bypass -File "%~dp0create-shortcuts.ps1"

echo.
echo  ================================================
echo   All done! 12 desktop apps built.
echo   Shortcuts: %%USERPROFILE%%\Desktop\AMTL Apps\
echo  ================================================
echo.
pause
