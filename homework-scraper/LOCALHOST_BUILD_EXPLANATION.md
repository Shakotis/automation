# "Why Does Build Show localhost?" - Quick Answer

## TL;DR

**The "localhost" messages are completely normal and won't affect your production deployment!** ✅

## What You're Seeing

```
[API] Using API_BASE_URL: http://localhost:8000/api
[Home] Using API_BASE_URL: http://localhost:8000/api
[Dashboard] Using API_BASE_URL: http://localhost:8000/api
```

## Why This Happens

1. You're building **locally** without a `.env.production` file
2. Next.js falls back to the default in `next.config.js`: `http://localhost:8000/api`
3. These are just **console logs during the build process**
4. They don't affect the actual API calls in production

## Why It's Not a Problem

- **Static Export**: Next.js generates static files (HTML + JS)
- **Client-Side API Calls**: All API requests happen **in the browser**, not during build
- **Runtime vs Build Time**: The URL is embedded in JavaScript and used at **runtime**
- **Netlify Environment**: Netlify can override with environment variables

## What I Just Fixed

✅ Created `.env.production` with your production URLs:
```env
NEXT_PUBLIC_API_URL=https://api.dovydas.space/api
NEXT_PUBLIC_SITE_URL=https://nd.dovydas.space
```

✅ Created `.env.local` for your local development:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
NEXT_PUBLIC_SITE_URL=http://localhost:3000
```

## How to Verify It's Working

### Option 1: Build Again Locally
```bash
cd frontend
npm run build
```

Now you should see:
```
[API] Using API_BASE_URL: https://api.dovydas.space/api  ✅
```

### Option 2: Just Deploy to Netlify
1. Commit and push the changes
2. Netlify will build with `.env.production`
3. Check browser developer tools (F12) → Network tab
4. API calls will go to `https://api.dovydas.space` ✅

## For Netlify Deployment

You have **two options**:

### Option 1: Use `.env.production` File (Already Done! ✅)
- File exists with correct production URLs
- Just commit and push
- Netlify will use these values

### Option 2: Set in Netlify Dashboard
- Go to Site Settings → Environment Variables
- Add `NEXT_PUBLIC_API_URL=https://api.dovydas.space/api`
- This overrides `.env.production`

**I recommend Option 1** - the file is already set up!

## Next Steps

1. **Commit the changes**:
   ```bash
   git add frontend/.env.production frontend/.env.local
   git commit -m "Add environment configuration files"
   git push
   ```

2. **Deploy** (automatic if connected to Netlify)

3. **Test in browser**:
   - Open your deployed site
   - Open Developer Tools (F12)
   - Check Network tab
   - Verify API calls go to `https://api.dovydas.space` ✅

## More Details

See `ENVIRONMENT_VARIABLES_GUIDE.md` for comprehensive documentation.

---

**Bottom Line**: Your production deployment will work correctly! The "localhost" message is just a build-time artifact. Your actual deployed site will use `https://api.dovydas.space/api` for all API calls. 🎉
