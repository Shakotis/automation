#!/bin/bash
# Deploy RISC implementation to Raspberry Pi

set -e

echo "=========================================="
echo "RISC (Cross-Account Protection) Deployment"
echo "=========================================="
echo ""

# Configuration
RPI_USER="dovydukas"
RPI_HOST="192.168.1.33"
BACKEND_DIR="/home/dovydukas/homework-scraper-backend"
SERVICE_NAME="homework-scraper"

echo "Step 1: Transferring RISC files to RPI..."
scp -r backend/risc "${RPI_USER}@${RPI_HOST}:${BACKEND_DIR}/"

echo ""
echo "Step 2: Installing Python dependencies..."
ssh "${RPI_USER}@${RPI_HOST}" << 'EOF'
cd /home/dovydukas/homework-scraper-backend
source venv/bin/activate
pip install PyJWT>=2.8.0 cryptography>=41.0.0 requests>=2.31.0 google-auth>=2.23.0
EOF

echo ""
echo "Step 3: Running migrations..."
ssh "${RPI_USER}@${RPI_HOST}" << 'EOF'
cd /home/dovydukas/homework-scraper-backend
source venv/bin/activate
python manage.py makemigrations risc
python manage.py migrate risc
EOF

echo ""
echo "Step 4: Collecting static files..."
ssh "${RPI_USER}@${RPI_HOST}" << 'EOF'
cd /home/dovydukas/homework-scraper-backend
source venv/bin/activate
python manage.py collectstatic --noinput
EOF

echo ""
echo "Step 5: Restarting backend service..."
ssh "${RPI_USER}@${RPI_HOST}" "sudo systemctl restart ${SERVICE_NAME}.service"

echo ""
echo "Step 6: Checking service status..."
ssh "${RPI_USER}@${RPI_HOST}" "sudo systemctl status ${SERVICE_NAME}.service --no-pager -l"

echo ""
echo "=========================================="
echo "✅ RISC Deployment Complete!"
echo "=========================================="
echo ""
echo "Next Steps:"
echo "1. Add 'risc' to INSTALLED_APPS in settings.py"
echo "2. Add path('risc/', include('risc.urls')) to main urls.py"
echo "3. Set RISC_RECEIVER_URL in settings.py"
echo "4. Create RISCConfiguration in Django admin"
echo "5. Setup Google Cloud service account with RISC Configuration Admin role"
echo "6. Run: python manage.py configure_risc --service-account /path/to/sa.json --receiver-url https://api.dovydas.space/risc/receiver/"
echo ""
echo "Test receiver endpoint:"
echo "  curl -X POST https://api.dovydas.space/risc/receiver/ -H 'Content-Type: application/json' -d '{\"test\":\"data\"}'"
echo ""
echo "Check RISC status:"
echo "  curl https://api.dovydas.space/risc/status/"
echo ""
