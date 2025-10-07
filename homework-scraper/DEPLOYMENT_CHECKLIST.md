# Deployment Checklist ✅

Quick reference for deploying to Netlify + Render.

## Before You Start

- [ ] Code pushed to GitHub
- [ ] Google OAuth credentials ready
- [ ] Generated encryption key (32 bytes)
- [ ] Render account created
- [ ] Netlify account created

## Backend (Render) - Step by Step

### 1. Create Services
- [ ] PostgreSQL database created
- [ ] Redis instance created
- [ ] Web service created (Django)
- [ ] Celery worker created
- [ ] Celery beat created

### 2. Environment Variables Set
- [ ] `SECRET_KEY` (generate in Render)
- [ ] `DATABASE_URL` (from PostgreSQL)
- [ ] `REDIS_URL` (from Redis)
- [ ] `GOOGLE_OAUTH2_CLIENT_ID`
- [ ] `GOOGLE_OAUTH2_CLIENT_SECRET`
- [ ] `ENCRYPTION_KEY` (your generated key)
- [ ] `DJANGO_SETTINGS_MODULE=homework_scraper.settings_production`
- [ ] `ALLOWED_HOSTS=.onrender.com`
- [ ] `PLAYWRIGHT_BROWSERS_PATH=/opt/render/.cache/ms-playwright`

### 3. Verify Backend
- [ ] Build completed successfully
- [ ] Web service is running
- [ ] Health check passes: `/api/health`
- [ ] Django admin accessible
- [ ] Created superuser

## Frontend (Netlify) - Step by Step

### 1. Deploy
- [ ] Site created from GitHub repo
- [ ] Base directory set to `frontend`
- [ ] Build command: `npm run build`
- [ ] Publish directory: `.next`

### 2. Environment Variables Set
- [ ] `NEXT_PUBLIC_API_URL` (your Render backend URL)
- [ ] `NEXT_PUBLIC_GOOGLE_CLIENT_ID`

### 3. Update Backend CORS
- [ ] Updated `CORS_ALLOWED_ORIGINS` with Netlify URL
- [ ] Updated `CSRF_TRUSTED_ORIGINS` with Netlify URL
- [ ] Backend redeployed

### 4. Verify Frontend
- [ ] Site loads successfully
- [ ] Can access API through proxy
- [ ] No CORS errors in console

## Post-Deployment

### Google OAuth
- [ ] Added Netlify URL to authorized origins
- [ ] Added Netlify URL to redirect URIs
- [ ] Added Render URL to authorized origins
- [ ] Tested Google login

### Testing
- [ ] Can create account
- [ ] Can login with Google
- [ ] Can add credentials
- [ ] Scraping works (Manodienynas)
- [ ] Scraping works (Eduka)
- [ ] Tasks appear in frontend
- [ ] Auto-scraping runs (check Celery Beat logs)

### Optional
- [ ] Custom domain configured
- [ ] Monitoring setup
- [ ] Backup strategy in place
- [ ] Upgraded from free tier (if needed)

## Common Issues & Fixes

### Backend won't start
- Check `DEBUG=False` in env vars
- Verify all required env vars are set
- Check build logs for errors
- Ensure `build.sh` has execute permissions

### Frontend can't reach API
- Verify `NEXT_PUBLIC_API_URL` is correct
- Check CORS settings on backend
- Look for errors in browser console
- Check Netlify function logs

### Playwright errors
- Ensure `playwright install chromium` in build
- Set `PLAYWRIGHT_BROWSERS_PATH` env var
- Check Render logs for browser installation

### Database connection issues
- Verify `DATABASE_URL` is set
- Check PostgreSQL service is running
- Ensure web service is in same region

## Deployment URLs

Update these with your actual URLs:

```
Backend (Render):  https://_____________________.onrender.com
Frontend (Netlify): https://_____________________.netlify.app
Database:          (internal only)
Redis:             (internal only)
```

## Commands Reference

### Render Shell
```bash
# Create superuser
python manage.py createsuperuser

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --no-input

# Check Celery
celery -A homework_scraper inspect active
```

### Netlify CLI
```bash
# Deploy
netlify deploy --prod

# Check logs
netlify logs

# Open site
netlify open:site
```

### Local Testing
```bash
# Test with production settings
cd backend
DJANGO_SETTINGS_MODULE=homework_scraper.settings_production python manage.py check --deploy

# Build frontend
cd frontend
npm run build
npm start
```

---

**Ready to Deploy?** Follow the detailed guide in [DEPLOYMENT.md](./DEPLOYMENT.md)
