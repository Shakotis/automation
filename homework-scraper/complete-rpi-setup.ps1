# Complete RPI Backend Setup Script
# Run this after packages are installed

$SSH_KEY = "C:\Users\Dovydukas\.ssh\rpi_3"
$SSH_CMD = "C:\Windows\System32\OpenSSH\ssh.exe"
$SCP_CMD = "C:\Windows\System32\OpenSSH\scp.exe"
$RPI_USER = "dovydukas"
$RPI_HOST = "172.20.10.7"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Completing RPI Backend Setup" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Step 1: Check if packages are installed
Write-Host "[1/9] Checking Python packages..." -ForegroundColor Yellow
$packageCount = & $SSH_CMD -i $SSH_KEY "${RPI_USER}@${RPI_HOST}" "cd homework-scraper-backend && ls venv/lib/python3.13/site-packages/ | wc -l"
Write-Host "Packages installed: $packageCount" -ForegroundColor White

if ($packageCount -lt 50) {
    Write-Host "❌ Packages not fully installed yet. Please wait for pip install to complete." -ForegroundColor Red
    Write-Host "Run this command to check progress:" -ForegroundColor Yellow
    Write-Host "  ssh -i $SSH_KEY ${RPI_USER}@${RPI_HOST} 'ps aux | grep pip'" -ForegroundColor White
    exit 1
}

# Step 2: Generate encryption key
Write-Host "`n[2/9] Generating encryption key..." -ForegroundColor Yellow
$encKey = & $SSH_CMD -i $SSH_KEY "${RPI_USER}@${RPI_HOST}" @"
cd homework-scraper-backend && \
source venv/bin/activate && \
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
"@
Write-Host "Generated key: $encKey" -ForegroundColor Green

# Step 3: Update .env with encryption key
Write-Host "`n[3/9] Updating .env file..." -ForegroundColor Yellow
& $SSH_CMD -i $SSH_KEY "${RPI_USER}@${RPI_HOST}" @"
cd homework-scraper-backend && \
sed -i 's/^ENCRYPTION_KEY=.*/ENCRYPTION_KEY=$encKey/' .env && \
echo "✓ Updated encryption key in .env"
"@

# Step 4: Run Django migrations
Write-Host "`n[4/9] Running Django migrations..." -ForegroundColor Yellow
& $SSH_CMD -i $SSH_KEY "${RPI_USER}@${RPI_HOST}" @"
cd homework-scraper-backend && \
source venv/bin/activate && \
python manage.py migrate && \
echo "✓ Migrations completed"
"@

# Step 5: Collect static files
Write-Host "`n[5/9] Collecting static files..." -ForegroundColor Yellow
& $SSH_CMD -i $SSH_KEY "${RPI_USER}@${RPI_HOST}" @"
cd homework-scraper-backend && \
source venv/bin/activate && \
python manage.py collectstatic --noinput && \
echo "✓ Static files collected"
"@

# Step 6: Copy and install systemd services
Write-Host "`n[6/9] Installing systemd services..." -ForegroundColor Yellow
& $SCP_CMD -i $SSH_KEY "homework-scraper.service" "${RPI_USER}@${RPI_HOST}:/tmp/"
& $SCP_CMD -i $SSH_KEY "homework-scraper-celery.service" "${RPI_USER}@${RPI_HOST}:/tmp/"
& $SCP_CMD -i $SSH_KEY "homework-scraper-celery-beat.service" "${RPI_USER}@${RPI_HOST}:/tmp/"

& $SSH_CMD -i $SSH_KEY "${RPI_USER}@${RPI_HOST}" @"
sudo mv /tmp/homework-scraper.service /etc/systemd/system/ && \
sudo mv /tmp/homework-scraper-celery.service /etc/systemd/system/ && \
sudo mv /tmp/homework-scraper-celery-beat.service /etc/systemd/system/ && \
sudo systemctl daemon-reload && \
echo "✓ Services installed"
"@

# Step 7: Configure Nginx
Write-Host "`n[7/9] Configuring Nginx..." -ForegroundColor Yellow
& $SCP_CMD -i $SSH_KEY "nginx-homework-scraper.conf" "${RPI_USER}@${RPI_HOST}:/tmp/"

& $SSH_CMD -i $SSH_KEY "${RPI_USER}@${RPI_HOST}" @"
sudo mv /tmp/nginx-homework-scraper.conf /etc/nginx/sites-available/homework-scraper && \
sudo ln -sf /etc/nginx/sites-available/homework-scraper /etc/nginx/sites-enabled/ && \
sudo rm -f /etc/nginx/sites-enabled/default && \
sudo nginx -t && \
sudo systemctl reload nginx && \
echo "✓ Nginx configured"
"@

# Step 8: Start services
Write-Host "`n[8/9] Starting services..." -ForegroundColor Yellow
& $SSH_CMD -i $SSH_KEY "${RPI_USER}@${RPI_HOST}" @"
sudo systemctl enable homework-scraper && \
sudo systemctl start homework-scraper && \
sudo systemctl enable homework-scraper-celery && \
sudo systemctl start homework-scraper-celery && \
sudo systemctl enable homework-scraper-celery-beat && \
sudo systemctl start homework-scraper-celery-beat && \
echo "✓ All services started"
"@

# Step 9: Test the setup
Write-Host "`n[9/9] Testing the deployment..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

& $SSH_CMD -i $SSH_KEY "${RPI_USER}@${RPI_HOST}" @"
echo "=== Service Status ===" && \
sudo systemctl is-active homework-scraper && \
sudo systemctl is-active homework-scraper-celery && \
sudo systemctl is-active homework-scraper-celery-beat && \
sudo systemctl is-active nginx && \
sudo systemctl is-active redis-server
"@

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "✓ Deployment Complete!" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Green

Write-Host "Backend is running at:" -ForegroundColor Cyan
Write-Host "  • Local: http://172.20.10.7/api/" -ForegroundColor White
Write-Host "  • Domain (after port forward): https://api.dovydas.space/api/" -ForegroundColor White

Write-Host "`nTest the API:" -ForegroundColor Cyan
Write-Host "  curl http://172.20.10.7/api/test/" -ForegroundColor White

Write-Host "`nCheck service status:" -ForegroundColor Cyan
Write-Host "  ssh -i $SSH_KEY ${RPI_USER}@${RPI_HOST} 'sudo systemctl status homework-scraper'" -ForegroundColor White

Write-Host "`nView logs:" -ForegroundColor Cyan
Write-Host "  ssh -i $SSH_KEY ${RPI_USER}@${RPI_HOST} 'sudo journalctl -u homework-scraper -f'" -ForegroundColor White

Write-Host "`n⚠️  IMPORTANT: Configure Supabase" -ForegroundColor Yellow
Write-Host "Edit .env on RPI and add:" -ForegroundColor White
Write-Host "  SUPABASE_URL=https://your-project.supabase.co" -ForegroundColor Gray
Write-Host "  SUPABASE_KEY=your-anon-key" -ForegroundColor Gray
Write-Host "Then restart: sudo systemctl restart homework-scraper" -ForegroundColor White
