# 🚀 Deploy Now - All Issues Fixed!

## ✅ What's Been Fixed

1. **Selenium ModuleNotFoundError** - Completely removed/replaced with Playwright
2. **DATABASE_URL parsing** - Fixed with Supabase SSL configuration
3. **Netlify 404 errors** - Fixed with proper netlify.toml and _redirects
4. **Import errors** - All production code now uses scrapers_simple (requests-based)

## 🎯 Quick Deploy Steps

### 1. Commit and Push Changes
```powershell
cd W:\automation\homework-scraper
git add .
git commit -m "Remove Selenium, replace with Playwright for credential verification"
git push origin main
```

### 2. Deploy to Render

#### Option A: Via Render Dashboard (Recommended)
1. Go to https://dashboard.render.com
2. Click "New +" → "Blueprint"
3. Connect your GitHub repository: `homework-scraper`
4. Render will read `render.yaml` and create services
5. **IMPORTANT:** After creation, immediately add environment variables (before first deploy)

#### Option B: Via Render CLI
```powershell
# Install Render CLI (if not installed)
npm install -g @render/cli

# Deploy
render deploy
```

### 3. Add Environment Variables in Render Dashboard

Go to your backend service → Environment tab, and add:

```bash
# Database (Use the POOLED connection for better performance)
DATABASE_URL=postgresql://postgres.kcixuytszyzgvcybxyym:IGnuxas123@aws-1-eu-north-1.pooler.supabase.com:5432/postgres

# Supabase
SUPABASE_URL=https://kcixuytszyzgvcybxyym.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtjaXh1eXRzenlEZ3ZjeWJ4eXltIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzUyNDU0MTMsImV4cCI6MjA1MDgyMTQxM30.rHE3YE_e1d1FslzFmY-RL5QXM8-8bAKr4EXpA5y6Seo
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtjaXh1eXRzenlEZ3ZjeWJ4eXltIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTczNTI0NTQxMywiZXhwIjoyMDUwODIxNDEzfQ.lgnzPTcj7QXuLKJoQ6lzC13L-e4aD4Jm_yI8nQ-_EpI

# Security
ENCRYPTION_KEY=your_32_character_encryption_key_here_make_it_random

# Google OAuth (Get these from Google Cloud Console)
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REDIRECT_URI=https://api.dovydas.space/auth/google/callback

# Django
DJANGO_SECRET_KEY=your_django_secret_key_here
DJANGO_ALLOWED_HOSTS=api.dovydas.space
DJANGO_CORS_ALLOWED_ORIGINS=https://nd.dovydas.space

# Optional: Celery (if using background tasks)
CELERY_BROKER_URL=redis://your-redis-url
```

### 4. Verify Build Success

Watch the build logs in Render dashboard. You should see:
```
✅ Installing dependencies from requirements.txt
✅ playwright==1.48.0 installed successfully
✅ Installing Playwright browsers
✅ Collecting static files - 163 static files copied
✅ Running migrations
✅ Build successful!
```

If you see any errors, check the logs and refer to troubleshooting below.

### 5. Configure Custom Domains (After Successful Deployment)

#### Frontend (Netlify)
1. Go to Netlify dashboard → Site settings → Domain management
2. Add custom domain: `nd.dovydas.space`
3. Add DNS record at your domain provider:
   ```
   Type: CNAME
   Name: nd
   Value: <your-netlify-site-name>.netlify.app
   ```

#### Backend (Render)
1. Go to Render dashboard → Your service → Settings → Custom Domain
2. Add custom domain: `api.dovydas.space`
3. Add DNS record at your domain provider:
   ```
   Type: CNAME
   Name: api
   Value: <your-render-service>.onrender.com
   ```

### 6. Update Google OAuth

After custom domains are configured:

1. Go to https://console.cloud.google.com
2. Navigate to APIs & Services → Credentials
3. Update your OAuth 2.0 Client:
   - **Authorized JavaScript origins:**
     - `https://nd.dovydas.space`
   - **Authorized redirect URIs:**
     - `https://api.dovydas.space/auth/google/callback`
     - `https://nd.dovydas.space/auth/callback`

## 🔍 Troubleshooting

### Build fails at migrations step
**Error:** `django.core.exceptions.ImproperlyConfigured: No module named 'playwright'`

**Solution:** This shouldn't happen anymore! But if it does:
1. Check that `playwright==1.48.0` is in `requirements.txt`
2. Check Render build logs - Playwright should be installed

### Build fails with DATABASE_URL error
**Error:** `ValueError: Port could not be cast to integer value as 'port'`

**Solution:** Make sure you're using the correct Supabase connection string format:
- ✅ Use: `postgresql://postgres.kcixuytszyzgvcybxyym:IGnuxas123@aws-1-eu-north-1.pooler.supabase.com:5432/postgres`
- ❌ Don't use: Connection strings without port number

### Playwright browsers not installing
**Error:** `playwright._impl._errors.Error: Browser is not installed`

**Solution:** Add this to your build command in `render.yaml`:
```yaml
buildCommand: pip install -r requirements.txt && playwright install chromium && python manage.py collectstatic --noinput && python manage.py migrate
```

### Frontend shows 404 on page refresh
**Error:** Refreshing any route shows 404

**Solution:** This is already fixed! The `netlify.toml` and `_redirects` files handle this.

## 📊 Deployment Checklist

Use this checklist to track your deployment:

- [ ] Code changes committed and pushed to GitHub
- [ ] Render Blueprint created from repository
- [ ] Environment variables added to Render (DATABASE_URL, SUPABASE_*, ENCRYPTION_KEY, GOOGLE_*)
- [ ] Build successful on Render
- [ ] Migrations run successfully
- [ ] Backend accessible at your-service.onrender.com
- [ ] Frontend deployed to Netlify
- [ ] Frontend accessible at your-site.netlify.app
- [ ] Custom domain DNS configured for nd.dovydas.space
- [ ] Custom domain DNS configured for api.dovydas.space
- [ ] Custom domains verified in Netlify and Render
- [ ] Google OAuth credentials updated with new domains
- [ ] Test login flow works
- [ ] Test credential verification works (Manodienynas, Eduka)
- [ ] Test homework scraping works
- [ ] Test Google Tasks sync works

## 🎉 Success Indicators

After deployment, you should be able to:

1. **Access frontend:** https://nd.dovydas.space
2. **Access backend:** https://api.dovydas.space/health (should return status)
3. **Login with Google:** OAuth flow should work
4. **Add credentials:** Should be able to add Manodienynas/Eduka credentials
5. **Verify credentials:** Credential verification should work (now uses Playwright!)
6. **Scrape homework:** Should be able to manually trigger homework scraping
7. **Sync to Google Tasks:** Should sync homework to Google Tasks

## 📝 What Changed in This Deployment

### Backend Changes
- ✅ Removed all Selenium dependencies
- ✅ Converted credential verification to use Playwright
- ✅ Updated Celery tasks to use scrapers_simple
- ✅ All production code now uses requests or Playwright (no Selenium)

### Frontend Changes
- ✅ Already configured correctly (no changes needed)

### Infrastructure Changes
- ✅ Using Supabase PostgreSQL instead of Render PostgreSQL
- ✅ Database connection configured with SSL
- ✅ Blueprint updated for Supabase

## 🔗 Useful Links

- **Render Dashboard:** https://dashboard.render.com
- **Netlify Dashboard:** https://app.netlify.com
- **Supabase Dashboard:** https://supabase.com/dashboard
- **Google Cloud Console:** https://console.cloud.google.com
- **Frontend (after deploy):** https://nd.dovydas.space
- **Backend (after deploy):** https://api.dovydas.space

---

**Need help?** Check the detailed documentation:
- `SELENIUM_REMOVED.md` - Details of Selenium removal
- `RENDER_ENV_VARS_SUPABASE.md` - Environment variable reference
- `SUPABASE_DATABASE_SETUP.md` - Database setup guide
- `CUSTOM_DOMAIN_SETUP.md` - Custom domain configuration

**Ready to deploy?** Run the commands in Section 1 above! 🚀
