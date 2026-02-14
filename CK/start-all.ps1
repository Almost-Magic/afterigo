# AMTL App Launcher — 2026-02-15
# Run in PowerShell to start all apps
# Usage: .\start-all.ps1
# To start specific apps: .\start-all.ps1 -Apps "ELAINE","Ripple CRM"

param(
    [string[]]$Apps = @()
)

$base = "C:\Users\ManiPadisetti\Dropbox\Desktop DB\Books and Articles Mani\Books\Almost Magic Tech Lab AMTL\Source and Brand\CK"

$allApps = @(
    @{Name="ELAINE"; Path="Elaine-git"; Port=5000; Cmd="python app.py"},
    @{Name="Ripple CRM"; Path="Ripple CRM"; Port=5001; Cmd="node server.js"},
    @{Name="Identity Atlas"; Path="Identity Atlas"; Port=5002; Cmd="node server.js"},
    @{Name="Learning Assistant"; Path="ck-learning-assistant"; Port=5003; Cmd="python app.py"},
    @{Name="CK-Writer"; Path="CK-Writer"; Port=5004; Cmd="node server.js"},
    @{Name="Costanza"; Path="Costanza"; Port=5005; Cmd="node server.js"},
    @{Name="Peterman"; Path="Peterman"; Port=5006; Cmd="node server.js"},
    @{Name="Genie v2.1"; Path="Finance App\Genie"; Port=5007; Cmd="node server.js"},
    @{Name="Digital Sentinel"; Path="Digital Sentinel"; Port=5008; Cmd="node server.js"},
    @{Name="The Ledger"; Path="The Ledger"; Port=5009; Cmd="node server.js"},
    @{Name="Swiss Army Knife"; Path="Swiss Army Knife"; Port=5010; Cmd="python app.py"},
    @{Name="Opp Hunter"; Path="Opportunity Hunter\backend"; Port=5011; Cmd="python app.py"},
    @{Name="The Workshop"; Path="workshop"; Port=5012; Cmd="python app.py"},
    @{Name="AMTL TTS"; Path="amtl-tts"; Port=3000; Cmd="node dist/server.js"},
    @{Name="AMTL Security"; Path="amtl-security"; Port=8600; Cmd="python main.py"},
    @{Name="Proof"; Path="proof"; Port=8000; Cmd="python -m uvicorn server:app --port 8000"}
)

# Filter if specific apps requested
if ($Apps.Count -gt 0) {
    $selectedApps = $allApps | Where-Object { $Apps -contains $_.Name }
} else {
    $selectedApps = $allApps
}

Write-Host "`n  AMTL App Launcher" -ForegroundColor Cyan
Write-Host "  ================`n" -ForegroundColor Cyan

foreach ($app in $selectedApps) {
    $port = $app.Port
    $busy = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
    if ($busy) {
        Write-Host "  [SKIP] $($app.Name) - port $port already in use" -ForegroundColor Yellow
    } else {
        Write-Host "  [START] $($app.Name) on port $port..." -ForegroundColor Green
        $envPort = "set PORT=$port &&"
        Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$base\$($app.Path)'; `$env:PORT=$port; $($app.Cmd)"
    }
}

Write-Host "`n  All apps launched. Check each PowerShell window for status." -ForegroundColor Cyan
Write-Host "  Note: Default ports have been spread to avoid conflicts.`n" -ForegroundColor DarkGray
