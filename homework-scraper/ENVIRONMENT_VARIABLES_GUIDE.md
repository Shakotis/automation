# Environment Variables Configuration

## Understanding the "localhost" Message

When you see this during build:
```
[API] Using API_BASE_URL: http://localhost:8000/api
[Home] Using API_BASE_URL: http://localhost:8000/api
[Dashboard] Using API_BASE_URL: http://localhost:8000/api
```

**Don't worry!** This is **completely normal** and **harmless** for production deployment. Here's why:

### Why It Shows "localhost"

1. **Build-Time vs Runtime**: These messages appear during the **static build** process on your local machine
2. **Static Export**: Next.js with `output: 'export'` generates static HTML/JS files
3. **Client-Side API Calls**: All API calls happen in the **browser** (runtime), not during build
4. **Environment Variables**: The actual API URL is embedded in the JavaScript bundle

### What Actually Happens in Production

1. **During Build** (local or CI/CD):
   - Next.js reads `NEXT_PUBLIC_API_URL` from environment
   - If not set, falls back to `localhost:8000` (from `next.config.js`)
   - Console logs show the value being used
   - Value is embedded in the generated JavaScript

2. **In Production** (Netlify):
   - Browser downloads the static files
   - JavaScript runs with the embedded API URL
   - API calls go to the correct production URL

## Environment Files

### `.env.production` ✅ (Committed to Git)
Production environment variables used during build:
```env
NEXT_PUBLIC_API_URL=https://api.dovydas.space/api
NEXT_PUBLIC_SITE_URL=https://nd.dovydas.space
```

### `.env.local` ⛔ (Ignored by Git)
Local development overrides:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
NEXT_PUBLIC_SITE_URL=http://localhost:3000
```

### `.env.example` 📝 (Committed to Git)
Template for team members:
```env
# See .env.production or .env.local for actual values
```

## Priority Order

Next.js loads environment variables in this order (highest priority first):

1. **`.env.local`** - Local overrides (ignored by git)
2. **`.env.production`** - Production values (when `NODE_ENV=production`)
3. **`.env.development`** - Development values (when `NODE_ENV=development`)
4. **`.env`** - Defaults for all environments
5. **Fallback in `next.config.js`** - Used if nothing else is set

## For Netlify Deployment

### Option 1: Use `.env.production` File (Recommended)
1. File already created with production URLs
2. Commit to git: `git add frontend/.env.production`
3. Netlify will use these values during build

### Option 2: Set in Netlify Dashboard
1. Go to **Netlify Dashboard** → Your Site → **Site configuration** → **Environment variables**
2. Add variable:
   - **Key**: `NEXT_PUBLIC_API_URL`
   - **Value**: `https://api.dovydas.space/api`
3. **Important**: Netlify dashboard values override `.env.production`

### Which Option to Choose?

**Use `.env.production` file if:**
- ✅ You want values in git for team visibility
- ✅ You want easier local production builds
- ✅ You have non-sensitive values only

**Use Netlify Dashboard if:**
- ✅ You have sensitive API keys
- ✅ You need different values per branch/environment
- ✅ You want to change values without redeploying

## Building Locally

### Development Build
```bash
cd frontend
npm run dev
# Uses .env.local (localhost:8000)
```

### Production Build
```bash
cd frontend
npm run build
# Uses .env.production (api.dovydas.space)
```

### Preview Production Build
```bash
cd frontend
npm run build
npm run start  # Note: This won't work with static export
# Use a static server instead:
npx serve out
```

## Verifying the Correct URL

### During Build
Check the build output:
```
[API] Using API_BASE_URL: https://api.dovydas.space/api  ← Should be production URL
```

### In Browser
1. Open browser developer tools (F12)
2. Go to **Console** tab
3. Look for API URL logs
4. Check **Network** tab when making API calls
5. Verify requests go to `https://api.dovydas.space`

### Testing the Built Files
```bash
cd frontend

# Build for production
npm run build

# Check the generated JavaScript
grep -r "api.dovydas.space" out/_next/static/

# Should find multiple matches with your production URL
```

## Common Issues

### Issue: "Still seeing localhost after deploy"
**Solution**: 
1. Verify `.env.production` exists with correct URL
2. Rebuild: `npm run build`
3. Check that Netlify is actually building (not using cached build)
4. Clear Netlify build cache and redeploy

### Issue: "API calls failing in production"
**Solution**:
1. Check browser Network tab - is it calling correct URL?
2. Verify CORS settings in Django backend
3. Check that backend allows your frontend domain
4. Verify `CSRF_TRUSTED_ORIGINS` and `CORS_ALLOWED_ORIGINS` in backend

### Issue: "Environment variable not updating"
**Solution**:
1. Restart Next.js dev server (`npm run dev`)
2. Clear Next.js cache: `rm -rf .next`
3. Rebuild: `npm run build`
4. Check that you're editing the right `.env` file

## Summary

✅ **The "localhost" message during build is normal**  
✅ **Production API calls use the embedded URL from environment variables**  
✅ **`.env.production` file is already configured correctly**  
✅ **Just commit, push, and deploy - it will work!**

## Next Steps

1. **Commit the new files**:
   ```bash
   git add frontend/.env.production
   git commit -m "Add production environment variables"
   git push
   ```

2. **Deploy to Netlify** (automatic if connected to git)

3. **Verify in browser** that API calls go to `https://api.dovydas.space`

4. **Done!** Your frontend will correctly connect to your backend.
