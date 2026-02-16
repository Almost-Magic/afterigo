#!/usr/bin/env pwsh
# Peterman V4.1 — Startup Script
# Almost Magic Tech Lab Pty Ltd

Write-Host "🎭 Peterman V4.1 — The Authority & Presence Engine" -ForegroundColor Gold
Write-Host "====================================================" -ForegroundColor DarkGray

# Check if PostgreSQL is running
$pgCheck = docker ps --format '{{.Names}}' | Select-String -Pattern "peterman-db"
if (-not $pgCheck) {
    Write-Host "`n⚠️  PostgreSQL not running. Starting container..." -ForegroundColor Yellow
    docker run -d --name peterman-db `
        -e POSTGRES_PASSWORD=postgres `
        -e POSTGRES_DB=peterman `
        -p 5432:5432 `
        postgres:17
    Start-Sleep -Seconds 5
    Write-Host "✅ PostgreSQL container started" -ForegroundColor Green
}

# Check Ollama
$ollamaCheck = curl -s http://localhost:11434/api/tags 2>$null
if ($null -eq $ollamaCheck) {
    Write-Host "`n⚠️  Ollama not responding on localhost:11434" -ForegroundColor Yellow
    Write-Host "   Ensure Ollama is running or update OLLAMA_URL in environment" -ForegroundColor DarkGray
}

# Check SearXNG
$searxngCheck = curl -s http://localhost:8888 2>$null
if ($null -eq $searxngCheck) {
    Write-Host "`n⚠️  SearXNG not responding on localhost:8888" -ForegroundColor Yellow
    Write-Host "   Run: docker run -d --name searxng -p 8888:8080 searxng/searxng" -ForegroundColor DarkGray
}

# Install/verify dependencies
Write-Host "`n📦 Verifying dependencies..." -ForegroundColor Cyan
pip install -q -r requirements.txt

# Initialize database
Write-Host "`n🗄️  Initializing database..." -ForegroundColor Cyan
python -c "from backend.models.database import db, init_db; init_db(app)" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Database initialization may have failed (PostgreSQL might not be ready)" -ForegroundColor Yellow
}

# Start Peterman
Write-Host "`n🚀 Starting Peterman V4.1..." -ForegroundColor Green
Write-Host "   Dashboard: http://localhost:5008" -ForegroundColor Cyan
Write-Host "   API Health: http://localhost:5008/api/health" -ForegroundColor Cyan
Write-Host "`nPress Ctrl+C to stop the server`n" -ForegroundColor DarkGray

python app.py
