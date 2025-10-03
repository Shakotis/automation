# Troubleshooting Guide

## Common Issues and Solutions

### ❌ "Failed to fetch" Errors in Browser Console

**Symptom**: Console shows `[API] Unexpected error: "Failed to fetch"` when loading the page.

**Cause**: The application tries to check if you're logged in when the page loads. If you're not logged in, this is **expected behavior** and not an error.

**Solution**: These errors are now suppressed for auth check endpoints. You can safely ignore them.

---

### ❌ "Sync failed: Please make sure you are logged in"

**Symptom**: Trying to scrape homework or sync to Google Tasks fails with this message.

**Cause**: You haven't signed in with Google yet.

**Solution**: 
1. Click the "Sign in with Google" button on the homepage
2. Complete the Google OAuth flow
3. Grant permissions for Google Tasks and Calendar
4. You'll be redirected back to the app

---

### ❌ Google Sign-In Button Not Working

**Symptom**: Clicking "Sign in with Google" shows an error or nothing happens.

**Troubleshooting**:

1. **Check both servers are running**:
   ```powershell
   # In PowerShell
   try { Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/auth/sites/" } catch { "Backend NOT running" }
   try { Invoke-RestMethod -Uri "http://localhost:3000/api/auth/sites/" } catch { "Frontend NOT running" }
   ```

2. **If servers aren't running**, start them:
   ```powershell
   cd C:\Users\Dovydukas\Documents\GitHub\automation\homework-scraper
   .\start-servers.ps1
   ```

3. **Hard refresh the browser**: Press `Ctrl + Shift + R` (Windows) or `Cmd + Shift + R` (Mac)

4. **Clear browser cache**: In DevTools (F12) → Network tab → Check "Disable cache"

5. **Test in Incognito/Private mode** to rule out extension conflicts

6. **Manually test the endpoint** in browser console (F12):
   ```javascript
   fetch('/api/auth/google/login/')
     .then(r => r.json())
     .then(data => console.log('✓ Success:', data))
     .catch(err => console.error('✗ Error:', err))
   ```

---

### ❌ Django Backend Not Running

**Symptoms**:
- PowerShell test shows "Backend NOT running"
- Browser shows connection errors

**Solution**:
```powershell
cd C:\Users\Dovydukas\Documents\GitHub\automation\homework-scraper\backend
& C:/Users/Dovydukas/Documents/GitHub/automation/.venv/Scripts/Activate.ps1
python manage.py runserver
```

---

### ❌ Next.js Frontend Not Running

**Symptoms**:
- PowerShell test shows "Frontend NOT running"  
- Browser shows "This site can't be reached"

**Solution**:
```powershell
cd C:\Users\Dovydukas\Documents\GitHub\automation\homework-scraper\frontend
$env:PATH = "C:\Program Files\nodejs;" + $env:PATH
npm run dev
```

---

### ❌ "ERR_TOO_MANY_REDIRECTS" Error

**Symptom**: Browser shows redirect loop error.

**Cause**: Django REST Framework's authentication was causing redirect loops.

**Solution**: This has been fixed by adding `authentication_classes = []` to public API views. If you still see this:
1. Pull the latest code
2. Restart the Django backend

---

## Quick Health Check

Run this in PowerShell to verify all services:

```powershell
Write-Host "`n=== Homework Scraper Health Check ===" -ForegroundColor Cyan

# Check Backend
Write-Host "`n1. Django Backend (http://127.0.0.1:8000)" -ForegroundColor Yellow
try {
    $backend = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/auth/sites/" -ErrorAction Stop
    Write-Host "   ✓ Backend is running - $($backend.available_sites.Count) sites available" -ForegroundColor Green
} catch {
    Write-Host "   ✗ Backend is NOT running" -ForegroundColor Red
    Write-Host "   Run: .\start-servers.ps1" -ForegroundColor Yellow
}

# Check Frontend
Write-Host "`n2. Next.js Frontend (http://localhost:3000)" -ForegroundColor Yellow
try {
    $frontend = Invoke-RestMethod -Uri "http://localhost:3000/api/auth/sites/" -ErrorAction Stop
    Write-Host "   ✓ Frontend is running" -ForegroundColor Green
} catch {
    Write-Host "   ✗ Frontend is NOT running" -ForegroundColor Red
    Write-Host "   Run: .\start-servers.ps1" -ForegroundColor Yellow
}

# Check Auth Endpoint
Write-Host "`n3. Google Auth Endpoint" -ForegroundColor Yellow
try {
    $auth = Invoke-RestMethod -Uri "http://localhost:3000/api/auth/google/login/" -ErrorAction Stop
    Write-Host "   ✓ Auth endpoint working" -ForegroundColor Green
} catch {
    Write-Host "   ✗ Auth endpoint failed: $_" -ForegroundColor Red
}

Write-Host "`n=== Health Check Complete ===" -ForegroundColor Cyan
Write-Host ""
```

---

## Browser Compatibility

**Recommended Browsers**:
- ✅ Google Chrome (latest)
- ✅ Microsoft Edge (latest)
- ✅ Firefox (latest)

**Known Issues**:
- Some ad blockers may interfere with OAuth flows
- Privacy extensions may block cookies (required for sessions)

---

## Getting Help

If you're still experiencing issues:

1. **Check the logs**:
   - Django terminal: Look for errors in red
   - Next.js terminal: Look for compilation errors
   - Browser console (F12): Check for JavaScript errors

2. **Restart everything**:
   ```powershell
   # Stop all servers (close terminal windows)
   # Then restart:
   cd C:\Users\Dovydukas\Documents\GitHub\automation\homework-scraper
   .\start-servers.ps1
   ```

3. **Clear all caches**:
   - Browser cache (Ctrl + Shift + Delete)
   - Next.js cache: Delete `frontend/.next` folder
   - Django sessions: Delete `backend/sessions` folder contents

4. **Check GitHub Issues**: https://github.com/Shakotis/automation/issues
