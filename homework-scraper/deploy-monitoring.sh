#!/bin/bash
# Deploy monitoring feature to RPI server

echo "🚀 Deploying Server Monitoring Feature..."
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Navigate to project directory
cd /home/dovydukas/homework-scraper || exit 1

echo -e "${YELLOW}📥 Pulling latest changes...${NC}"
git pull origin main

# Activate virtual environment
echo -e "${YELLOW}🐍 Activating virtual environment...${NC}"
source venv/bin/activate

# Install/update dependencies
echo -e "${YELLOW}📦 Installing dependencies...${NC}"
pip install -r backend/requirements.txt --quiet

# Check if monitoring app is in settings
echo -e "${YELLOW}⚙️  Checking Django settings...${NC}"
if grep -q "'monitoring'" backend/homework_scraper/settings.py; then
    echo -e "${GREEN}✓ Monitoring app already in settings${NC}"
else
    echo -e "${YELLOW}⚠️  Adding monitoring app to settings...${NC}"
    # Backup settings
    cp backend/homework_scraper/settings.py backend/homework_scraper/settings.py.backup
    
    # Add monitoring to INSTALLED_APPS (this is a simple append, adjust as needed)
    sed -i "/INSTALLED_APPS = \[/,/\]/s/'tasks',/'tasks',\n    'monitoring',/" backend/homework_scraper/settings.py
    
    if grep -q "'monitoring'" backend/homework_scraper/settings.py; then
        echo -e "${GREEN}✓ Monitoring app added to settings${NC}"
    else
        echo -e "${RED}✗ Failed to add monitoring app. Please add manually.${NC}"
    fi
fi

# Create log directory
echo -e "${YELLOW}📁 Setting up log directory...${NC}"
sudo mkdir -p /var/log/homework-scraper
sudo chown -R dovydukas:dovydukas /var/log/homework-scraper
sudo chmod -R 755 /var/log/homework-scraper

# Restart services
echo -e "${YELLOW}🔄 Restarting services...${NC}"
sudo systemctl restart homework-scraper.service
sleep 2

# Check service status
echo ""
echo -e "${YELLOW}📊 Checking service status...${NC}"
if systemctl is-active --quiet homework-scraper.service; then
    echo -e "${GREEN}✓ homework-scraper.service is running${NC}"
else
    echo -e "${RED}✗ homework-scraper.service is not running${NC}"
    echo "Run: sudo systemctl status homework-scraper.service"
fi

if systemctl is-active --quiet homework-scraper-celery.service; then
    echo -e "${GREEN}✓ homework-scraper-celery.service is running${NC}"
else
    echo -e "${YELLOW}⚠️  homework-scraper-celery.service is not running${NC}"
fi

if systemctl is-active --quiet homework-scraper-celery-beat.service; then
    echo -e "${GREEN}✓ homework-scraper-celery-beat.service is running${NC}"
else
    echo -e "${YELLOW}⚠️  homework-scraper-celery-beat.service is not running${NC}"
fi

# Test API endpoint
echo ""
echo -e "${YELLOW}🧪 Testing monitoring API...${NC}"
API_RESPONSE=$(curl -s http://localhost:8000/api/monitoring/)
if echo "$API_RESPONSE" | grep -q "success"; then
    echo -e "${GREEN}✓ Monitoring API is responding${NC}"
    echo "Response: $API_RESPONSE" | head -c 100
    echo "..."
else
    echo -e "${RED}✗ Monitoring API test failed${NC}"
    echo "Response: $API_RESPONSE"
fi

echo ""
echo -e "${GREEN}✅ Deployment complete!${NC}"
echo ""
echo "📝 Next steps:"
echo "1. Visit: https://dovydas.space/logs"
echo "2. Make sure you're logged in with Google"
echo "3. Check the monitoring page"
echo ""
echo "🔍 Useful commands:"
echo "  sudo systemctl status homework-scraper.service"
echo "  journalctl -u homework-scraper.service -f"
echo "  curl http://localhost:8000/api/monitoring/"
echo ""
