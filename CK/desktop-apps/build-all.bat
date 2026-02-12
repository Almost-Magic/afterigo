@echo off
REM ============================================================
REM AMTL Desktop Apps -- Build All to Standalone .exe
REM ============================================================
REM Builds every CK desktop app using electron-builder.
REM Output goes to CK\desktop-apps\dist\<appname>\
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
    echo [1/4] Installing Electron and electron-builder...
    npm install --save-dev electron@latest electron-builder@latest
    if %ERRORLEVEL% neq 0 (
        echo ERROR: npm install failed.
        pause
        exit /b 1
    )
) else (
    echo [1/4] Dependencies already installed.
)

REM Step 3: Convert SVG icons to ICO (simple PNG fallback)
echo [2/4] Checking icons...
if not exist "icons\elaine.ico" (
    echo   SVG icons found but .ico files missing.
    echo   Electron-builder will use SVG fallback or you can convert manually.
    echo   For best results: npx svg2ico icons\elaine.svg icons\elaine.ico
)

REM Step 4: Build each app
echo [3/4] Building all apps...
echo.

set APPS=elaine workshop ripple touchstone writer learning peterman genie costanza author-studio junk-drawer supervisor
set COUNT=0
set TOTAL=12

for %%A in (%APPS%) do (
    set /a COUNT+=1
    echo   [!COUNT!/%TOTAL%] Building %%A...

    REM Create a temporary build package.json for each app
    cd /d "%~dp0apps\%%A"

    REM Run electron-builder from the app directory
    call npx electron-builder --win --config.extends=null --config.appId=tech.almostmagic.%%A --config.productName="%%A" --config.files[0]="../../shared/**/*" --config.files[1]="config.json" --config.extraMetadata.main="shared/main.js" --config.directories.output="../../dist/%%A" --config.win.target=portable 2>nul

    if !ERRORLEVEL! equ 0 (
        echo     Built successfully.
    ) else (
        echo     WARNING: Build may have issues. Check dist\%%A\ folder.
    )

    cd /d "%~dp0"
)

echo.
echo [4/4] Build complete!
echo.
echo Output location: %~dp0dist\
echo.

REM Step 5: Create Desktop shortcuts
echo Creating Desktop shortcuts...
set DESKTOP=%USERPROFILE%\Desktop

for %%A in (%APPS%) do (
    if exist "dist\%%A\*.exe" (
        for /f "delims=" %%F in ('dir /b "dist\%%A\*.exe" 2^>nul') do (
            echo   Shortcut: %%A
            powershell -Command "$ws = New-Object -ComObject WScript.Shell; $sc = $ws.CreateShortcut('%DESKTOP%\AMTL %%A.lnk'); $sc.TargetPath = '%~dp0dist\%%A\%%F'; $sc.WorkingDirectory = '%~dp0dist\%%A'; $sc.Save()"
        )
    )
)

echo.
echo  ================================================
echo   All done! Desktop shortcuts created.
echo  ================================================
echo.
pause
