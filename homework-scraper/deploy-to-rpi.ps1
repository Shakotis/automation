# Deploy Backend to Raspberry Pi 3B+
# This script deploys the Django backend to the RPI server

$RPI_USER = "dovydukas"
$RPI_HOST = "172.20.10.7"
$SSH_KEY = "C:\Users\Dovydukas\.ssh\rpi_3"
$BACKEND_DIR = "homework-scraper-backend"
$SSH_CMD = "C:\Windows\System32\OpenSSH\ssh.exe"
$SCP_CMD = "C:\Windows\System32\OpenSSH\scp.exe"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Deploying Backend to Raspberry Pi" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Step 1: Create backend directory on RPI
Write-Host "`n[1/8] Creating backend directory on RPI..." -ForegroundColor Yellow
& $SSH_CMD -i $SSH_KEY "${RPI_USER}@${RPI_HOST}" "mkdir -p $BACKEND_DIR"

# Step 2: Copy backend files to RPI
Write-Host "`n[2/8] Copying backend files to RPI..." -ForegroundColor Yellow
& $SCP_CMD -i $SSH_KEY -r "backend/*" "${RPI_USER}@${RPI_HOST}:${BACKEND_DIR}/"

# Step 3: Create .env file on RPI
Write-Host "`n[3/8] Creating .env file on RPI..." -ForegroundColor Yellow
$ENV_CONTENT = @"
DEBUG=False
SECRET_KEY=your-secret-key-here-$(Get-Random -Maximum 999999)
ALLOWED_HOSTS=172.20.10.7,api.dovydas.space,localhost,127.0.0.1
FRONTEND_URL=https://nd.dovydas.space

# Supabase Settings
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key

# Google OAuth
GOOGLE_OAUTH2_CLIENT_ID=
GOOGLE_OAUTH2_CLIENT_SECRET=
GOOGLE_OAUTH_REDIRECT_URI=https://api.dovydas.space/api/auth/google/callback

# Encryption
ENCRYPTION_KEY=

# Session Security
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False
SESSION_COOKIE_DOMAIN=

# Database
DATABASE_URL=sqlite:///db.sqlite3
"@

$ENV_CONTENT | Out-File -FilePath "temp_env" -Encoding UTF8 -NoNewline
& $SCP_CMD -i $SSH_KEY "temp_env" "${RPI_USER}@${RPI_HOST}:${BACKEND_DIR}/.env"
Remove-Item "temp_env"

# Step 4: Install system dependencies on RPI
Write-Host "`n[4/8] Installing system dependencies on RPI..." -ForegroundColor Yellow
& $SSH_CMD -i $SSH_KEY "${RPI_USER}@${RPI_HOST}" @"
sudo apt-get update && \
sudo apt-get install -y nginx redis-server python3-venv python3-pip && \
sudo systemctl enable redis-server && \
sudo systemctl start redis-server
"@

# Step 5: Set up Python virtual environment and install dependencies
Write-Host "`n[5/8] Setting up Python virtual environment..." -ForegroundColor Yellow
& $SSH_CMD -i $SSH_KEY "${RPI_USER}@${RPI_HOST}" @"
cd $BACKEND_DIR && \
python3 -m venv venv && \
source venv/bin/activate && \
pip install --upgrade pip && \
pip install -r requirements.txt && \
playwright install chromium && \
playwright install-deps
"@

# Step 6: Run Django migrations
Write-Host "`n[6/8] Running Django migrations..." -ForegroundColor Yellow
& $SSH_CMD -i $SSH_KEY "${RPI_USER}@${RPI_HOST}" @"
cd $BACKEND_DIR && \
source venv/bin/activate && \
python manage.py migrate && \
python manage.py collectstatic --noinput
"@

# Step 7: Create systemd service files
Write-Host "`n[7/8] Creating systemd service files..." -ForegroundColor Yellow

# Create gunicorn service
$GUNICORN_SERVICE = @"
[Unit]
Description=Homework Scraper Gunicorn Service
After=network.target

[Service]
User=$RPI_USER
Group=$RPI_USER
WorkingDirectory=/home/$RPI_USER/$BACKEND_DIR
Environment="PATH=/home/$RPI_USER/$BACKEND_DIR/venv/bin"
ExecStart=/home/$RPI_USER/$BACKEND_DIR/venv/bin/gunicorn homework_scraper.wsgi:application --bind 0.0.0.0:8000 --workers 2 --timeout 120

[Install]
WantedBy=multi-user.target
"@

$GUNICORN_SERVICE | Out-File -FilePath "temp_gunicorn.service" -Encoding UTF8 -NoNewline
& $SCP_CMD -i $SSH_KEY "temp_gunicorn.service" "${RPI_USER}@${RPI_HOST}:/tmp/"
Remove-Item "temp_gunicorn.service"

# Create celery worker service
$CELERY_SERVICE = @"
[Unit]
Description=Homework Scraper Celery Worker
After=network.target redis.service

[Service]
User=$RPI_USER
Group=$RPI_USER
WorkingDirectory=/home/$RPI_USER/$BACKEND_DIR
Environment="PATH=/home/$RPI_USER/$BACKEND_DIR/venv/bin"
ExecStart=/home/$RPI_USER/$BACKEND_DIR/venv/bin/celery -A homework_scraper worker -l info

[Install]
WantedBy=multi-user.target
"@

$CELERY_SERVICE | Out-File -FilePath "temp_celery.service" -Encoding UTF8 -NoNewline
& $SCP_CMD -i $SSH_KEY "temp_celery.service" "${RPI_USER}@${RPI_HOST}:/tmp/"
Remove-Item "temp_celery.service"

# Create celery beat service
$CELERY_BEAT_SERVICE = @"
[Unit]
Description=Homework Scraper Celery Beat
After=network.target redis.service

[Service]
User=$RPI_USER
Group=$RPI_USER
WorkingDirectory=/home/$RPI_USER/$BACKEND_DIR
Environment="PATH=/home/$RPI_USER/$BACKEND_DIR/venv/bin"
ExecStart=/home/$RPI_USER/$BACKEND_DIR/venv/bin/celery -A homework_scraper beat -l info

[Install]
WantedBy=multi-user.target
"@

$CELERY_BEAT_SERVICE | Out-File -FilePath "temp_celery_beat.service" -Encoding UTF8 -NoNewline
& $SCP_CMD -i $SSH_KEY "temp_celery_beat.service" "${RPI_USER}@${RPI_HOST}:/tmp/"
Remove-Item "temp_celery_beat.service"

# Install services
& $SSH_CMD -i $SSH_KEY "${RPI_USER}@${RPI_HOST}" @"
sudo mv /tmp/temp_gunicorn.service /etc/systemd/system/homework-scraper.service && \
sudo mv /tmp/temp_celery.service /etc/systemd/system/homework-scraper-celery.service && \
sudo mv /tmp/temp_celery_beat.service /etc/systemd/system/homework-scraper-celery-beat.service && \
sudo systemctl daemon-reload
"@

# Step 8: Configure Nginx
Write-Host "`n[8/8] Configuring Nginx..." -ForegroundColor Yellow

$NGINX_CONFIG = @"
server {
    listen 80;
    server_name 172.20.10.7 api.dovydas.space;

    client_max_body_size 20M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host `$host;
        proxy_set_header X-Real-IP `$remote_addr;
        proxy_set_header X-Forwarded-For `$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto `$scheme;
        proxy_connect_timeout 120s;
        proxy_send_timeout 120s;
        proxy_read_timeout 120s;
    }

    location /static/ {
        alias /home/$RPI_USER/$BACKEND_DIR/staticfiles/;
    }

    location /media/ {
        alias /home/$RPI_USER/$BACKEND_DIR/media/;
    }
}
"@

$NGINX_CONFIG | Out-File -FilePath "temp_nginx" -Encoding UTF8 -NoNewline
& $SCP_CMD -i $SSH_KEY "temp_nginx" "${RPI_USER}@${RPI_HOST}:/tmp/"
Remove-Item "temp_nginx"

& $SSH_CMD -i $SSH_KEY "${RPI_USER}@${RPI_HOST}" @"
sudo mv /tmp/temp_nginx /etc/nginx/sites-available/homework-scraper && \
sudo ln -sf /etc/nginx/sites-available/homework-scraper /etc/nginx/sites-enabled/ && \
sudo rm -f /etc/nginx/sites-enabled/default && \
sudo nginx -t && \
sudo systemctl restart nginx && \
sudo systemctl enable nginx
"@

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "Starting Services..." -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

& $SSH_CMD -i $SSH_KEY "${RPI_USER}@${RPI_HOST}" @"
sudo systemctl start homework-scraper && \
sudo systemctl enable homework-scraper && \
sudo systemctl start homework-scraper-celery && \
sudo systemctl enable homework-scraper-celery && \
sudo systemctl start homework-scraper-celery-beat && \
sudo systemctl enable homework-scraper-celery-beat
"@

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "Deployment Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host "`nBackend is now running at:" -ForegroundColor Cyan
Write-Host "  - Local: http://172.20.10.7" -ForegroundColor White
Write-Host "  - Domain (after port forwarding): https://api.dovydas.space" -ForegroundColor White
Write-Host "`nCheck service status:" -ForegroundColor Cyan
Write-Host "  ssh -i $SSH_KEY ${RPI_USER}@${RPI_HOST} 'sudo systemctl status homework-scraper'" -ForegroundColor White
Write-Host "`nView logs:" -ForegroundColor Cyan
Write-Host "  ssh -i $SSH_KEY ${RPI_USER}@${RPI_HOST} 'sudo journalctl -u homework-scraper -f'" -ForegroundColor White
