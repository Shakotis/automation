# Deploy RISC implementation to Raspberry Pi

$ErrorActionPreference = "Stop"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "RISC (Cross-Account Protection) Deployment" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$RPI_USER = "dovydukas"
$RPI_HOST = "192.168.1.33"
$BACKEND_DIR = "/home/dovydukas/homework-scraper-backend"
$SERVICE_NAME = "homework-scraper"

Write-Host "Step 1: Transferring RISC files to RPI..." -ForegroundColor Yellow
scp -r backend/risc "${RPI_USER}@${RPI_HOST}:${BACKEND_DIR}/"

Write-Host ""
Write-Host "Step 2: Installing Python dependencies..." -ForegroundColor Yellow
ssh "${RPI_USER}@${RPI_HOST}" @"
cd $BACKEND_DIR
source venv/bin/activate
pip install 'PyJWT>=2.8.0' 'cryptography>=41.0.0' 'requests>=2.31.0' 'google-auth>=2.23.0'
"@

Write-Host ""
Write-Host "Step 3: Running migrations..." -ForegroundColor Yellow
ssh "${RPI_USER}@${RPI_HOST}" @"
cd $BACKEND_DIR
source venv/bin/activate
python manage.py makemigrations risc
python manage.py migrate risc
"@

Write-Host ""
Write-Host "Step 4: Collecting static files..." -ForegroundColor Yellow
ssh "${RPI_USER}@${RPI_HOST}" @"
cd $BACKEND_DIR
source venv/bin/activate
python manage.py collectstatic --noinput
"@

Write-Host ""
Write-Host "Step 5: Restarting backend service..." -ForegroundColor Yellow
ssh "${RPI_USER}@${RPI_HOST}" "sudo systemctl restart $SERVICE_NAME.service"

Write-Host ""
Write-Host "Step 6: Checking service status..." -ForegroundColor Yellow
ssh "${RPI_USER}@${RPI_HOST}" "sudo systemctl status $SERVICE_NAME.service --no-pager -l"

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "✅ RISC Deployment Complete!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "1. Add 'risc' to INSTALLED_APPS in settings.py"
Write-Host "2. Add path('risc/', include('risc.urls')) to main urls.py"
Write-Host "3. Set RISC_RECEIVER_URL in settings.py"
Write-Host "4. Create RISCConfiguration in Django admin"
Write-Host "5. Setup Google Cloud service account with RISC Configuration Admin role"
Write-Host "6. Run: python manage.py configure_risc --service-account /path/to/sa.json --receiver-url https://api.dovydas.space/risc/receiver/"
Write-Host ""
Write-Host "Test receiver endpoint:" -ForegroundColor Yellow
Write-Host '  curl -X POST https://api.dovydas.space/risc/receiver/ -H "Content-Type: application/json" -d "{\"test\":\"data\"}"'
Write-Host ""
Write-Host "Check RISC status:" -ForegroundColor Yellow
Write-Host "  curl https://api.dovydas.space/risc/status/"
Write-Host ""
