# 🚀 READY TO DEPLOY - Final Steps

## ✅ What's Been Fixed

### 1. Frontend (Netlify 404 Error) - FIXED ✅
- ✅ Created `netlify.toml` with correct publish directory (`out`)
- ✅ Added SPA redirect rules (`_redirects` file)
- ✅ Configured caching and security headers

### 2. Backend (Database Configuration) - FIXED ✅
- ✅ Updated `render.yaml` to use Supabase instead of Render PostgreSQL
- ✅ Removed database provisioning section
- ✅ Configured environment variables for all services
- ✅ Tested Supabase connection locally - **WORKS!** ✅

---

## 🎯 Your Credentials (Confirmed Working)

```bash
# Database
DATABASE_URL=postgresql://postgres.kcixuytszyzgvcybxyym:IGnuxas123@aws-1-eu-north-1.pooler.supabase.com:5432/postgres

# Supabase API
SUPABASE_URL=https://kcixuytszyzgvcybxyym.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtjaXh1eXRzenl6Z3ZjeWJ4eXltIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTkxODY3NjYsImV4cCI6MjA3NDc2Mjc2Nn0.SQO1ni7OKTWSb76nFbgUwY50CDL4UfW8pW8VA7Fsnwg
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtjaXh1eXRzenl6Z3ZjeWJ4eXltIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1OTE4Njc2NiwiZXhwIjoyMDc0NzYyNzY2fQ.bsUDTLD5__idVQuv5SeqQO9wxL-ZpNVRPWAhF16XQkk
```

✅ **Database connection tested and confirmed working!**

---

## 📋 Deployment Steps (15 minutes total)

### Step 1: Commit and Push (2 minutes)

```powershell
cd w:\automation\homework-scraper

# Add all changes
git add .

# Commit
git commit -m "Configure Supabase database and fix Netlify 404"

# Push to GitHub
git push origin main
```

**What happens:**
- ✅ Netlify auto-deploys frontend (2-3 min)
- ✅ Frontend will be live at https://nd.dovydas.space
- ⏳ Render needs manual setup (next steps)

---

### Step 2: Deploy to Render (10 minutes)

#### Option A: Fresh Deployment (Recommended)

**If this is your first deploy OR you want to start fresh:**

1. **Go to Render Dashboard**: https://dashboard.render.com

2. **Delete old services if they exist**:
   - Look for `homework-scraper-backend`, `homework-scraper-celery`, `homework-scraper-celery-beat`, `homework-scraper-db`
   - Delete them (keep `homework-scraper-redis` if it exists)

3. **Deploy with Blueprint**:
   - Click **"New"** → **"Blueprint"**
   - Connect GitHub repository: `Shakotis/automation`
   - Render detects `render.yaml`
   - Click **"Apply Blueprint"**
   - Wait 2-3 minutes for services to be created

4. **Set Environment Variables**:
   
   **For `homework-scraper-backend`:**
   - Go to service → **Environment** tab
   - Add these variables (click "Add Environment Variable" for each):
     ```
     DATABASE_URL = postgresql://postgres.kcixuytszyzgvcybxyym:IGnuxas123@aws-1-eu-north-1.pooler.supabase.com:5432/postgres
     
     SUPABASE_URL = https://kcixuytszyzgvcybxyym.supabase.co
     
     SUPABASE_KEY = eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtjaXh1eXRzenl6Z3ZjeWJ4eXltIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTkxODY3NjYsImV4cCI6MjA3NDc2Mjc2Nn0.SQO1ni7OKTWSb76nFbgUwY50CDL4UfW8pW8VA7Fsnwg
     
     SUPABASE_SERVICE_KEY = eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtjaXh1eXRzenl6Z3ZjeWJ4eXltIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1OTE4Njc2NiwiZXhwIjoyMDc0NzYyNzY2fQ.bsUDTLD5__idVQuv5SeqQO9wxL-ZpNVRPWAhF16XQkk
     
     ENCRYPTION_KEY = [Click "Generate Value" button]
     
     GOOGLE_OAUTH2_CLIENT_ID = [Your Google client ID]
     
     GOOGLE_OAUTH2_CLIENT_SECRET = [Your Google client secret]
     ```
   - Click **"Save Changes"** → This triggers the build!

   **For `homework-scraper-celery`:**
   - Go to service → **Environment** tab
   - Add:
     ```
     DATABASE_URL = [same as web service]
     SUPABASE_URL = [same as web service]
     SUPABASE_KEY = [same as web service]
     SECRET_KEY = [copy from web service AFTER it's generated]
     ENCRYPTION_KEY = [copy from web service]
     ```
   - Save changes

   **For `homework-scraper-celery-beat`:**
   - Go to service → **Environment** tab
   - Add:
     ```
     DATABASE_URL = [same as web service]
     SUPABASE_URL = [same as web service]
     SUPABASE_KEY = [same as web service]
     SECRET_KEY = [copy from web service]
     ```
   - Save changes

5. **Wait for Build** (5-8 minutes):
   - Watch logs in `homework-scraper-backend`
   - Should see migrations running
   - Build should succeed

---

#### Option B: Update Existing Deployment

**If services already exist and just need updating:**

1. **Update Environment Variables**:
   - Go to each service
   - Add the `DATABASE_URL`, `SUPABASE_URL`, etc. (from Step 2-4 above)
   
2. **Manual Deploy**:
   - For each service, click **"Manual Deploy"** → **"Deploy latest commit"**

---

### Step 3: Verify Deployment (2 minutes)

#### Frontend Check:
```
Visit: https://nd.dovydas.space
Expected: Site loads without 404 ✅
```

#### Backend Check:
```
Visit: https://homework-scraper-backend.onrender.com/api/health
Expected: {"status": "ok"} ✅
```

#### Database Check:
```
1. Go to: https://supabase.com/dashboard/project/kcixuytszyzgvcybxyym/editor
2. Should see tables created:
   - auth_user
   - django_migrations
   - django_session
   - authentication_*
   - scraper_*
   - tasks_*
```

---

## ✅ Success Indicators

You'll know everything worked when:

### Frontend (Netlify):
- ✅ Site loads at https://nd.dovydas.space
- ✅ No 404 errors on any routes
- ✅ Can navigate between pages
- ✅ Static assets load correctly

### Backend (Render):
- ✅ Build logs show: "Build complete!" ✅
- ✅ Migrations: "Running migrations... OK" ✅
- ✅ Service status: "Live" (green dot) ✅
- ✅ Health endpoint returns: `{"status": "ok"}` ✅

### Database (Supabase):
- ✅ All Django tables visible in dashboard
- ✅ No connection errors in logs
- ✅ Can query tables in SQL editor

### Workers (Render):
- ✅ `homework-scraper-celery` status: "Live" ✅
- ✅ `homework-scraper-celery-beat` status: "Live" ✅
- ✅ Logs show: "celery@worker ready" ✅

---

## 🐛 Quick Troubleshooting

### Frontend Still Shows 404:
```powershell
# Clear Netlify cache and redeploy
# In Netlify dashboard: Deploys → Trigger deploy → Clear cache and deploy
```

### Backend Build Fails - "DATABASE_URL not set":
```
Make sure you added DATABASE_URL in Environment tab
Value should start with: postgresql://postgres.kcixuytszyzgvcybxyym:IGnuxas123@...
```

### Backend Build Fails - "could not connect":
```
Check Supabase project is active (not paused)
Try direct connection instead:
postgresql://postgres:IGnuxas123@db.kcixuytszyzgvcybxyym.supabase.co:5432/postgres
```

### Workers Not Starting:
```
Make sure you copied SECRET_KEY from web service to workers
Check DATABASE_URL is set for workers too
```

---

## 📝 Environment Variables Checklist

Before deploying, make sure you have:

### For Render Backend:
- [x] `DATABASE_URL` - Supabase connection string
- [x] `SUPABASE_URL` - Project URL
- [x] `SUPABASE_KEY` - Anon key
- [x] `SUPABASE_SERVICE_KEY` - Service role key
- [ ] `ENCRYPTION_KEY` - Generate in Render
- [ ] `GOOGLE_OAUTH2_CLIENT_ID` - Get from Google Console
- [ ] `GOOGLE_OAUTH2_CLIENT_SECRET` - Get from Google Console

### For Netlify Frontend:
- [ ] `NEXT_PUBLIC_API_URL` - https://api.dovydas.space/api (or .onrender.com URL)
- [ ] `NEXT_PUBLIC_SITE_URL` - https://nd.dovydas.space
- [ ] `NEXT_PUBLIC_GOOGLE_CLIENT_ID` - Same as backend

---

## 🎯 After Successful Deployment

### 1. Configure Custom Domain (api.dovydas.space)

See: `CUSTOM_DOMAIN_SETUP.md`

- Add CNAME: `api` → `homework-scraper-backend.onrender.com`
- Add custom domain in Render
- Wait for SSL certificate

### 2. Update Google OAuth

- Go to: https://console.cloud.google.com
- Add authorized origins:
  - `https://nd.dovydas.space`
  - `https://api.dovydas.space`
- Add redirect URIs:
  - `https://nd.dovydas.space/auth/callback`

### 3. Test Full Application

- Sign in with Google
- Add educational platform credentials
- Test homework scraping
- Verify Google Tasks sync

---

## 📚 Reference Documents

- **`RENDER_ENV_VARS_SUPABASE.md`** - Detailed environment variables guide
- **`SUPABASE_DATABASE_SETUP.md`** - Supabase configuration guide
- **`CUSTOM_DOMAIN_SETUP.md`** - Domain configuration
- **`FIXES_SUMMARY.md`** - Summary of all fixes
- **`VISUAL_ACTION_GUIDE.md`** - Visual step-by-step guide

---

## 🚀 Ready? Let's Deploy!

**Run these commands NOW:**

```powershell
cd w:\automation\homework-scraper
git add .
git commit -m "Configure Supabase database and fix Netlify 404"
git push origin main
```

Then follow Step 2 above to deploy to Render! 🎉

---

**Estimated Total Time:**
- Commit & Push: 1 minute
- Netlify auto-deploy: 2-3 minutes
- Render setup: 5 minutes
- Render build: 5-8 minutes
- **Total: ~15 minutes** ⏱️

You're almost there! 🚀
