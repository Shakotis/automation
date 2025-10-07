# Quick Start Guide - Visual 🚀

## Step 1: Prepare (5 minutes)

```
┌─────────────────────────────────────────┐
│  Generate Encryption Key                │
│                                         │
│  $ openssl rand -hex 32                 │
│                                         │
│  Copy output → Save for later          │
└─────────────────────────────────────────┘
```

## Step 2: Deploy Backend to Render (10-15 minutes)

```
┌──────────────────────────────────────────────────────────┐
│  render.com → New → Blueprint                            │
│                                                          │
│  1. Connect GitHub                                       │
│  2. Select: homework-scraper repo                        │
│  3. Render detects render.yaml                           │
│  4. Creates 5 services automatically:                    │
│     ✓ Web Service (Django)                              │
│     ✓ PostgreSQL Database                               │
│     ✓ Redis                                             │
│     ✓ Celery Worker                                     │
│     ✓ Celery Beat                                       │
│                                                          │
│  5. Add environment variables:                           │
│     - GOOGLE_OAUTH2_CLIENT_ID                           │
│     - GOOGLE_OAUTH2_CLIENT_SECRET                       │
│     - ENCRYPTION_KEY (from Step 1)                      │
│                                                          │
│  6. Click "Apply"                                        │
│                                                          │
│  Wait 5-10 minutes for deployment...                    │
│                                                          │
│  ✅ Backend deployed!                                    │
│  URL: https://your-backend.onrender.com                 │
└──────────────────────────────────────────────────────────┘
```

## Step 3: Deploy Frontend to Netlify (5-10 minutes)

```
┌──────────────────────────────────────────────────────────┐
│  netlify.com → New site from Git                         │
│                                                          │
│  1. Connect GitHub                                       │
│  2. Select: homework-scraper repo                        │
│  3. Configure:                                           │
│     Base directory: frontend                             │
│     Build command: npm run build                         │
│     Publish directory: .next                             │
│                                                          │
│  4. Add environment variables:                           │
│     NEXT_PUBLIC_API_URL=                                │
│       https://your-backend.onrender.com/api             │
│     NEXT_PUBLIC_GOOGLE_CLIENT_ID=                       │
│       (your google client id)                           │
│                                                          │
│  5. Click "Deploy site"                                  │
│                                                          │
│  Wait 3-5 minutes for deployment...                     │
│                                                          │
│  ✅ Frontend deployed!                                   │
│  URL: https://your-app.netlify.app                      │
└──────────────────────────────────────────────────────────┘
```

## Step 4: Connect Frontend & Backend (5 minutes)

```
┌──────────────────────────────────────────────────────────┐
│  Update Backend CORS                                     │
│                                                          │
│  1. Go to Render → Your web service                      │
│  2. Environment tab                                      │
│  3. Update:                                              │
│                                                          │
│     CORS_ALLOWED_ORIGINS=                               │
│       https://your-app.netlify.app,http://localhost:3000│
│                                                          │
│     CSRF_TRUSTED_ORIGINS=                               │
│       https://your-app.netlify.app                      │
│                                                          │
│  4. Save (triggers redeploy)                            │
│                                                          │
│  ✅ Frontend can now talk to backend!                   │
└──────────────────────────────────────────────────────────┘
```

## Step 5: Configure Google OAuth (5 minutes)

```
┌──────────────────────────────────────────────────────────┐
│  console.cloud.google.com → Credentials                  │
│                                                          │
│  1. Select your OAuth 2.0 Client                         │
│  2. Add Authorized JavaScript origins:                   │
│     - https://your-app.netlify.app                      │
│     - https://your-backend.onrender.com                 │
│                                                          │
│  3. Add Authorized redirect URIs:                        │
│     - https://your-app.netlify.app/auth/callback        │
│     - https://your-backend.onrender.com/api/auth/...    │
│                                                          │
│  4. Save                                                 │
│                                                          │
│  ✅ Google OAuth configured!                            │
└──────────────────────────────────────────────────────────┘
```

## Step 6: Test Everything (10 minutes)

```
┌──────────────────────────────────────────────────────────┐
│  Testing Checklist                                       │
│                                                          │
│  Open: https://your-app.netlify.app                     │
│                                                          │
│  ✓ Site loads                                           │
│  ✓ Login with Google works                              │
│  ✓ Can access dashboard                                 │
│  ✓ Add Manodienynas credentials                         │
│  ✓ Add Eduka credentials                                │
│  ✓ Click "Scrape Now"                                   │
│  ✓ Homework appears                                     │
│  ✓ No errors in browser console                         │
│                                                          │
│  Backend Check:                                          │
│  Visit: https://your-backend.onrender.com/api/health    │
│  Should see: {"status": "ok"}                           │
│                                                          │
│  ✅ Everything works!                                    │
└──────────────────────────────────────────────────────────┘
```

## Visual Architecture

```
           USERS
             │
             ▼
    ┌────────────────┐
    │    NETLIFY     │  ← Frontend (Next.js)
    │   CDN Global   │    
    └────────┬───────┘
             │ HTTPS
             ▼
    ┌────────────────┐
    │     RENDER     │  ← Backend (Django)
    ├────────────────┤
    │  Web Service   │  ← API + Auth + Scrapers
    ├────────────────┤
    │ Celery Worker  │  ← Background Tasks
    ├────────────────┤
    │ Celery Beat    │  ← Scheduled Scraping
    ├────────────────┤
    │  PostgreSQL    │  ← Database
    ├────────────────┤
    │     Redis      │  ← Task Queue
    └────────────────┘
```

## Timeline

```
Total Time: ~40-50 minutes

Prepare          ████░░░░░░  5 min
Backend Deploy   ████████░░  15 min
Frontend Deploy  ██████░░░░  10 min
Connect          ████░░░░░░  5 min
OAuth Setup      ████░░░░░░  5 min
Testing          ████████░░  10 min
                 ──────────
                 50 minutes
```

## Cost Timeline

```
FREE TIER:
Month 1-3: $0/month  ✨
  - Full functionality
  - Backend sleeps after 15min inactivity
  - 90-day database limit

UPGRADE TO PRODUCTION:
Month 4+: $40/month  💼
  - No backend sleep
  - Unlimited database
  - Better performance
```

## Help?

```
┌─────────────────────────────────┐
│  Stuck? Check these:            │
│                                 │
│  📖 DEPLOYMENT.md              │
│     Full detailed guide         │
│                                 │
│  ✅ DEPLOYMENT_CHECKLIST.md    │
│     Quick reference             │
│                                 │
│  ❓ Troubleshooting section    │
│     Common issues & fixes       │
└─────────────────────────────────┘
```

## Success! 🎉

```
┌──────────────────────────────────────────┐
│  🎊 Your app is now live!               │
│                                          │
│  Frontend: https://your-app.netlify.app  │
│  Backend:  https://your-backend...       │
│                                          │
│  ✅ Automatic scraping enabled          │
│  ✅ SSL certificates active             │
│  ✅ Auto-deploy from GitHub             │
│                                          │
│  Ready for users! 🚀                    │
└──────────────────────────────────────────┘
```

---

**Next Steps:**
1. Share your app URL with users
2. Monitor logs for first 24 hours
3. Consider upgrading to paid tier when needed
4. Enjoy your deployed homework scraper! 🎓
