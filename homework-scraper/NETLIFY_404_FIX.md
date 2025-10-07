# ✅ Netlify 404 Fix Applied

## Problem
Getting "Page not found" 404 errors when deploying Next.js app to Netlify.

## Root Cause
1. **Wrong publish directory**: Was set to `.next` (server mode) instead of `out` (static export)
2. **Missing static export config**: Next.js wasn't configured for static HTML export
3. **API route incompatibility**: Had API proxy route that can't be statically exported

## Solutions Applied

### 1. Updated netlify.toml
**Changed:**
```toml
publish = ".next"  ❌
```

**To:**
```toml
publish = "out"  ✅
```

### 2. Updated next.config.js
**Added:**
```javascript
output: 'export',              // Enable static HTML export
trailingSlash: true,          // Better static hosting compatibility
images: {
  unoptimized: true,          // Required for static export
}
```

### 3. Removed API Proxy Route
**Deleted:** `frontend/app/api/[...path]/route.ts`

**Reason:** Static exports can't include API routes. Frontend will call backend directly using `NEXT_PUBLIC_API_URL`.

### 4. Build Verification
```bash
npm run build
✓ Compiled successfully in 6.1s
✓ Generating static pages (20/20)
✓ Exporting (2/2)
✓ Finalizing page optimization
```

**Output directory:** `frontend/out/` ✅

---

## 📋 Complete Configuration for Netlify

### Build Settings (Netlify Dashboard):
```
Base directory:     frontend
Build command:      npm run build
Publish directory:  frontend/out
Node version:       20
```

### Environment Variables (Netlify Dashboard):
```bash
NEXT_PUBLIC_API_URL=https://your-backend.onrender.com/api
NEXT_PUBLIC_SITE_URL=https://your-app.netlify.app
NEXT_PUBLIC_GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
```

### Redirects (Already in netlify.toml):
```toml
[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

---

## 📋 Complete Configuration for Render.com

### Option 1: Blueprint (RECOMMENDED)
Just use the `render.yaml` file - it's already configured!

In Render Dashboard:
1. Click "New" → "Blueprint"
2. Select your GitHub repo
3. Click "Apply"

### Option 2: Manual Setup

**Build Command:**
```bash
chmod +x build.sh && ./build.sh
```

Or detailed:
```bash
pip install --upgrade pip && \
pip install -r requirements.txt && \
playwright install chromium && \
python manage.py collectstatic --no-input && \
python manage.py migrate
```

**Start Command (Web Service):**
```bash
gunicorn homework_scraper.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --threads 4 --timeout 120
```

**Start Command (Celery Worker):**
```bash
celery -A homework_scraper worker --loglevel=info --concurrency=2
```

**Start Command (Celery Beat):**
```bash
celery -A homework_scraper beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

### Environment Variables for Render:
See `backend/.env.production.example` for complete list. Key ones:

```bash
SECRET_KEY=<use-render-generate-value>
DEBUG=False
ALLOWED_HOSTS=.onrender.com
DJANGO_SETTINGS_MODULE=homework_scraper.settings_production

# Database & Redis (auto-provided by services)
DATABASE_URL=<from-postgresql-service>
REDIS_URL=<from-redis-service>
CELERY_BROKER_URL=<from-redis-service>

# CORS - UPDATE with your Netlify URL!
CORS_ALLOWED_ORIGINS=https://your-app.netlify.app,http://localhost:3000
CSRF_TRUSTED_ORIGINS=https://your-app.netlify.app

# Google OAuth
GOOGLE_OAUTH2_CLIENT_ID=<from-google-console>
GOOGLE_OAUTH2_CLIENT_SECRET=<from-google-console>

# Encryption
ENCRYPTION_KEY=<use-render-generate-value>

# Playwright
PLAYWRIGHT_BROWSERS_PATH=/opt/render/.cache/ms-playwright
```

---

## 🧪 Test Locally Before Deploying

### Test Static Build:
```bash
cd frontend
npm run build

# Verify 'out' directory exists
ls out
# Should see: 404.html, index.html, _next/, etc.

# Test locally with a static server
npx serve out
# Visit http://localhost:3000
```

### Test Backend:
```bash
cd backend
python manage.py runserver
# Visit http://localhost:8000/api/health
# Should see: {"status": "ok"}
```

---

## 🚀 Deploy Now!

### Step 1: Push to GitHub
```bash
git add .
git commit -m "Fixed Netlify 404 - added static export config"
git push origin main
```

### Step 2: Deploy Backend (Render)
1. Go to https://render.com
2. Click "New" → "Blueprint"
3. Select your repo
4. Click "Apply Blueprint"
5. Wait ~15 minutes for services to start
6. Add environment variables (see list above)
7. Verify: Visit `https://your-backend.onrender.com/api/health`

### Step 3: Deploy Frontend (Netlify)
1. Go to https://netlify.com
2. Click "Add new site" → "Import an existing project"
3. Select GitHub → Choose your repo
4. Configure:
   - Base: `frontend`
   - Build: `npm run build`
   - Publish: `frontend/out`
5. Add environment variables (see list above)
6. Click "Deploy site"

### Step 4: Update URLs
After both are deployed:

**In Render (Backend):**
- Update `CORS_ALLOWED_ORIGINS` with your actual Netlify URL
- Update `CSRF_TRUSTED_ORIGINS` with your actual Netlify URL

**In Netlify (Frontend):**
- Update `NEXT_PUBLIC_API_URL` with your actual Render backend URL

**In Google Cloud Console:**
- Add authorized redirect URI: `https://your-app.netlify.app/auth/callback`
- Add authorized origin: `https://your-app.netlify.app`

---

## ✅ Verification Checklist

After deployment:
- [ ] Frontend loads without 404 errors
- [ ] Backend health check works: `/api/health`
- [ ] Google OAuth login works
- [ ] Can add educational platform credentials
- [ ] Homework scraping works
- [ ] No CORS errors in browser console
- [ ] Celery worker is processing tasks (check Render logs)

---

## 📚 Additional Documentation

- `RENDER_NETLIFY_COMMANDS.md` - All commands in one place
- `DEPLOYMENT.md` - Comprehensive deployment guide
- `QUICK_START_VISUAL.md` - Visual step-by-step guide
- `BUILD_FIXES.md` - Previous Next.js build fixes

---

**Status:** ✅ Ready to Deploy  
**Last Updated:** October 7, 2025  
**Build Status:** All 20 pages generated successfully
