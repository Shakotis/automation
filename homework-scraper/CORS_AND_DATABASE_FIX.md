# CORS and Database Connection Fix

## Issues Identified

### 1. CORS Error
```
Access to fetch at 'https://api.dovydas.space/api/auth/user' from origin 'https://nd.dovydas.space' 
has been blocked by CORS policy: No 'Access-Control-Allow-Origin' header is present on the requested resource.
```

### 2. Database Connection Error
```
psycopg2.OperationalError: connection to server at "aws-1-eu-north-1.pooler.supabase.com" (51.21.18.29), 
port 5432 failed: Connection refused
```

## Solutions Applied

### ✅ Fixed CORS Configuration

**Changes made to `backend/homework_scraper/settings_production.py`:**

1. **Added all frontend domains to CORS_ALLOWED_ORIGINS:**
   ```python
   CORS_ALLOWED_ORIGINS = [
       'https://nd.dovydas.space',      # Main frontend
       'https://api.dovydas.space',     # API domain
       'https://dovydas.space',         # Root domain
       'https://www.dovydas.space'      # WWW subdomain
   ]
   ```

2. **Added cookie header to CORS_ALLOW_HEADERS:**
   ```python
   CORS_ALLOW_HEADERS = [
       # ... other headers
       'cookie',  # Important for session cookies
   ]
   ```

3. **Added CORS_EXPOSE_HEADERS:**
   ```python
   CORS_EXPOSE_HEADERS = [
       'content-type',
       'x-csrftoken',
   ]
   ```

4. **Configured session cookies for cross-domain:**
   ```python
   SESSION_COOKIE_SECURE = True
   SESSION_COOKIE_SAMESITE = 'None'
   SESSION_COOKIE_HTTPONLY = False
   SESSION_COOKIE_DOMAIN = '.dovydas.space'  # Share across subdomains
   ```

### ⚠️ Database Connection Issue - ACTION REQUIRED

**The current error shows:**
- Your DATABASE_URL is using port **5432** (Direct connection)
- Connection is being **refused** by Supabase

**Why this happens:**
- Port 5432 is for direct connections to Supabase PostgreSQL
- Direct connections have a limit (typically 20-50 connections)
- When the limit is reached, new connections are refused
- This is especially problematic for web applications

**SOLUTION - Use Session Pooler (Port 6543):**

#### Step 1: Get the correct connection string from Supabase

1. Go to your Supabase Dashboard
2. Navigate to: **Settings** → **Database**
3. Scroll to **Connection string** section
4. Select **"Session mode"** (NOT Transaction mode)
5. Copy the connection string - it should look like:
   ```
   postgresql://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres
   ```
   
   **Important:** Notice port **6543** (not 5432)

#### Step 2: Update Render Environment Variables

1. Go to Render Dashboard: https://dashboard.render.com/
2. Select your backend service (homework-scraper backend)
3. Click on **"Environment"** tab
4. Find the **DATABASE_URL** variable
5. Click **Edit**
6. Replace the value with your Supabase Session Pooler connection string
7. Click **"Save Changes"**
8. Your service will automatically redeploy

#### Step 3: Verify the fix

After redeployment:
1. Check Render logs for: `✓ Using port 6543 (Session pooler - recommended for Django)`
2. Try accessing your frontend at https://nd.dovydas.space
3. The API calls should now work without connection errors

## Why Port 6543 vs 5432?

| Port | Mode | Description | Use Case |
|------|------|-------------|----------|
| **5432** | Direct | Direct PostgreSQL connection | Development, migrations, admin tasks |
| **6543** | Session Pooler | pgBouncer connection pooler | **Production web apps** ✅ |
| 6543 | Transaction Pooler | Limited transaction support | Serverless functions |

**For Django/web applications, always use port 6543 (Session mode)**

## Environment Variables to Set on Render

Make sure these are set in your Render Dashboard → Environment:

```bash
# Required
DATABASE_URL=postgresql://postgres.[ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres
SECRET_KEY=your-secret-key-here
DJANGO_SETTINGS_MODULE=homework_scraper.settings_production

# Optional but recommended
CORS_ALLOWED_ORIGINS=https://nd.dovydas.space,https://api.dovydas.space,https://dovydas.space
CSRF_TRUSTED_ORIGINS=https://nd.dovydas.space,https://api.dovydas.space
FRONTEND_URL=https://nd.dovydas.space
ALLOWED_HOSTS=api.dovydas.space,.dovydas.space,.onrender.com
```

## Testing the Fix

### 1. Test CORS
Open browser console on https://nd.dovydas.space and check:
```javascript
// Should NOT see CORS errors anymore
fetch('https://api.dovydas.space/api/auth/user', {
  credentials: 'include'
})
```

### 2. Test Database Connection
Check Render logs for:
```
✓ Connecting to Supabase: aws-0-eu-north-1.pooler.supabase.com:6543
✓ Using port 6543 (Session pooler - recommended for Django)
```

### 3. Test Full Flow
1. Visit https://nd.dovydas.space
2. Log in with Google OAuth
3. Navigate to settings
4. Verify credentials load without errors

## Additional Security Notes

The changes maintain security while fixing CORS:
- `CORS_ALLOW_CREDENTIALS = True` allows cookies
- `SESSION_COOKIE_SECURE = True` requires HTTPS
- `SESSION_COOKIE_SAMESITE = 'None'` allows cross-site cookies (required for api.dovydas.space ← nd.dovydas.space)
- `SESSION_COOKIE_DOMAIN = '.dovydas.space'` allows cookie sharing between subdomains
- CORS is still restricted to specific origins (not `CORS_ALLOW_ALL_ORIGINS`)

## Still Having Issues?

### CORS still not working:
1. Clear browser cache and cookies
2. Verify environment variables are set on Render
3. Check Render logs for CORS configuration
4. Try incognito/private browsing mode

### Database still failing:
1. Verify DATABASE_URL has port 6543
2. Check Supabase is not paused (free tier auto-pauses after inactivity)
3. Verify your Supabase password is correct
4. Check Supabase Dashboard → Settings → Database for connection limits

### Session cookies not working:
1. Ensure you're using HTTPS (both api.dovydas.space and nd.dovydas.space)
2. Check browser developer tools → Application → Cookies
3. Look for `sessionid` cookie with domain `.dovydas.space`
4. Verify `SameSite=None` and `Secure` flags are set

## Quick Reference: Common Supabase Connection Strings

```bash
# ✅ CORRECT - Session Pooler (Port 6543) - USE THIS
postgresql://postgres.xxx:password@aws-0-region.pooler.supabase.com:6543/postgres

# ❌ AVOID - Direct Connection (Port 5432) - Connection limits
postgresql://postgres.xxx:password@aws-0-region.pooler.supabase.com:5432/postgres

# ❌ WRONG - Transaction Pooler (Port 6543 with different host) - Limited features
postgresql://postgres.xxx:password@db.xxx.supabase.co:6543/postgres
```

The key is: `pooler.supabase.com:6543` with Session mode!
