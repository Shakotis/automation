# Recent Improvements & Fixes

## 🎯 Issues Fixed

### 1. **"Failed to Fetch" Errors** ✅
**Problem**: Frontend couldn't connect to backend API, showing "Failed to fetch" and "Unexpected token '<'" errors.

**Solution**:
- Added API proxy configuration in `next.config.js` to forward `/api/*` requests to Django backend
- Added `credentials: 'include'` to all fetch calls to properly send authentication cookies
- Created `start-servers.ps1` script to ensure both servers start with correct configuration

**Files Changed**:
- `frontend/next.config.js` - Added rewrites for API proxy
- `frontend/app/dashboard/page.tsx` - Added `credentials: 'include'` to all fetch calls
- `frontend/app/settings/page.tsx` - Updated API calls to use proxy

---

### 2. **Improved OAuth & Credential Flow** ✅
**Problem**: Users had to authenticate twice - once for Google OAuth, then separately add site credentials in settings.

**Solution**:
- Enhanced OAuth callback to check for credentials automatically
- Redirects users to appropriate page based on their status:
  - **First-time users** → Onboarding flow
  - **Users without credentials** → Settings with setup prompt (`/settings?setup=credentials`)
  - **Users with verified credentials** → Dashboard
- Added visual prompt in Settings when redirected from OAuth for credential setup

**Files Changed**:
- `backend/authentication/views.py` - Enhanced `GoogleOAuthCallbackView._handle_oauth_callback()`
- `frontend/app/settings/page.tsx` - Added `showCredentialsPrompt` banner

**User Experience**:
1. User clicks "Sign in with Google"
2. Completes Google OAuth
3. System checks if they have site credentials
4. If not → Redirected to Settings with helpful prompt: "🔐 Setup Your Site Credentials"
5. User adds Manodienynas/Eduka credentials once
6. Credentials are encrypted and stored securely
7. Ready to scrape!

---

### 3. **Enhanced Scrape Button** ✅
**Problem**: Scrape button didn't provide clear feedback or error messages.

**Solution**:
- Added detailed success messages showing scraped count and sync status
- Added authentication check with redirect to Google OAuth if not signed in
- Added credential error detection with prompt to go to Settings
- Added network error handling with helpful message

**Files Changed**:
- `frontend/app/dashboard/page.tsx` - Enhanced `handleScrapeNow()` function

**Error Messages**:
- ✅ Success: "Successfully scraped 5 homework items and synced 5 to Google Tasks!"
- ⚠️ Not authenticated: "Please sign in with Google to scrape homework" (redirects to /auth/google)
- ❌ Credential error: "Would you like to go to Settings to add/verify your credentials?" (confirmation dialog)
- ❌ Network error: "Network error: Could not connect to the server. Please ensure both servers are running."

---

### 4. **Google Tasks Title Format Customization** ✅
**Problem**: Users wanted control over what appears as the task title in Google Tasks.

**Solution**:
- Added `google_tasks_title_format` field to `UserScrapingPreferences` model
- Two options:
  - **Task Title** (default): Shows homework title in Google Tasks (e.g., "Complete math worksheet")
  - **Subject Name**: Shows subject in Google Tasks (e.g., "Mathematics")
- Updated Google Tasks sync to respect user preference
- Added UI dropdown in Settings page under "Google Tasks Integration"

**Files Changed**:
- `backend/scraper/models.py` - Added `google_tasks_title_format` field
- `backend/scraper/views.py` - Updated preferences API to include new field
- `backend/tasks/services.py` - Updated `create_task_from_homework()` to use preference
- `frontend/app/settings/page.tsx` - Added Select dropdown for title format
- `backend/scraper/migrations/0003_*.py` - Database migration

**Usage**:
1. Go to Settings
2. Scroll to "Google Tasks Integration"
3. Select preferred title format from dropdown
4. Click "Save Settings"
5. Next homework sync will use the selected format

---

### 5. **Server Startup Script** ✅
**Problem**: Complex process to start both Django and Next.js servers correctly.

**Solution**:
- Created `start-servers.ps1` (Windows PowerShell script)
- Created `start-servers.sh` (Linux/Mac bash script)
- Created `START_SERVERS.md` documentation

**Script Features**:
- ✅ Automatically stops old/stale Node.js processes
- ✅ Starts Django backend on port 8000 in new window
- ✅ Starts Next.js frontend on port 3000 in new window
- ✅ Shows clear status messages and URLs
- ✅ Configures proper Node.js PATH

**Usage**:
```powershell
# Windows
cd homework-scraper
.\start-servers.ps1

# Linux/Mac
cd homework-scraper
chmod +x start-servers.sh
./start-servers.sh
```

---

## 🔐 Credential Storage & Security

### How It Works
1. **Google OAuth**: User authenticates with Google (one-time setup)
2. **Site Credentials**: User enters Manodienynas/Eduka credentials in Settings
3. **Encryption**: Credentials are encrypted before storage
4. **Session Persistence**: Authentication persists across page reloads using secure cookies
5. **Verification**: Credentials are verified by actually logging into the sites
6. **Auto-Scraping**: Verified credentials are used automatically for scraping

### Storage Locations
- **Google OAuth Tokens**: `authentication_googleoauth` table
- **Site Credentials**: `authentication_usercredential` table (encrypted)
- **Session Data**: Django sessions (secure cookies)
- **Preferences**: `scraper_userscrapingpreferences` table

### Security Features
- ✅ Encrypted credential storage
- ✅ CSRF protection
- ✅ Secure session cookies
- ✅ CORS configuration for localhost only
- ✅ Verification system to ensure credentials work

---

## 📝 API Endpoints

### Authentication
- `GET /api/auth/google/login/` - Get Google OAuth URL
- `GET /api/auth/google/callback/` - Handle OAuth callback
- `GET /api/auth/user/` - Get current user info
- `POST /api/auth/credentials/` - Save site credentials
- `GET /api/auth/credentials/` - Get user credentials
- `POST /api/auth/verify-credentials/` - Verify credentials
- `POST /api/auth/logout/` - Logout user

### Scraper
- `GET /api/scraper/homework/` - List homework (supports `?status=upcoming|overdue|completed`)
- `POST /api/scraper/homework/scrape/` - Trigger manual scrape
- `POST /api/scraper/homework/{id}/complete/` - Mark homework complete/incomplete
- `GET /api/scraper/stats/` - Get dashboard statistics
- `GET /api/scraper/preferences/` - Get user preferences
- `PUT /api/scraper/preferences/` - Update user preferences

### Google Tasks
- `POST /api/scraper/homework/sync-google-tasks/` - Manual sync to Google Tasks

---

## 🚀 Next Steps

### Recommended Workflow
1. **Start Servers**: Run `.\start-servers.ps1`
2. **Sign in**: Go to http://localhost:3000 and click "Login with Google"
3. **Setup Credentials**: Add your Manodienynas/Eduka credentials in Settings
4. **Verify Credentials**: Click "Verify" button for each site
5. **Configure Preferences**: 
   - Enable/disable specific sites
   - Set scraping frequency
   - Choose Google Tasks title format
6. **Start Scraping**: Click "Scrape Now" in Dashboard
7. **Manage Homework**: Use filters, mark tasks complete, view stats

### Future Enhancements
- [ ] Automatic scraping on schedule (Celery integration)
- [ ] Email notifications for new homework
- [ ] Calendar integration for due dates
- [ ] Mobile app
- [ ] Multi-language support
- [ ] Homework templates/recurring assignments
- [ ] Study time tracking

---

## 🐛 Troubleshooting

### Servers Won't Start
```powershell
# Check if ports are in use
netstat -ano | findstr :3000
netstat -ano | findstr :8000

# Kill processes if needed
taskkill /PID <PID> /F
```

### "Failed to Fetch" Errors
1. Ensure both servers are running (check terminal windows)
2. Verify Next.js is on port 3000 (not 3001)
3. Verify Django is on port 8000
4. Check browser console for detailed error messages
5. Try clearing browser cache and cookies

### OAuth Redirects to Wrong URL
Check `next.config.js` has correct port configuration and restart Next.js server.

### Scrape Button Doesn't Work
1. Ensure you're signed in with Google
2. Check that you have credentials added in Settings
3. Verify credentials by clicking "Verify" button
4. Check Django terminal for error messages

### Database Errors
```bash
cd backend
python manage.py migrate
```

---

## 📚 Technical Details

### Technology Stack
- **Frontend**: Next.js 15.5.4 with TypeScript, HeroUI components
- **Backend**: Django 5.2.6 with REST Framework
- **Database**: SQLite (development)
- **Web Scraping**: Selenium with headless Chrome
- **Authentication**: Google OAuth 2.0
- **Task Management**: Google Tasks API

### Project Structure
```
homework-scraper/
├── backend/
│   ├── authentication/      # OAuth & credential management
│   ├── scraper/             # Homework scraping logic
│   ├── tasks/               # Google Tasks integration
│   └── homework_scraper/    # Django settings
├── frontend/
│   ├── app/                 # Next.js pages
│   ├── components/          # Reusable components
│   └── lib/                 # API utilities
├── start-servers.ps1        # Windows startup script
├── start-servers.sh         # Linux/Mac startup script
└── START_SERVERS.md         # Documentation
```

### Environment Variables
Create `.env` file in `backend/` directory:
```env
SECRET_KEY=your-secret-key
DEBUG=True
GOOGLE_OAUTH2_CLIENT_ID=your-client-id
GOOGLE_OAUTH2_CLIENT_SECRET=your-client-secret
SUPABASE_URL=your-supabase-url
SUPABASE_KEY=your-supabase-key
```

---

## ✅ Testing Checklist

- [ ] Both servers start successfully with script
- [ ] Google OAuth login works
- [ ] Credentials can be added and verified
- [ ] Scrape button fetches real homework
- [ ] Homework appears in dashboard with correct data
- [ ] Filters work (all, upcoming, overdue, completed)
- [ ] Mark complete/incomplete works
- [ ] Google Tasks sync works
- [ ] Google Tasks title format preference works
- [ ] Settings save correctly
- [ ] Session persists across page reloads
- [ ] Error messages are clear and helpful

---

**Last Updated**: October 1, 2025
**Version**: 2.0.0
