# Render Environment Variables - Supabase Configuration

## 🎯 Overview

Your `render.yaml` has been updated to use **Supabase** instead of Render PostgreSQL.
This guide shows you exactly which environment variables to set in Render Dashboard.

---

## 📋 Environment Variables to Set

You need to set these **manually** in Render Dashboard for each service:

### 🌐 Web Service: `homework-scraper-backend`

Go to: https://dashboard.render.com → `homework-scraper-backend` → Environment

**Add these variables:**

```bash
# ============================================
# DATABASE CONFIGURATION (Supabase)
# ============================================

DATABASE_URL
postgresql://postgres.kcixuytszyzgvcybxyym:IGnuxas123@aws-1-eu-north-1.pooler.supabase.com:5432/postgres

# ============================================
# SUPABASE API CREDENTIALS
# ============================================

SUPABASE_URL
https://kcixuytszyzgvcybxyym.supabase.co

SUPABASE_KEY
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtjaXh1eXRzenl6Z3ZjeWJ4eXltIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTkxODY3NjYsImV4cCI6MjA3NDc2Mjc2Nn0.SQO1ni7OKTWSb76nFbgUwY50CDL4UfW8pW8VA7Fsnwg

SUPABASE_SERVICE_KEY
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtjaXh1eXRzenl6Z3ZjeWJ4eXltIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1OTE4Njc2NiwiZXhwIjoyMDc0NzYyNzY2fQ.bsUDTLD5__idVQuv5SeqQO9wxL-ZpNVRPWAhF16XQkk

# ============================================
# GOOGLE OAUTH (Get from Google Cloud Console)
# ============================================

GOOGLE_OAUTH2_CLIENT_ID
your-google-client-id.apps.googleusercontent.com

GOOGLE_OAUTH2_CLIENT_SECRET
your-google-client-secret

# ============================================
# ENCRYPTION (Use Render's Generate Value)
# ============================================

ENCRYPTION_KEY
Click "Generate Value" button in Render

# ============================================
# OTHER (Already set by render.yaml)
# ============================================
# These are automatically set:
# - SECRET_KEY (auto-generated)
# - DEBUG (false)
# - ALLOWED_HOSTS (.onrender.com,api.dovydas.space)
# - CORS_ALLOWED_ORIGINS
# - CSRF_TRUSTED_ORIGINS
# - REDIS_URL (from Redis service)
# - CELERY_BROKER_URL (from Redis service)
```

---

### 👷 Worker Service: `homework-scraper-celery`

Go to: https://dashboard.render.com → `homework-scraper-celery` → Environment

**Add these variables:**

```bash
# ============================================
# DATABASE CONFIGURATION (Supabase)
# ============================================

DATABASE_URL
postgresql://postgres.kcixuytszyzgvcybxyym:IGnuxas123@aws-1-eu-north-1.pooler.supabase.com:5432/postgres

# ============================================
# SUPABASE API CREDENTIALS
# ============================================

SUPABASE_URL
https://kcixuytszyzgvcybxyym.supabase.co

SUPABASE_KEY
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtjaXh1eXRzenl6Z3ZjeWJ4eXltIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTkxODY3NjYsImV4cCI6MjA3NDc2Mjc2Nn0.SQO1ni7OKTWSb76nFbgUwY50CDL4UfW8pW8VA7Fsnwg

# ============================================
# SHARED SECRETS (Copy from web service)
# ============================================

SECRET_KEY
Copy the value from homework-scraper-backend service

ENCRYPTION_KEY
Copy the value from homework-scraper-backend service

# ============================================
# OTHER (Already set by render.yaml)
# ============================================
# These are automatically set:
# - REDIS_URL (from Redis service)
# - CELERY_BROKER_URL (from Redis service)
# - PLAYWRIGHT_BROWSERS_PATH
```

---

### ⏰ Beat Service: `homework-scraper-celery-beat`

Go to: https://dashboard.render.com → `homework-scraper-celery-beat` → Environment

**Add these variables:**

```bash
# ============================================
# DATABASE CONFIGURATION (Supabase)
# ============================================

DATABASE_URL
postgresql://postgres.kcixuytszyzgvcybxyym:IGnuxas123@aws-1-eu-north-1.pooler.supabase.com:5432/postgres

# ============================================
# SUPABASE API CREDENTIALS
# ============================================

SUPABASE_URL
https://kcixuytszyzgvcybxyym.supabase.co

SUPABASE_KEY
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtjaXh1eXRzenl6Z3ZjeWJ4eXltIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTkxODY3NjYsImV4cCI6MjA3NDc2Mjc2Nn0.SQO1ni7OKTWSb76nFbgUwY50CDL4UfW8pW8VA7Fsnwg

# ============================================
# SHARED SECRETS (Copy from web service)
# ============================================

SECRET_KEY
Copy the value from homework-scraper-backend service

# ============================================
# OTHER (Already set by render.yaml)
# ============================================
# These are automatically set:
# - REDIS_URL (from Redis service)
# - CELERY_BROKER_URL (from Redis service)
```

---

## 🚀 Step-by-Step Deployment

### Step 1: Commit and Push Changes

```powershell
cd w:\automation\homework-scraper

# Stage all changes
git add .

# Commit
git commit -m "Configure Supabase database and fix Netlify 404"

# Push to GitHub
git push origin main
```

### Step 2: Delete Old Services (If They Exist)

If you previously deployed with the old `render.yaml`:

1. Go to https://dashboard.render.com
2. **Delete these if they exist**:
   - `homework-scraper-db` (PostgreSQL database)
   - `homework-scraper-backend` (old web service)
   - `homework-scraper-celery` (old worker)
   - `homework-scraper-celery-beat` (old beat worker)
3. **Keep these**:
   - `homework-scraper-redis` (Redis - can be reused)

### Step 3: Deploy with Blueprint

1. **Go to Render Dashboard**
2. **Click "New" → "Blueprint"**
3. **Connect your GitHub repository**: `automation`
4. **Render detects `render.yaml`**
5. **Click "Apply Blueprint"**

Render will create:
- ✅ Web Service: `homework-scraper-backend`
- ✅ Redis: `homework-scraper-redis` (or use existing)
- ✅ Worker: `homework-scraper-celery`
- ✅ Worker: `homework-scraper-celery-beat`

⏱️ **Wait 2-3 minutes** for services to be created (NOT provisioned yet, just created)

### Step 4: Set Environment Variables

**For Web Service** (`homework-scraper-backend`):

1. Click on the service
2. Go to "Environment" tab
3. Click "Add Environment Variable"
4. Add each variable from the list above:
   - `DATABASE_URL`
   - `SUPABASE_URL`
   - `SUPABASE_KEY`
   - `SUPABASE_SERVICE_KEY`
   - `GOOGLE_OAUTH2_CLIENT_ID`
   - `GOOGLE_OAUTH2_CLIENT_SECRET`
   - `ENCRYPTION_KEY` (click "Generate Value")
5. Click "Save Changes" (triggers build)

**For Celery Worker** (`homework-scraper-celery`):

1. Go to the service → Environment tab
2. Add:
   - `DATABASE_URL` (same as web service)
   - `SUPABASE_URL` (same as web service)
   - `SUPABASE_KEY` (same as web service)
   - `SECRET_KEY` (copy from web service after it's generated)
   - `ENCRYPTION_KEY` (copy from web service)
3. Save changes

**For Celery Beat** (`homework-scraper-celery-beat`):

1. Go to the service → Environment tab
2. Add:
   - `DATABASE_URL` (same as web service)
   - `SUPABASE_URL` (same as web service)
   - `SUPABASE_KEY` (same as web service)
   - `SECRET_KEY` (copy from web service)
3. Save changes

### Step 5: Wait for Build

⏱️ **Time**: 5-8 minutes

Watch the logs:
- Web service should build and start
- Migrations should run automatically
- Health check should pass

### Step 6: Verify Deployment

1. **Check Health Endpoint**:
   ```
   https://homework-scraper-backend.onrender.com/api/health
   ```
   Should return: `{"status": "ok"}`

2. **Check Supabase Dashboard**:
   - Go to: https://supabase.com/dashboard/project/kcixuytszyzgvcybxyym/editor
   - Should see Django tables created:
     - auth_user
     - django_migrations
     - django_session
     - etc.

3. **Check Service Logs**:
   - All services should be running
   - No error messages
   - Celery worker connected to Redis

---

## ✅ Verification Checklist

After deployment, verify:

### Backend:
- [ ] Web service is "Live" (green dot)
- [ ] Health check works: `/api/health`
- [ ] Build logs show successful migrations
- [ ] No errors in service logs

### Database:
- [ ] Tables created in Supabase dashboard
- [ ] Can connect to database from Render shell
- [ ] Migrations applied successfully

### Workers:
- [ ] Celery worker is "Live"
- [ ] Celery beat is "Live"
- [ ] Both connected to Redis (check logs)
- [ ] No connection errors

### Frontend:
- [ ] Netlify build succeeds
- [ ] Site loads at: https://nd.dovydas.space
- [ ] No 404 errors on routes
- [ ] Can reach API endpoints

---

## 🐛 Troubleshooting

### Build Fails: "DATABASE_URL not set"

**Cause**: Environment variable not added

**Solution**:
1. Go to service → Environment tab
2. Add `DATABASE_URL` with Supabase connection string
3. Click "Save Changes"

### Build Fails: "could not connect to server"

**Cause**: Wrong connection string or Supabase project paused

**Solution**:
1. Verify connection string is exactly:
   ```
   postgresql://postgres.kcixuytszyzgvcybxyym:IGnuxas123@aws-1-eu-north-1.pooler.supabase.com:5432/postgres
   ```
2. Check Supabase project is active (not paused)
3. Try direct connection instead of pooled:
   ```
   postgresql://postgres:IGnuxas123@db.kcixuytszyzgvcybxyym.supabase.co:5432/postgres
   ```

### Migrations Fail: "relation already exists"

**Cause**: Tables already exist from previous deployment

**Solution**:
1. Go to Supabase dashboard
2. SQL Editor
3. Run:
   ```sql
   -- Drop all Django tables (if needed)
   DROP SCHEMA public CASCADE;
   CREATE SCHEMA public;
   ```
4. Redeploy in Render

### Workers Can't Connect to Database

**Cause**: Environment variables not set for workers

**Solution**:
1. Verify `DATABASE_URL` is set in BOTH worker services
2. Copy `SECRET_KEY` from web service to workers
3. Redeploy workers

---

## 📝 Environment Variables Summary Table

| Variable | Web Service | Celery Worker | Celery Beat | Value |
|----------|-------------|---------------|-------------|-------|
| DATABASE_URL | ✅ Required | ✅ Required | ✅ Required | Supabase connection string |
| SUPABASE_URL | ✅ Required | ✅ Required | ✅ Required | https://kcixuytszyzgvcybxyym.supabase.co |
| SUPABASE_KEY | ✅ Required | ✅ Required | ✅ Required | Anon key (starts with eyJhbGci...) |
| SUPABASE_SERVICE_KEY | ✅ Required | ❌ Optional | ❌ Optional | Service role key |
| SECRET_KEY | ✅ Auto-generated | ✅ Copy from web | ✅ Copy from web | Django secret key |
| ENCRYPTION_KEY | ✅ Generate | ✅ Copy from web | ❌ Not needed | 32-byte key |
| GOOGLE_OAUTH2_CLIENT_ID | ✅ Required | ❌ Not needed | ❌ Not needed | From Google Console |
| GOOGLE_OAUTH2_CLIENT_SECRET | ✅ Required | ❌ Not needed | ❌ Not needed | From Google Console |
| REDIS_URL | ✅ Auto-linked | ✅ Auto-linked | ✅ Auto-linked | From Redis service |
| CELERY_BROKER_URL | ✅ Auto-linked | ✅ Auto-linked | ✅ Auto-linked | From Redis service |

---

## 🎉 Success!

Once all variables are set and services are deployed:

1. **Frontend**: https://nd.dovydas.space
2. **Backend**: https://homework-scraper-backend.onrender.com
3. **Health**: https://homework-scraper-backend.onrender.com/api/health
4. **Database**: Supabase dashboard shows tables

Next steps:
- Configure custom domain (api.dovydas.space)
- Update Google OAuth credentials
- Test the full application workflow

---

**Need help?** Check the logs in Render Dashboard or Supabase Dashboard for specific error messages.
