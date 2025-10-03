# PowerShell script to start Celery services for automated homework scraping
# Run this script from the homework-scraper root directory

Write-Host "Starting Celery Services for Homework Scraper..." -ForegroundColor Green
Write-Host ""

# Check if Redis is installed
$redisInstalled = Get-Command redis-server -ErrorAction SilentlyContinue
if (-not $redisInstalled) {
    Write-Host "WARNING: Redis is not installed or not in PATH!" -ForegroundColor Yellow
    Write-Host "Please install Redis first:" -ForegroundColor Yellow
    Write-Host "  choco install redis-64" -ForegroundColor Cyan
    Write-Host "  or download from: https://github.com/microsoftarchive/redis/releases" -ForegroundColor Cyan
    Write-Host ""
    $continue = Read-Host "Continue anyway? (y/n)"
    if ($continue -ne "y") {
        exit
    }
}

# Check if backend directory exists
if (-not (Test-Path ".\backend")) {
    Write-Host "ERROR: backend directory not found!" -ForegroundColor Red
    Write-Host "Please run this script from the homework-scraper root directory." -ForegroundColor Red
    exit
}

# Change to backend directory for Celery commands
$backendPath = Resolve-Path ".\backend"

Write-Host "Starting services in separate windows..." -ForegroundColor Cyan
Write-Host ""

# Start Redis in a new window
Write-Host "[1/3] Starting Redis server..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Write-Host 'Redis Server' -ForegroundColor Green; redis-server"
Start-Sleep -Seconds 2

# Start Celery Worker in a new window
Write-Host "[2/3] Starting Celery Worker..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Write-Host 'Celery Worker' -ForegroundColor Green; cd '$backendPath'; celery -A homework_scraper worker --loglevel=info --pool=solo"
Start-Sleep -Seconds 3

# Start Celery Beat in a new window
Write-Host "[3/3] Starting Celery Beat (Scheduler)..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Write-Host 'Celery Beat Scheduler' -ForegroundColor Green; cd '$backendPath'; celery -A homework_scraper beat --loglevel=info"
Start-Sleep -Seconds 2

Write-Host ""
Write-Host "=====================================" -ForegroundColor Green
Write-Host "All Celery services started!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green
Write-Host ""
Write-Host "Running services:" -ForegroundColor Cyan
Write-Host "  [✓] Redis Server (localhost:6379)" -ForegroundColor White
Write-Host "  [✓] Celery Worker (processing tasks)" -ForegroundColor White
Write-Host "  [✓] Celery Beat (scheduling tasks)" -ForegroundColor White
Write-Host ""
Write-Host "Automated scraping schedule:" -ForegroundColor Cyan
Write-Host "  • 9am-1pm: Every 2 hours (9am, 11am, 1pm)" -ForegroundColor White
Write-Host "  • 1pm-4pm: Every hour (1pm, 2pm, 3pm, 4pm)" -ForegroundColor White
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Start Django: cd backend; python manage.py runserver" -ForegroundColor White
Write-Host "  2. Start Frontend: cd frontend; npm run dev" -ForegroundColor White
Write-Host ""
Write-Host "Monitoring:" -ForegroundColor Yellow
Write-Host "  • View logs in the opened terminal windows" -ForegroundColor White
Write-Host "  • Install Flower for web monitoring: pip install flower" -ForegroundColor White
Write-Host "  • Run Flower: celery -A homework_scraper flower" -ForegroundColor White
Write-Host "  • Access Flower at: http://localhost:5555" -ForegroundColor White
Write-Host ""
Write-Host "To stop services: Close the terminal windows or press Ctrl+C in each." -ForegroundColor Yellow
Write-Host ""
