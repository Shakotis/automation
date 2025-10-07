# 🔧 Local Development Quick Start

## Issue: Frontend Can't Connect to Backend

Your frontend (Next.js) is running at `http://localhost:3000`  
But it's trying to connect to backend at `http://localhost:8000` which isn't running.

## ✅ Solution: Start the Django Backend

### Option 1: Use the Start Script (Recommended)
```powershell
cd W:\automation\homework-scraper
.\start-servers.ps1
```

This will start both frontend and backend automatically.

### Option 2: Start Backend Manually

**Terminal 1 - Backend:**
```powershell
cd W:\automation\homework-scraper\backend
python manage.py runserver 8000
```

**Terminal 2 - Frontend (if not already running):**
```powershell
cd W:\automation\homework-scraper\frontend
npm run dev
```

## 🌐 Access Your App

Once both servers are running:
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000/api
- **Django Admin:** http://localhost:8000/admin

## ⚠️ Important Notes for Local Development

### 1. Database Configuration
For local development, make sure you have a local database or point to Supabase:

**Create `.env` file in backend folder:**
```env
# For local SQLite (easiest)
DATABASE_URL=sqlite:///db.sqlite3

# OR for Supabase (if you want to use production DB locally)
DATABASE_URL=postgresql://postgres.kcixuytszyzgvcybxyym:3BH6CyUl5OpWDqtD@aws-0-eu-central-1.pooler.supabase.com:6543/postgres

# Other settings
DEBUG=True
SECRET_KEY=your-dev-secret-key-change-this
ALLOWED_HOSTS=localhost,127.0.0.1
```

### 2. Run Migrations
First time setup:
```powershell
cd W:\automation\homework-scraper\backend
python manage.py migrate
python manage.py createsuperuser
```

### 3. Google OAuth Configuration
For local development, you'll need to:
1. Update Google OAuth redirect URI to include `http://localhost:8000`
2. Set environment variables for Google credentials

---

## 🚀 For Production Deployment

This is a separate issue - see `FIX_CHECKLIST_NOW.md` for deployment fixes.

---

**Current Error Explained:**
```
Failed to load resource: net::ERR_CONNECTION_REFUSED
localhost:8000/api/auth/user
```

This means: Frontend is working ✅, Backend is not running ❌

**Fix:** Start Django backend at `localhost:8000`
