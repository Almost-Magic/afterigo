<#
.SYNOPSIS
    Creates Desktop shortcuts for all AMTL desktop apps.
    Each shortcut starts the backend and launches the Electron app.
.USAGE
    .\create-shortcuts.ps1
#>

$ErrorActionPreference = "SilentlyContinue"

$BASE = Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path))
$DESKTOP_APPS = Split-Path -Parent $MyInvocation.MyCommand.Path
$DIST = Join-Path $DESKTOP_APPS "dist"
$ELECTRON = Join-Path $DESKTOP_APPS "node_modules\.bin\electron.cmd"
$ELECTRON_MAIN = Join-Path $DESKTOP_APPS "shared\main.js"
$SERVICES_PS1 = Join-Path $BASE "services.ps1"
$SHORTCUTS_DIR = Join-Path $env:USERPROFILE "Desktop\AMTL Apps"
$LAUNCHERS_DIR = Join-Path $DESKTOP_APPS "launchers"

# App definitions: id, name, backend service key, accent colour
$Apps = @(
    @{ id = "elaine";        name = "Elaine";              backend = "elaine";       accent = "#c9a84c"; letter = "E" },
    @{ id = "workshop";      name = "The Workshop";        backend = "workshop";     accent = "#c9a84c"; letter = "W" },
    @{ id = "ripple";        name = "Ripple CRM";          backend = "ripple";       accent = "#38bdf8"; letter = "R" },
    @{ id = "touchstone";    name = "Touchstone";          backend = "touchstone";   accent = "#f59e0b"; letter = "T" },
    @{ id = "writer";        name = "CK Writer";           backend = "writer";       accent = "#34d399"; letter = "W" },
    @{ id = "learning";      name = "Learning Assistant";   backend = "learning";     accent = "#38bdf8"; letter = "L" },
    @{ id = "peterman";      name = "Peterman";            backend = "peterman";     accent = "#60a5fa"; letter = "P" },
    @{ id = "genie";         name = "Genie";               backend = "genie";        accent = "#a78bfa"; letter = "G" },
    @{ id = "costanza";      name = "Costanza";            backend = "costanza";     accent = "#a78bfa"; letter = "C" },
    @{ id = "author-studio"; name = "Author Studio";       backend = "authorstudio"; accent = "#e879f9"; letter = "A" },
    @{ id = "junk-drawer";   name = "Junk Drawer";         backend = "junkdrawer";   accent = "#94a3b8"; letter = "J" },
    @{ id = "supervisor";    name = "Supervisor";          backend = "supervisor";   accent = "#f87171"; letter = "S" }
)

Write-Host ""
Write-Host "  AMTL Desktop Shortcuts Creator" -ForegroundColor Cyan
Write-Host "  ================================" -ForegroundColor DarkGray
Write-Host ""

# Create directories
New-Item -ItemType Directory -Path $SHORTCUTS_DIR -Force | Out-Null
New-Item -ItemType Directory -Path $LAUNCHERS_DIR -Force | Out-Null

$created = 0

foreach ($app in $Apps) {
    $id = $app.id
    $name = $app.name
    $backend = $app.backend
    $configPath = Join-Path $DESKTOP_APPS "apps\$id\config.json"

    # Find .exe in dist (check win-unpacked/ first for dir target builds)
    $exePath = $null
    $distDir = Join-Path $DIST $id
    $unpackedDir = Join-Path $distDir "win-unpacked"
    if (Test-Path $unpackedDir) {
        $exeFile = Get-ChildItem -Path $unpackedDir -Filter "*.exe" | Where-Object { $_.Name -notlike "Uninstall*" } | Select-Object -First 1
        if ($exeFile) {
            $exePath = $exeFile.FullName
        }
    }
    if (-not $exePath -and (Test-Path $distDir)) {
        $exeFile = Get-ChildItem -Path $distDir -Filter "*.exe" | Where-Object { $_.Name -notlike "Uninstall*" } | Select-Object -First 1
        if ($exeFile) {
            $exePath = $exeFile.FullName
        }
    }

    # Create launcher script (.bat) — starts backend then opens app
    $launcherPath = Join-Path $LAUNCHERS_DIR "$id.bat"

    if ($exePath) {
        # Use built .exe
        $launcherContent = @"
@echo off
title Launching $name...
echo Starting $name backend...
powershell -ExecutionPolicy Bypass -File "$SERVICES_PS1" start $backend
echo Starting $name desktop...
start "" "$exePath"
exit
"@
    } else {
        # Fallback: use electron dev mode
        $launcherContent = @"
@echo off
title Launching $name...
echo Starting $name backend...
powershell -ExecutionPolicy Bypass -File "$SERVICES_PS1" start $backend
echo Starting $name desktop (dev mode)...
start "" "$ELECTRON" "$ELECTRON_MAIN" "--config=$configPath"
exit
"@
    }

    Set-Content -Path $launcherPath -Value $launcherContent -Encoding ASCII

    # Create .lnk shortcut on Desktop
    $shortcutPath = Join-Path $SHORTCUTS_DIR "$name.lnk"
    $ws = New-Object -ComObject WScript.Shell
    $sc = $ws.CreateShortcut($shortcutPath)
    $sc.TargetPath = $launcherPath
    $sc.WorkingDirectory = $DESKTOP_APPS
    $sc.Description = "$name - Almost Magic Tech Lab"
    $sc.WindowStyle = 7  # Minimised

    # Use .exe icon if available, otherwise use a system icon
    if ($exePath -and (Test-Path $exePath)) {
        $sc.IconLocation = "$exePath,0"
    }

    $sc.Save()
    $created++

    $method = if ($exePath) { "exe" } else { "electron-dev" }
    Write-Host ("  {0,-22} " -f $name) -NoNewline -ForegroundColor Green
    Write-Host "shortcut created ($method)" -ForegroundColor DarkGray
}

# Create "Launch All" shortcut
$launchAllPath = Join-Path $LAUNCHERS_DIR "launch-all.bat"
$launchAllContent = @"
@echo off
title AMTL - Launching All Apps...
echo Starting all backend services...
powershell -ExecutionPolicy Bypass -File "$SERVICES_PS1" start all
echo Waiting for backends...
timeout /t 10 /nobreak >nul
echo Launching desktop apps...
"@

foreach ($app in $Apps) {
    $launcherFile = Join-Path $LAUNCHERS_DIR "$($app.id).bat"
    $launchAllContent += "`nstart """" ""$launcherFile"""
}

$launchAllContent += @"

echo.
echo All apps launching!
timeout /t 5 /nobreak >nul
exit
"@

Set-Content -Path $launchAllPath -Value $launchAllContent -Encoding ASCII

$shortcutPath = Join-Path $SHORTCUTS_DIR "Launch All AMTL Apps.lnk"
$ws = New-Object -ComObject WScript.Shell
$sc = $ws.CreateShortcut($shortcutPath)
$sc.TargetPath = $launchAllPath
$sc.WorkingDirectory = $DESKTOP_APPS
$sc.Description = "Launch all AMTL desktop apps"
$sc.WindowStyle = 7
$sc.Save()

# Create "Start Backends Only" shortcut
$backendsPath = Join-Path $LAUNCHERS_DIR "start-backends.bat"
$backendsContent = @"
@echo off
title AMTL - Starting All Backends...
echo Starting all backend services...
powershell -ExecutionPolicy Bypass -File "$SERVICES_PS1" start all
echo.
echo All backends started. Use The Workshop (http://localhost:5003) to access apps.
echo.
pause
"@

Set-Content -Path $backendsPath -Value $backendsContent -Encoding ASCII

$shortcutPath = Join-Path $SHORTCUTS_DIR "Start Backends Only.lnk"
$ws = New-Object -ComObject WScript.Shell
$sc = $ws.CreateShortcut($shortcutPath)
$sc.TargetPath = $backendsPath
$sc.WorkingDirectory = $DESKTOP_APPS
$sc.Description = "Start all AMTL backend services without desktop apps"
$sc.WindowStyle = 7
$sc.Save()

Write-Host ""
Write-Host "  ================================" -ForegroundColor DarkGray
Write-Host "  $($created + 2) shortcuts created in:" -ForegroundColor Green
Write-Host "    $SHORTCUTS_DIR" -ForegroundColor Cyan
Write-Host ""
Write-Host "  $created app shortcuts + Launch All + Start Backends" -ForegroundColor DarkGray
Write-Host ""
