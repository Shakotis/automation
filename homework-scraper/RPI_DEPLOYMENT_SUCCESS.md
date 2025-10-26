# RPI Backend Deployment - Complete! ✅

## 🎉 Deployment Status: SUCCESS!

Your Raspberry Pi 3B+ is now running as your backend server!

### ✅ What's Running

- **Django Backend**: Running on Gunicorn (port 8000)
- **Nginx**: Reverse proxy and web server (port 80)
- **Redis**: Message broker for Celery
- **Celery Worker**: Background task processor
- **Celery Beat**: Scheduled task manager

### 🌐 Access Points

- **Local Network**: `http://172.20.10.7/api/`
- **After Port Forwarding**: `https://api.dovydas.space/api/`
- **Frontend**: `https://nd.dovydas.space`

### 🔧 Testing the API

Test from any computer on your network:
```powershell
Invoke-WebRequest -Uri "http://172.20.10.7/api/test/"
```

Expected response:
```json
{"status": "success", "message": "Backend API is working!", "django_running": true, "google_oauth_configured": true}
```

## 📝 Configuration Needed

### 1. Supabase Configuration (IMPORTANT!)

Your backend is currently using placeholder Supabase credentials. To fix:

```bash
# SSH into RPI
ssh -i C:\Users\Dovydukas\.ssh\rpi_3 dovydukas@172.20.10.7

# Edit the .env file
cd homework-scraper-backend
nano .env
```

Update these lines:
```env
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-anon-key-here
```

**Where to find these:**
1. Go to your Supabase dashboard: https://supabase.com/dashboard
2. Select your project
3. Go to **Settings** → **API**
4. Copy:
   - **Project URL** → Use for `SUPABASE_URL`
   - **anon/public key** → Use for `SUPABASE_KEY`

After updating, restart the service:
```bash
sudo systemctl restart homework-scraper
```

### 2. Port Forwarding Setup

To make your API accessible at `api.dovydas.space`:

1. **On your router:**
   - Forward **external port 443** → **RPI 172.20.10.7:80**
   - Or forward **external port 80** → **RPI 172.20.10.7:80**

2. **DNS Configuration:**
   - Add an A record: `api.dovydas.space` → Your public IP

3. **SSL Certificate (Recommended):**
   ```bash
   # On RPI
   sudo apt-get install certbot python3-certbot-nginx
   sudo certbot --nginx -d api.dovydas.space
   ```

## 🛠️ Management Commands

### Service Management

```bash
# Check status
sudo systemctl status homework-scraper
sudo systemctl status homework-scraper-celery
sudo systemctl status homework-scraper-celery-beat

# Restart services
sudo systemctl restart homework-scraper
sudo systemctl restart homework-scraper-celery
sudo systemctl restart homework-scraper-celery-beat

# View logs
sudo journalctl -u homework-scraper -f
sudo journalctl -u homework-scraper-celery -f
```

### Updating the Backend

When you make changes to the code:

```bash
# On your Windows machine
cd c:\Users\Dovydukas\Documents\GitHub\automation\homework-scraper
scp -i C:\Users\Dovydukas\.ssh\rpi_3 -r backend\* dovydukas@172.20.10.7:homework-scraper-backend/

# On RPI
ssh -i C:\Users\Dovydukas\.ssh\rpi_3 dovydukas@172.20.10.7
cd homework-scraper-backend
source venv/bin/activate
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart homework-scraper
```

Or use the quick update script:

```powershell
# Create update-rpi-backend.ps1
& "C:\Windows\System32\OpenSSH\scp.exe" -i C:\Users\Dovydukas\.ssh\rpi_3 -r backend\* dovydukas@172.20.10.7:homework-scraper-backend/
& "C:\Windows\System32\OpenSSH\ssh.exe" -i C:\Users\Dovydukas\.ssh\rpi_3 dovydukas@172.20.10.7 "cd homework-scraper-backend && source venv/bin/activate && python manage.py migrate && python manage.py collectstatic --noinput && sudo systemctl restart homework-scraper"
```

### Database Management

```bash
# Create Django superuser
cd homework-scraper-backend
source venv/bin/activate
python manage.py createsuperuser

# Access admin panel
# http://172.20.10.7/admin/
```

### Monitor Resources

```bash
# Check system resources
free -h              # Memory usage
df -h                # Disk space
htop                 # CPU and process monitor
```

## 🔐 Security Considerations

1. **Change Django SECRET_KEY** in `.env`
2. **Enable HTTPS** with Let's Encrypt (certbot)
3. **Configure firewall:**
   ```bash
   sudo apt-get install ufw
   sudo ufw allow 22    # SSH
   sudo ufw allow 80    # HTTP
   sudo ufw allow 443   # HTTPS
   sudo ufw enable
   ```

4. **Set up regular backups:**
   ```bash
   # Backup database
   cd ~/homework-scraper-backend
   sqlite3 db.sqlite3 ".backup backup-$(date +%Y%m%d).db"
   ```

## 📊 Current Configuration

- **Python**: 3.13.5
- **Django**: 5.2.7
- **Database**: SQLite (located at `homework-scraper-backend/db.sqlite3`)
- **Static Files**: `homework-scraper-backend/staticfiles/`
- **Workers**: 2 Gunicorn workers
- **Encryption Key**: ✅ Generated and configured

## 🔗 Frontend Integration

Your frontend at `https://nd.dovydas.space` is already configured to connect to the backend.

**Update frontend environment:**
```env
NEXT_PUBLIC_API_URL=https://api.dovydas.space/api
```

## 🐛 Troubleshooting

### Backend not responding
```bash
sudo systemctl status homework-scraper
sudo journalctl -u homework-scraper -n 50
```

### Celery tasks not running
```bash
sudo systemctl status homework-scraper-celery
sudo systemctl status redis-server
```

### Permission issues
```bash
cd ~/homework-scraper-backend
sudo chown -R dovydukas:dovydukas .
```

### Out of memory
```bash
# Increase swap space
sudo dd if=/dev/zero of=/swapfile bs=1M count=2048
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

## 📞 Quick Reference

**SSH Command:**
```powershell
ssh -i C:\Users\Dovydukas\.ssh\rpi_3 dovydukas@172.20.10.7
```

**API Test:**
```powershell
Invoke-WebRequest -Uri "http://172.20.10.7/api/test/"
```

**Restart All Services:**
```bash
sudo systemctl restart homework-scraper homework-scraper-celery homework-scraper-celery-beat nginx
```

## 🎯 Next Steps

1. ✅ ~~Deploy backend to RPI~~ **DONE!**
2. ⚠️  Configure Supabase credentials
3. 🔄 Set up port forwarding for api.dovydas.space
4. 🔒 Install SSL certificate with certbot
5. 👤 Create Django admin user
6. 🧪 Test full integration with frontend
7. 📱 Test homework scraping functionality

---

**Congratulations! Your Raspberry Pi is now a fully functional backend server! 🎉**
