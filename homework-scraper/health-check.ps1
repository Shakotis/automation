#!/usr/bin/env pwsh
# Health Check Script for Homework Scraper

Write-Host "`n╔═══════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  Homework Scraper - Health Check         ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════╝`n" -ForegroundColor Cyan

$allGood = $true

# Check Backend
Write-Host "1. Django Backend (http://127.0.0.1:8000)" -ForegroundColor Yellow
try {
    $backend = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/auth/sites/" -ErrorAction Stop -TimeoutSec 3
    Write-Host "   ✓ Backend is running" -ForegroundColor Green
    Write-Host "   Available sites: $($backend.available_sites.Count)" -ForegroundColor Gray
} catch {
    Write-Host "   ✗ Backend is NOT running" -ForegroundColor Red
    Write-Host "   Please start with: .\start-servers.ps1" -ForegroundColor Yellow
    $allGood = $false
}

# Check Frontend
Write-Host "`n2. Next.js Frontend (http://localhost:3000)" -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3000/" -UseBasicParsing -ErrorAction Stop -TimeoutSec 3
    Write-Host "   ✓ Frontend is running (Status: $($response.StatusCode))" -ForegroundColor Green
} catch {
    Write-Host "   ✗ Frontend is NOT running" -ForegroundColor Red
    Write-Host "   Please start with: .\start-servers.ps1" -ForegroundColor Yellow
    $allGood = $false
}

# Check API Proxy
Write-Host "`n3. API Proxy" -ForegroundColor Yellow
try {
    $proxy = Invoke-RestMethod -Uri "http://localhost:3000/api/auth/sites/" -ErrorAction Stop -TimeoutSec 3
    Write-Host "   ✓ API proxy is working" -ForegroundColor Green
} catch {
    Write-Host "   ✗ API proxy failed: $($_.Exception.Message)" -ForegroundColor Red
    $allGood = $false
}

# Check Google Auth Endpoint
Write-Host "`n4. Google OAuth Endpoint" -ForegroundColor Yellow
try {
    $auth = Invoke-RestMethod -Uri "http://localhost:3000/api/auth/google/login/" -ErrorAction Stop -TimeoutSec 3
    if ($auth.authorization_url -like "https://accounts.google.com/*") {
        Write-Host "   ✓ OAuth endpoint working" -ForegroundColor Green
    } else {
        Write-Host "   ⚠ OAuth endpoint returned unexpected response" -ForegroundColor Yellow
    }
} catch {
    Write-Host "   ✗ OAuth endpoint failed: $($_.Exception.Message)" -ForegroundColor Red
    $allGood = $false
}

# Check Node.js processes
Write-Host "`n5. Running Processes" -ForegroundColor Yellow
$nodeProcesses = Get-Process | Where-Object {$_.ProcessName -eq "node"} | Measure-Object
$pythonProcesses = Get-Process | Where-Object {$_.ProcessName -eq "python" -and $_.Path -like "*automation*"} | Measure-Object

if ($nodeProcesses.Count -gt 0) {
    Write-Host "   ✓ Node.js process running ($($nodeProcesses.Count) instance(s))" -ForegroundColor Green
} else {
    Write-Host "   ⚠ No Node.js processes found" -ForegroundColor Yellow
}

if ($pythonProcesses.Count -gt 0) {
    Write-Host "   ✓ Python process running ($($pythonProcesses.Count) instance(s))" -ForegroundColor Green
} else {
    Write-Host "   ⚠ No Python processes found" -ForegroundColor Yellow
}

# Final Summary
Write-Host "`n╔═══════════════════════════════════════════╗" -ForegroundColor Cyan
if ($allGood) {
    Write-Host "║  ✓ All systems operational!              ║" -ForegroundColor Green
    Write-Host "╚═══════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host "`nYou can access the app at: http://localhost:3000" -ForegroundColor Green
} else {
    Write-Host "║  ✗ Some services are down                ║" -ForegroundColor Red
    Write-Host "╚═══════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host "`nTo start all services, run:" -ForegroundColor Yellow
    Write-Host "    .\start-servers.ps1" -ForegroundColor White
}
Write-Host ""
