# Script to start both Django backend and Next.js frontend servers

Write-Host "🚀 Starting Homework Scraper Servers..." -ForegroundColor Green
Write-Host ""

# Check if Python virtual environment exists
$venvPath = "C:\Users\Dovydukas\Documents\GitHub\automation\.venv"
if (-Not (Test-Path $venvPath)) {
    Write-Host "❌ Virtual environment not found at $venvPath" -ForegroundColor Red
    exit 1
}

# Check if Node.js is available
$nodePath = "C:\Program Files\nodejs"
if (-Not (Test-Path "$nodePath\node.exe")) {
    Write-Host "❌ Node.js not found at $nodePath" -ForegroundColor Red
    exit 1
}

# Kill any existing Node.js processes (to clear old Next.js instances)
Write-Host "🔄 Stopping any existing Node.js processes..." -ForegroundColor Yellow
Get-Process | Where-Object {$_.ProcessName -like "*node*"} | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

# Kill any existing Python processes running Django (optional)
Write-Host "🔄 Checking for existing Django processes..." -ForegroundColor Yellow
Get-Process | Where-Object {$_.CommandLine -like "*manage.py runserver*"} | Stop-Process -Force -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "✅ Starting Django Backend (Port 8000)..." -ForegroundColor Cyan

# Start Django backend in a new PowerShell window
$backendPath = Join-Path $PSScriptRoot "backend"
$djangoScript = @"
Set-Location '$backendPath'
& '$venvPath\Scripts\Activate.ps1'
`$host.UI.RawUI.WindowTitle = 'Django Backend - Port 8000'
Write-Host '🐍 Django Backend Server' -ForegroundColor Green
Write-Host 'Running on http://127.0.0.1:8000' -ForegroundColor Yellow
Write-Host 'Press Ctrl+C to stop' -ForegroundColor Gray
Write-Host ''
python manage.py runserver
"@

Start-Process powershell -ArgumentList "-NoExit", "-Command", $djangoScript

# Wait a moment for Django to start
Start-Sleep -Seconds 3

Write-Host "✅ Starting Next.js Frontend (Port 3000)..." -ForegroundColor Cyan

# Start Next.js frontend in a new PowerShell window
$frontendPath = Join-Path $PSScriptRoot "frontend"
$nextjsScript = @"
Set-Location '$frontendPath'
`$env:PATH = '$nodePath;' + `$env:PATH
`$host.UI.RawUI.WindowTitle = 'Next.js Frontend - Port 3000'
Write-Host '⚡ Next.js Frontend Server' -ForegroundColor Green
Write-Host 'Running on http://localhost:3000' -ForegroundColor Yellow
Write-Host 'Press Ctrl+C to stop' -ForegroundColor Gray
Write-Host ''
npm run dev
"@

Start-Process powershell -ArgumentList "-NoExit", "-Command", $nextjsScript

Write-Host ""
Write-Host "✅ Both servers are starting!" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 Django Backend:  http://127.0.0.1:8000" -ForegroundColor Cyan
Write-Host "🌐 Next.js Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host ""
Write-Host "📝 Check the new terminal windows for server logs" -ForegroundColor Yellow
Write-Host "🛑 Close the terminal windows or press Ctrl+C in them to stop servers" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press any key to exit this launcher..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
