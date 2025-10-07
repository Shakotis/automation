# Render.com & Netlify Deployment Commands

## 🔵 Netlify (Frontend) Configuration

### Build Settings in Netlify Dashboard:

```
Base directory:     frontend
Build command:      npm run build
Publish directory:  frontend/out
```

### Environment Variables to Set in Netlify:
```
NEXT_PUBLIC_API_URL=https://api.dovydas.space/api
NEXT_PUBLIC_SITE_URL=https://nd.dovydas.space
NEXT_PUBLIC_GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
```

### Alternative: Deploy via Netlify CLI
```bash
# Install Netlify CLI
npm install -g netlify-cli

# Login to Netlify
netlify login

# Deploy (from project root)
cd frontend
netlify deploy --prod

# Follow prompts:
# - Create & configure new site: Yes
# - Publish directory: ./out
```

---

## 🟢 Render.com (Backend) Configuration

### Option 1: Using Blueprint (render.yaml) - RECOMMENDED

**In Render Dashboard:**
1. Click "New" → "Blueprint"
2. Connect your GitHub repository
3. Select the repository
4. Render will automatically detect `render.yaml`
5. Click "Apply"

**Services will be created automatically:**
- ✅ Web Service (Django)
- ✅ PostgreSQL Database
- ✅ Redis
- ✅ Celery Worker
- ✅ Celery Beat

### Option 2: Manual Web Service Setup

**Build Settings in Render Dashboard:**

```
Name:               homework-scraper-backend
Environment:        Python 3
Region:             Oregon (or your choice)
Branch:             main
Root Directory:     backend

Build Command:
chmod +x build.sh && ./build.sh

Start Command:
gunicorn homework_scraper.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --threads 4 --timeout 120
```

### Build Command (Detailed):
```bash
pip install --upgrade pip && \
pip install -r requirements.txt && \
playwright install chromium && \
python manage.py collectstatic --no-input && \
python manage.py migrate
```

### Start Command for Web Service:
```bash
gunicorn homework_scraper.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --threads 4 --timeout 120
```

### Start Command for Celery Worker:
```bash
celery -A homework_scraper worker --loglevel=info --concurrency=2
```

### Start Command for Celery Beat:
```bash
celery -A homework_scraper beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

---

## 🔐 Environment Variables for Render (Backend)

**REQUIRED - Set these in Render Dashboard:**

```bash
# Django Core
SECRET_KEY=your-secret-key-here-use-render-generate-value
DEBUG=False
ALLOWED_HOSTS=.onrender.com
DJANGO_SETTINGS_MODULE=homework_scraper.settings_production

# Database (CRITICAL: Must be set by linking PostgreSQL service in Render)
# DO NOT manually enter this! Link the PostgreSQL service in Render Dashboard
# and it will automatically populate this variable with the correct format:
# DATABASE_URL=postgresql://user:password@host:5432/database
DATABASE_URL=${postgres.database_url}  # This is set automatically by Render when you link the database

# Redis (auto-provided by Render Redis service)
# These are also set automatically when you link the Redis service
REDIS_URL=${redis.connectionString}
CELERY_BROKER_URL=${redis.connectionString}
CELERY_RESULT_BACKEND=${redis.connectionString}

# CORS - UPDATE with your custom domains
CORS_ALLOWED_ORIGINS=https://nd.dovydas.space,http://localhost:3000
CSRF_TRUSTED_ORIGINS=https://nd.dovydas.space,https://api.dovydas.space

# Google OAuth - GET from Google Cloud Console
GOOGLE_OAUTH2_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_OAUTH2_CLIENT_SECRET=your-client-secret

# Supabase (if used)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key

# Encryption for credentials - USE Render Generate Value
ENCRYPTION_KEY=32-byte-encryption-key

# Playwright
PLAYWRIGHT_BROWSERS_PATH=/opt/render/.cache/ms-playwright
```

---

## 📝 Step-by-Step Deployment

### Step 1: Deploy Backend to Render (20 minutes)

1. **Create Render Account**: https://render.com
2. **Connect GitHub**: Dashboard → Connect Repository
3. **Deploy via Blueprint**:
   - Click "New" → "Blueprint"
   - Select `automation` repository
   - Render detects `render.yaml`
   - Click "Apply Blueprint"
   - Wait for services to provision (~10-15 mins)

4. **Add Environment Variables**:
   - Go to each service
   - Click "Environment"
   - Add variables from list above
   - **IMPORTANT**: Update these after creation:
     - `CORS_ALLOWED_ORIGINS` - add your Netlify URL
     - `GOOGLE_OAUTH2_CLIENT_ID` - from Google Console
     - `GOOGLE_OAUTH2_CLIENT_SECRET` - from Google Console

5. **Verify Backend**:
   - Visit: `https://your-backend.onrender.com/api/health`
   - Should see: `{"status": "ok"}`

### Step 2: Deploy Frontend to Netlify (10 minutes)

1. **Create Netlify Account**: https://netlify.com
2. **Connect GitHub**: 
   - Click "Add new site" → "Import an existing project"
   - Choose GitHub → Select `automation` repository
   
3. **Configure Build Settings**:
   ```
   Base directory:     frontend
   Build command:      npm run build
   Publish directory:  frontend/out
   ```

4. **Add Environment Variables**:
   - Site settings → Environment variables → Add variables
   ```
   NEXT_PUBLIC_API_URL=https://api.dovydas.space/api
   NEXT_PUBLIC_SITE_URL=https://nd.dovydas.space
   NEXT_PUBLIC_GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
   ```

5. **Deploy**: Click "Deploy site"

### Step 3: Connect Services (5 minutes)

1. **Update Backend CORS**:
   - Go to Render → homework-scraper-backend → Environment
   - Update `CORS_ALLOWED_ORIGINS`: `https://nd.dovydas.space`
   - Click "Save Changes" (triggers redeploy)

2. **Update Google OAuth**:
   - Go to Google Cloud Console
   - Add authorized redirect URI: `https://nd.dovydas.space/auth/callback`
   - Add authorized origin: `https://nd.dovydas.space`

### Step 4: Test (5 minutes)

1. Visit your frontend: `https://nd.dovydas.space`
2. Click "Sign in with Google"
3. Add educational platform credentials
4. Test homework scraping
5. Verify data syncs to Google Tasks

---

## 🐛 Troubleshooting

### Frontend 404 Errors:
- ✅ **FIXED**: Changed `publish` to `out` in netlify.toml
- ✅ **FIXED**: Added `output: 'export'` to next.config.js
- ✅ **FIXED**: Added proper redirect rules

### If you still get 404s:
```bash
# Rebuild locally to test
cd frontend
npm run build

# Check that 'out' directory was created
ls out

# Should see: 404.html, index.html, _next folder, etc.
```

### Backend Connection Issues:
- Check CORS settings in Render
- Verify `NEXT_PUBLIC_API_URL` in Netlify
- Check backend logs in Render Dashboard

### Build Failures:
- Check Node version (should be 20)
- Verify all dependencies installed
- Check build logs in dashboard

---

## 📊 Service Costs

### Free Tier (Good for Testing):
- **Netlify**: 100 GB bandwidth/month, 300 build minutes
- **Render**: 
  - Web service sleeps after 15 min inactivity
  - PostgreSQL: 90 days, then expires
  - Redis: Persistent

### Paid Tier (Production):
- **Netlify Pro**: $19/month
  - Unlimited bandwidth
  - 300 build minutes
  
- **Render**:
  - Web service: $7/month (always on)
  - PostgreSQL: $7/month (persistent)
  - Redis: $7/month
  - **Total**: ~$21/month

**Combined Total**: ~$40/month for full production

---

## 🎯 Quick Command Reference

### Local Development:
```bash
# Frontend
cd frontend
npm run dev

# Backend
cd backend
python manage.py runserver
celery -A homework_scraper worker -l info
celery -A homework_scraper beat -l info
```

### Production Build Test:
```bash
# Frontend
cd frontend
npm run build
npm start

# Backend
cd backend
python manage.py collectstatic --no-input
gunicorn homework_scraper.wsgi:application
```

### Git Deployment:
```bash
# Commit changes
git add .
git commit -m "Deploy to production"
git push origin main

# Both Netlify and Render auto-deploy on push!
```

---

## ✅ Checklist

### Before Deploying:
- [ ] Google OAuth credentials ready
- [ ] Supabase credentials ready (if using)
- [ ] GitHub repository connected to Render
- [ ] GitHub repository connected to Netlify

### After Backend Deployed:
- [ ] Health check passes: `/api/health`
- [ ] Database migrated successfully
- [ ] Celery worker running
- [ ] Environment variables set

### After Frontend Deployed:
- [ ] Site loads without 404
- [ ] Google login works
- [ ] API calls reach backend
- [ ] No CORS errors in console

### Final Verification:
- [ ] Can add educational platform credentials
- [ ] Homework scraping works
- [ ] Google Tasks sync works
- [ ] Auto-scraping runs on schedule

---

**Need Help?** Check:
- `DEPLOYMENT.md` - Comprehensive guide
- `QUICK_START_VISUAL.md` - Visual guide
- `BUILD_FIXES.md` - Recent fixes applied
