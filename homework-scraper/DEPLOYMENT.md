# Deployment Guide: Netlify + Render

This guide will walk you through deploying the Homework Scraper application with:
- **Frontend (Next.js)** → Netlify
- **Backend (Django)** → Render.com

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Backend Deployment (Render)](#backend-deployment-render)
3. [Frontend Deployment (Netlify)](#frontend-deployment-netlify)
4. [Post-Deployment Setup](#post-deployment-setup)
5. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Accounts
- [ ] GitHub account (for code repository)
- [ ] Render account (https://render.com - free tier available)
- [ ] Netlify account (https://netlify.com - free tier available)
- [ ] Google Cloud Console (for OAuth credentials)

### Required Information
- [ ] Google OAuth Client ID & Secret
- [ ] Supabase credentials (if using)
- [ ] Encryption key (32-byte random string)

### Generate Encryption Key
```bash
# Python
python -c "import secrets; print(secrets.token_hex(32))"

# OR OpenSSL
openssl rand -hex 32
```

---

## Backend Deployment (Render)

### Step 1: Push Code to GitHub

```bash
cd homework-scraper
git add .
git commit -m "Prepare for production deployment"
git push origin main
```

### Step 2: Create Render Services

#### Option A: Using Blueprint (render.yaml) - RECOMMENDED

1. Go to https://render.com
2. Click **"New"** → **"Blueprint"**
3. Connect your GitHub repository
4. Select the repository: `homework-scraper`
5. Render will detect `render.yaml` and create all services:
   - Web Service (Django)
   - PostgreSQL Database
   - Redis
   - Celery Worker
   - Celery Beat

6. Review the services and click **"Apply"**

#### Option B: Manual Setup

If you prefer manual setup or blueprint doesn't work:

##### 2.1 Create PostgreSQL Database

1. Click **"New"** → **"PostgreSQL"**
2. Name: `homework-scraper-db`
3. Database: `homework_scraper`
4. User: `homework_user`
5. Region: `Oregon` (or closest to you)
6. Plan: **Free**
7. Click **"Create Database"**
8. **Save the connection string** (Internal Database URL)

##### 2.2 Create Redis Instance

1. Click **"New"** → **"Redis"**
2. Name: `homework-scraper-redis`
3. Region: Same as database
4. Plan: **Free**
5. Click **"Create Redis"**
6. **Save the connection string**

##### 2.3 Create Web Service (Django)

1. Click **"New"** → **"Web Service"**
2. Connect your GitHub repository
3. Configuration:
   - **Name**: `homework-scraper-backend`
   - **Region**: Same as database
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3`
   - **Build Command**: 
     ```bash
     chmod +x build.sh && ./build.sh
     ```
   - **Start Command**: 
     ```bash
     gunicorn homework_scraper.wsgi:application --bind 0.0.0.0:$PORT
     ```
   - **Plan**: **Free**

4. Click **"Advanced"** and add environment variables (see below)

##### 2.4 Add Environment Variables

Add these in the Render Dashboard under **Environment** tab:

```bash
# Django
SECRET_KEY=<generate-with-render-or-use-your-own>
DEBUG=False
DJANGO_SETTINGS_MODULE=homework_scraper.settings_production
ALLOWED_HOSTS=.onrender.com
PYTHON_VERSION=3.11

# Database (from Step 2.1)
DATABASE_URL=<your-postgres-internal-url>

# Redis (from Step 2.2)
REDIS_URL=<your-redis-internal-url>
CELERY_BROKER_URL=<your-redis-internal-url>
CELERY_RESULT_BACKEND=<your-redis-internal-url>

# CORS (will update after Netlify deployment)
CORS_ALLOWED_ORIGINS=http://localhost:3000
CSRF_TRUSTED_ORIGINS=https://your-backend.onrender.com

# Google OAuth
GOOGLE_OAUTH2_CLIENT_ID=<your-google-client-id>
GOOGLE_OAUTH2_CLIENT_SECRET=<your-google-client-secret>

# Encryption
ENCRYPTION_KEY=<your-32-byte-hex-string>

# Supabase (optional)
SUPABASE_URL=<your-supabase-url>
SUPABASE_KEY=<your-supabase-key>

# Playwright
PLAYWRIGHT_BROWSERS_PATH=/opt/render/.cache/ms-playwright
```

5. Click **"Create Web Service"**

##### 2.5 Create Celery Worker

1. Click **"New"** → **"Background Worker"**
2. Same repository and branch
3. Configuration:
   - **Name**: `homework-scraper-celery`
   - **Root Directory**: `backend`
   - **Build Command**: Same as web service
   - **Start Command**:
     ```bash
     celery -A homework_scraper worker --loglevel=info --concurrency=2
     ```
4. Add same environment variables (except CORS)

##### 2.6 Create Celery Beat

1. Click **"New"** → **"Background Worker"**
2. Same repository and branch
3. Configuration:
   - **Name**: `homework-scraper-celery-beat`
   - **Root Directory**: `backend`
   - **Start Command**:
     ```bash
     celery -A homework_scraper beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler
     ```
4. Add same environment variables

### Step 3: Verify Backend Deployment

1. Wait for all services to deploy (5-10 minutes)
2. Check the web service logs for errors
3. Visit your backend URL: `https://your-backend.onrender.com/api/health`
4. Should see: `{"status": "ok"}`

### Step 4: Run Initial Setup

Connect to your web service shell:

```bash
# In Render Dashboard → Shell
python manage.py createsuperuser
```

---

## Frontend Deployment (Netlify)

### Step 1: Prepare Frontend

1. Update `frontend/.env.production`:
```bash
NEXT_PUBLIC_API_URL=https://your-backend.onrender.com/api
NEXT_PUBLIC_GOOGLE_CLIENT_ID=<your-google-client-id>
```

2. Commit changes:
```bash
git add .
git commit -m "Configure frontend for production"
git push origin main
```

### Step 2: Deploy to Netlify

#### Option A: Using Netlify UI

1. Go to https://netlify.com
2. Click **"Add new site"** → **"Import an existing project"**
3. Connect to GitHub
4. Select your repository: `homework-scraper`
5. Configure build settings:
   - **Base directory**: `frontend`
   - **Build command**: `npm run build`
   - **Publish directory**: `.next`
6. Click **"Deploy site"**

#### Option B: Using Netlify CLI

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Login
netlify login

# Deploy from frontend directory
cd frontend
netlify init
netlify deploy --prod
```

### Step 3: Configure Environment Variables

1. In Netlify Dashboard, go to **Site settings** → **Environment variables**
2. Add variables:
```bash
NEXT_PUBLIC_API_URL=https://your-backend.onrender.com/api
NEXT_PUBLIC_GOOGLE_CLIENT_ID=<your-google-client-id>
```

3. Click **"Save"**

### Step 4: Update Backend CORS Settings

Now that you have your Netlify URL, update backend environment variables:

1. Go to Render Dashboard
2. Select your web service
3. Update environment variables:
```bash
CORS_ALLOWED_ORIGINS=https://your-app.netlify.app,http://localhost:3000
CSRF_TRUSTED_ORIGINS=https://your-app.netlify.app,https://your-backend.onrender.com
```

4. Click **"Save Changes"** (this will redeploy)

### Step 5: Update Netlify Redirects

1. Update `frontend/netlify.toml`:
```toml
[[redirects]]
  from = "/api/*"
  to = "https://your-backend.onrender.com/api/:splat"
  status = 200
  force = false
```

2. Commit and push:
```bash
git add frontend/netlify.toml
git commit -m "Update API proxy URL"
git push origin main
```

Netlify will auto-deploy the changes.

---

## Post-Deployment Setup

### 1. Update Google OAuth Redirect URIs

In Google Cloud Console → Credentials → OAuth 2.0 Client:

**Authorized JavaScript origins:**
- `https://your-app.netlify.app`
- `https://your-backend.onrender.com`

**Authorized redirect URIs:**
- `https://your-app.netlify.app/auth/callback`
- `https://your-backend.onrender.com/api/auth/google/callback`

### 2. Test the Application

1. Visit: `https://your-app.netlify.app`
2. Try logging in with Google
3. Add credentials for Manodienynas/Eduka
4. Verify scraping works
5. Check that scheduled tasks run (Celery Beat)

### 3. Setup Custom Domain (Optional)

#### For Netlify:
1. Netlify Dashboard → **Domain settings**
2. Add custom domain
3. Update DNS records

#### For Render:
1. Render Dashboard → **Settings** → **Custom Domains**
2. Add domain and verify

### 4. Enable HTTPS (Automatic)

Both Netlify and Render automatically provision SSL certificates.
- Netlify: Uses Let's Encrypt
- Render: Uses Let's Encrypt

### 5. Setup Monitoring

#### Render:
- Built-in metrics and logs
- View logs: Dashboard → Your service → **Logs**

#### Netlify:
- Analytics in dashboard
- Deploy logs and functions logs available

### 6. Configure Auto-Deploy

Both platforms support auto-deploy from GitHub:
- **Netlify**: Enabled by default
- **Render**: Enabled by default

Pushing to `main` branch triggers redeployment.

---

## Troubleshooting

### Backend Issues

#### 1. "ModuleNotFoundError" during build
```bash
# Make sure all dependencies are in requirements.txt
pip freeze > requirements.txt
git add requirements.txt
git commit -m "Update requirements"
git push
```

#### 2. Database connection errors
- Verify `DATABASE_URL` environment variable is set correctly
- Check that PostgreSQL service is running
- Ensure web service can connect to database (same region helps)

#### 3. Static files not loading
```bash
# In Render shell
python manage.py collectstatic --no-input --clear
```

#### 4. Celery not processing tasks
- Check that Redis URL is correct in all services
- Verify Celery worker is running (check logs)
- Ensure Beat scheduler is running for periodic tasks

#### 5. Playwright browser not found
```bash
# Add to build command in render.yaml or build.sh
playwright install chromium
```

### Frontend Issues

#### 1. "API request failed"
- Check `NEXT_PUBLIC_API_URL` is correct
- Verify backend is running and accessible
- Check CORS settings on backend
- Look at browser console for CORS errors

#### 2. Build fails on Netlify
```bash
# Clear cache and rebuild
# In Netlify: Deploy settings → Clear cache and deploy
```

#### 3. Environment variables not updating
- After changing env vars in Netlify, trigger new deploy
- Or redeploy from Netlify Dashboard

#### 4. 404 on page refresh
- This should be handled by `netlify.toml` redirects
- Verify `netlify.toml` is in `frontend/` directory

### CORS Issues

If you see CORS errors:

1. **Backend** - Update Django settings:
```python
CORS_ALLOWED_ORIGINS = [
    'https://your-app.netlify.app',
    'http://localhost:3000',
]

CSRF_TRUSTED_ORIGINS = [
    'https://your-app.netlify.app',
    'https://your-backend.onrender.com',
]
```

2. **Netlify Proxy** - Make sure redirect in `netlify.toml` is correct

3. **Credentials** - Ensure both have:
```python
CORS_ALLOW_CREDENTIALS = True
```

---

## Performance Optimization

### Backend (Render)

1. **Upgrade Plan**: Free tier sleeps after inactivity
   - Consider **Starter** plan ($7/month) for production
   - No sleep, more resources

2. **Database Connection Pooling**: Already configured with `conn_max_age=600`

3. **Caching**: Consider adding Redis caching for API responses

4. **Gunicorn Workers**: Adjust based on plan
   - Free: `--workers 1`
   - Starter: `--workers 2`
   - Standard: `--workers 4`

### Frontend (Netlify)

1. **Next.js Optimization**: Already using latest Next.js 15

2. **Image Optimization**: Enabled in `next.config.js`

3. **Caching**: Headers configured in `netlify.toml`

---

## Cost Estimate

### Free Tier (Development)
- **Netlify**: Free (100GB bandwidth, 300 build minutes/month)
- **Render Web Service**: Free (750 hours/month, sleeps after 15min inactivity)
- **Render PostgreSQL**: Free (1GB storage, expires after 90 days)
- **Render Redis**: Free (25MB storage)
- **Total**: $0/month

### Paid Tier (Production)
- **Netlify Pro**: $19/month (more bandwidth, team features)
- **Render Starter**: $7/month per service (no sleep)
  - Web Service: $7
  - Worker: $7
  - PostgreSQL: $7
  - Redis: $0 (free tier sufficient)
- **Total**: ~$40/month

### Recommended for Production
- Start with Render free tier + Netlify free tier
- Upgrade Render web service to Starter when needed ($7)
- PostgreSQL free tier is fine for small user base
- Upgrade as needed based on usage

---

## Backup Strategy

### Database Backups (Render)

1. **Manual Backup**:
```bash
# In Render shell or local with DATABASE_URL
pg_dump $DATABASE_URL > backup.sql
```

2. **Automated Backups**: Available on paid PostgreSQL plans

### Alternative: Use Supabase for Storage
- Free tier includes automatic backups
- More reliable for production
- Consider migrating from SQLite/PostgreSQL to Supabase

---

## Next Steps

1. [ ] Deploy backend to Render
2. [ ] Deploy frontend to Netlify
3. [ ] Update Google OAuth redirect URIs
4. [ ] Test full application flow
5. [ ] Setup monitoring and alerts
6. [ ] Configure custom domains (optional)
7. [ ] Plan for backups
8. [ ] Consider upgrading from free tier

---

## Support & Resources

- **Render Docs**: https://render.com/docs
- **Netlify Docs**: https://docs.netlify.com
- **Django Production Checklist**: https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/
- **Next.js Deployment**: https://nextjs.org/docs/deployment

---

**Deployment Date**: {{ date }}  
**Last Updated**: {{ date }}  
**Status**: Ready for Production ✅
