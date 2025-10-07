# DATABASE_URL Port Error - FIXED ✅

## Problem
Build was failing with:
```
ValueError: Port could not be cast to integer value as 'port'
```

This error occurred because the `DATABASE_URL` environment variable had a malformed value with literal text "port" instead of a number like "5432".

---

## Root Cause
The `render.yaml` file had incorrect syntax for defining the PostgreSQL database:
```yaml
# WRONG ❌
services:
  - type: pserv  # Invalid type
    name: homework-scraper-db
    runtime: postgresql
    databaseName: homework_scraper
    databaseUser: homework_user
```

---

## Fixes Applied

### 1. Fixed render.yaml Structure ✅
**File**: `render.yaml`

Changed database definition to correct format:
```yaml
# CORRECT ✅
databases:
  - name: homework-scraper-db
    databaseName: homework_scraper
    user: homework_user
    plan: free
```

**Key changes:**
- Moved `databases:` to root level (not inside `services:`)
- Changed type from `pserv` to proper database definition
- Used `user` instead of `databaseUser`
- Removed `runtime: postgresql` (not needed)

### 2. Added Better Error Handling ✅
**File**: `backend/homework_scraper/settings_production.py`

Added validation to provide clearer error messages:
```python
DATABASE_URL = os.environ.get('DATABASE_URL', '')

# Check if DATABASE_URL is properly set
if not DATABASE_URL or DATABASE_URL == '' or 'postgresql://' not in DATABASE_URL:
    raise ValueError(
        "DATABASE_URL environment variable is not properly set. "
        "Please configure it in Render Dashboard with format: "
        "postgresql://user:password@host:port/database"
    )

try:
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
except ValueError as e:
    raise ValueError(
        f"Failed to parse DATABASE_URL: {str(e)}. "
        f"Check that your DATABASE_URL is properly formatted. "
        f"Current value starts with: {DATABASE_URL[:30]}..."
    )
```

### 3. Updated Documentation ✅
**File**: `RENDER_NETLIFY_COMMANDS.md`

Clarified that DATABASE_URL should be automatically set:
```bash
# Database (CRITICAL: Must be set by linking PostgreSQL service in Render)
# DO NOT manually enter this! Link the PostgreSQL service in Render Dashboard
DATABASE_URL=${postgres.database_url}
```

### 4. Created Troubleshooting Guide ✅
**File**: `DATABASE_URL_FIX.md`

Added comprehensive guide with:
- Problem explanation
- Multiple solution options
- Verification steps
- Best practices

---

## How to Deploy Now

### Option A: Using render.yaml (RECOMMENDED)

1. **Commit these changes:**
   ```powershell
   git add render.yaml backend/homework_scraper/settings_production.py
   git commit -m "Fix DATABASE_URL configuration in render.yaml"
   git push origin main
   ```

2. **Deploy in Render Dashboard:**
   - Go to https://render.com/dashboard
   - Click "New" → "Blueprint"
   - Connect your GitHub repository
   - Select `automation` repository
   - Render will detect the updated `render.yaml`
   - Click "Apply Blueprint"
   - Wait for deployment (~10-15 minutes)

3. **Verify:**
   - Check that all services are created:
     - ✅ homework-scraper-backend (Web Service)
     - ✅ homework-scraper-db (PostgreSQL)
     - ✅ homework-scraper-redis (Redis)
     - ✅ homework-scraper-celery (Worker)
     - ✅ homework-scraper-celery-beat (Worker)
   
   - Visit: `https://homework-scraper-backend.onrender.com/api/health`
   - Should see: `{"status": "ok"}`

### Option B: Manual Database Linking

If blueprint doesn't work, manually link the database:

1. **Create PostgreSQL Database:**
   - Dashboard → New → PostgreSQL
   - Name: `homework-scraper-db`
   - Database: `homework_scraper`
   - User: `homework_user`
   - Click "Create Database"

2. **Link to Web Service:**
   - Go to web service → Environment
   - Add variable: `DATABASE_URL`
   - Value: Click "Add from Database"
   - Select `homework-scraper-db`
   - Choose "Internal Database URL"
   - Save and redeploy

---

## Expected Build Output

After fixing, you should see:
```bash
✓ Installing Playwright browsers...
FFMPEG playwright build v1010 downloaded to /opt/render/.cache/ms-playwright/ffmpeg-1010
Collecting static files...
127 static files copied to '/opt/render/project/src/staticfiles'
Running migrations...
Operations to perform:
  Apply all migrations: admin, auth, authentication, contenttypes, django_celery_beat, scraper, sessions, tasks
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  ... (more migrations)
✓ Build complete!
✓ Service started successfully
```

---

## Verification Checklist

After deployment:
- [ ] Build completes without DATABASE_URL errors
- [ ] Migrations run successfully
- [ ] Static files collected
- [ ] Health check endpoint works
- [ ] Database has tables created
- [ ] Celery worker connects to Redis
- [ ] Can create user accounts
- [ ] Can save educational credentials

---

## Key Takeaways

1. **Always use `databases:` at root level in render.yaml**
2. **Don't use `type: pserv` - that's not valid**
3. **Let Render auto-populate DATABASE_URL via service linking**
4. **Never manually type DATABASE_URL with template placeholders**
5. **Test render.yaml syntax before deploying**

---

## Related Files
- `render.yaml` - Blueprint configuration (FIXED ✅)
- `settings_production.py` - Production settings with validation (FIXED ✅)
- `DATABASE_URL_FIX.md` - Detailed troubleshooting guide
- `RENDER_NETLIFY_COMMANDS.md` - Updated deployment instructions

---

**Status**: Ready to deploy! 🚀

Commit the changes and redeploy using Blueprint for automatic database setup.
