# Homework Scraper - Quick Start

## Starting Both Servers

### Windows (PowerShell)
```powershell
.\start-servers.ps1
```

### Linux/Mac (Bash)
```bash
chmod +x start-servers.sh
./start-servers.sh
```

## Manual Start

### Backend (Django)
```bash
cd backend
# Activate virtual environment (Windows)
..\..\.venv\Scripts\Activate.ps1
# Or (Linux/Mac)
source ../../.venv/bin/activate

python manage.py runserver
```

### Frontend (Next.js)
```bash
cd frontend
npm run dev
```

## Access Points

- **Frontend**: http://localhost:3000
- **Backend API**: http://127.0.0.1:8000
- **Django Admin**: http://127.0.0.1:8000/admin

## Stopping Servers

- In the server terminal windows, press `Ctrl+C`
- Or close the terminal windows

## Features

### Dashboard
- View all homework assignments
- Filter by status (all, upcoming, overdue, completed)
- Mark tasks as complete/incomplete
- Auto-sync with Google Tasks

### Settings
- Configure credentials for Manodienynas and Eduka
- Set scraping frequency
- **NEW**: Choose Google Tasks title format (Subject Name or Task Title)
- Connect Google account for Tasks sync

### Scraping
- Manual scrape trigger in dashboard
- Automatic sync to Google Tasks (if configured)
- Support for Manodienynas.lt and Eduka.lt

## Troubleshooting

### Port Already in Use
If you get "port already in use" errors:

**Windows:**
```powershell
# Find and kill process on port 3000 (Next.js)
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# Find and kill process on port 8000 (Django)
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

**Linux/Mac:**
```bash
# Kill Next.js (port 3000)
lsof -ti:3000 | xargs kill -9

# Kill Django (port 8000)
lsof -ti:8000 | xargs kill -9
```

### Failed to Fetch Errors
Make sure both servers are running:
1. Backend must be on port 8000
2. Frontend must be on port 3000
3. API proxy is configured in `next.config.js` (already done)

### Database Issues
```bash
cd backend
python manage.py migrate
```

### Missing Dependencies
```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```
