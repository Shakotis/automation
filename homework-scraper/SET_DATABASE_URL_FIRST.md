# 🚨 CRITICAL: Set DATABASE_URL BEFORE Deploying!

## ⚠️ The Problem

The build is failing because `DATABASE_URL` is not set when the service tries to build for the first time.

**Error:**
```
ValueError: DATABASE_URL environment variable is not set.
```

## ✅ The Solution

You MUST set the environment variable **BEFORE** or **IMMEDIATELY AFTER** creating the service.

---

## 🎯 Correct Deployment Order

### Step 1: Commit & Push

```powershell
cd w:\automation\homework-scraper
git add .
git commit -m "Configure Supabase database and fix Netlify 404"
git push origin main
```

---

### Step 2: Deploy to Render with Blueprint

1. Go to: https://dashboard.render.com
2. Click **"New"** → **"Blueprint"**
3. Select repository: `Shakotis/automation`
4. Click **"Apply Blueprint"**

⚠️ **Services will be created but will FAIL to build initially** - This is expected!

---

### Step 3: Set Environment Variables IMMEDIATELY

**For `homework-scraper-backend` service:**

1. Click on the service (it will show "Build failed" - that's OK!)
2. Go to **"Environment"** tab
3. Click **"Add Environment Variable"**
4. Add **ALL** of these:

```bash
# DATABASE CONNECTION (REQUIRED!)
DATABASE_URL
postgresql://postgres:3BH6CyUl5OpWDqtD@db.kcixuytszyzgvcybxyym.supabase.co:5432/postgres

# SUPABASE CONFIGURATION
SUPABASE_URL
https://kcixuytszyzgvcybxyym.supabase.co

SUPABASE_KEY
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtjaXh1eXRzenl6Z3ZjeWJ4eXltIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTkxODY3NjYsImV4cCI6MjA3NDc2Mjc2Nn0.SQO1ni7OKTWSb76nFbgUwY50CDL4UfW8pW8VA7Fsnwg

SUPABASE_SERVICE_KEY
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtjaXh1eXRzenl6Z3ZjeWJ4eXltIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1OTE4Njc2NiwiZXhwIjoyMDc0NzYyNzY2fQ.bsUDTLD5__idVQuv5SeqQO9wxL-ZpNVRPWAhF16XQkk

# ENCRYPTION KEY
ENCRYPTION_KEY
[Click "Generate Value" button]

# GOOGLE OAUTH (if you have them)
GOOGLE_OAUTH2_CLIENT_ID
[Your Google Client ID]

GOOGLE_OAUTH2_CLIENT_SECRET
[Your Google Client Secret]
```

5. Click **"Save Changes"**
6. This will **automatically trigger a rebuild** ✅

---

### Step 4: Set Variables for Worker Services

**For `homework-scraper-celery`:**

1. Go to the service → Environment tab
2. Add these:

```bash
DATABASE_URL
postgresql://postgres:3BH6CyUl5OpWDqtD@db.kcixuytszyzgvcybxyym.supabase.co:5432/postgres

SUPABASE_URL
https://kcixuytszyzgvcybxyym.supabase.co

SUPABASE_KEY
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtjaXh1eXRzenl6Z3ZjeWJ4eXltIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTkxODY3NjYsImV4cCI6MjA3NDc2Mjc2Nn0.SQO1ni7OKTWSb76nFbgUwY50CDL4UfW8pW8VA7Fsnwg

SECRET_KEY
[Copy from homework-scraper-backend after it's generated]

ENCRYPTION_KEY
[Copy from homework-scraper-backend]
```

**For `homework-scraper-celery-beat`:**

Same as above, minus `ENCRYPTION_KEY`:

```bash
DATABASE_URL
postgresql://postgres:3BH6CyUl5OpWDqtD@db.kcixuytszyzgvcybxyym.supabase.co:5432/postgres

SUPABASE_URL
https://kcixuytszyzgvcybxyym.supabase.co

SUPABASE_KEY
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtjaXh1eXRzenl6Z3ZjeWJ4eXltIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTkxODY3NjYsImV4cCI6MjA3NDc2Mjc2Nn0.SQO1ni7OKTWSb76nFbgUwY50CDL4UfW8pW8VA7Fsnwg

SECRET_KEY
[Copy from homework-scraper-backend]
```

---

### Step 5: Wait for Build

⏱️ **Time:** 5-8 minutes

Watch the logs in `homework-scraper-backend`:
- Should show migrations running
- Should complete successfully
- Service should show "Live" (green dot)

---

## 🔑 Why This Happens

In `render.yaml`, we set:

```yaml
- key: DATABASE_URL
  sync: false  # This means: "Don't auto-set, user will add manually"
```

This is intentional because:
1. We don't want to commit sensitive credentials to Git
2. Render can't auto-populate Supabase credentials (it's external)
3. You must add them manually in the dashboard

---

## 📝 Your Database Credentials

You have **TWO** connection strings from Supabase. Both work, but use the **direct** one for simplicity:

### ✅ RECOMMENDED: Direct Connection
```
postgresql://postgres:3BH6CyUl5OpWDqtD@db.kcixuytszyzgvcybxyym.supabase.co:5432/postgres
```
- Port: 5432 (standard PostgreSQL)
- Simpler, more reliable
- Good for most use cases

### Alternative: Pooled Connection
```
postgresql://postgres.kcixuytszyzgvcybxyym:IGnuxas123@aws-1-eu-north-1.pooler.supabase.com:5432/postgres
```
- Uses connection pooler (PgBouncer)
- Better for high traffic
- Slightly more complex

**For now, use the direct connection!**

---

## ✅ Verification

After adding variables and redeploying:

### Check Build Logs:
```
Installing Python dependencies... ✓
Installing Playwright browsers... ✓
Collecting static files... ✓
Running database migrations... ✓
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  ...
Build complete! ✓
```

### Check Health Endpoint:
```
https://homework-scraper-backend.onrender.com/api/health
→ {"status": "ok"} ✅
```

### Check Supabase Dashboard:
```
https://supabase.com/dashboard/project/kcixuytszyzgvcybxyym/editor
→ See Django tables created ✅
```

---

## 🐛 Troubleshooting

### Still Getting DATABASE_URL Error?

**Check:**
1. Variable name is EXACTLY: `DATABASE_URL` (case-sensitive)
2. No extra spaces before/after the connection string
3. Connection string starts with: `postgresql://`
4. You clicked "Save Changes" after adding variables

**Try:**
- Copy the connection string again (might have typo)
- Use direct connection instead of pooled
- Check Supabase project is active (not paused)

### Build Still Failing After Adding Variables?

**Solution:**
1. Go to service → Events tab
2. Click **"Manual Deploy"** → **"Deploy latest commit"**
3. This forces a fresh build with the new variables

### SSL Connection Error?

**Solution:**
The settings now include `ssl_require=True` automatically.
If you still get SSL errors, add `?sslmode=require` to the connection string:

```
postgresql://postgres:3BH6CyUl5OpWDqtD@db.kcixuytszyzgvcybxyym.supabase.co:5432/postgres?sslmode=require
```

---

## 📊 Complete Environment Variables Checklist

### Before Build Can Succeed:

**homework-scraper-backend:**
- [x] `DATABASE_URL` (CRITICAL!)
- [x] `SUPABASE_URL`
- [x] `SUPABASE_KEY`
- [x] `SUPABASE_SERVICE_KEY`
- [x] `ENCRYPTION_KEY` (Generate in Render)
- [ ] `GOOGLE_OAUTH2_CLIENT_ID` (Optional for now)
- [ ] `GOOGLE_OAUTH2_CLIENT_SECRET` (Optional for now)

**homework-scraper-celery:**
- [x] `DATABASE_URL` (CRITICAL!)
- [x] `SUPABASE_URL`
- [x] `SUPABASE_KEY`
- [ ] `SECRET_KEY` (Copy from backend after it builds)
- [ ] `ENCRYPTION_KEY` (Copy from backend)

**homework-scraper-celery-beat:**
- [x] `DATABASE_URL` (CRITICAL!)
- [x] `SUPABASE_URL`
- [x] `SUPABASE_KEY`
- [ ] `SECRET_KEY` (Copy from backend after it builds)

---

## 🎯 Quick Copy-Paste

**For fast deployment, copy this and paste values in Render:**

```
DATABASE_URL=postgresql://postgres:3BH6CyUl5OpWDqtD@db.kcixuytszyzgvcybxyym.supabase.co:5432/postgres
SUPABASE_URL=https://kcixuytszyzgvcybxyym.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtjaXh1eXRzenl6Z3ZjeWJ4eXltIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTkxODY3NjYsImV4cCI6MjA3NDc2Mjc2Nn0.SQO1ni7OKTWSb76nFbgUwY50CDL4UfW8pW8VA7Fsnwg
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtjaXh1eXRzenl6Z3ZjeWJ4eXltIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1OTE4Njc2NiwiZXhwIjoyMDc0NzYyNzY2fQ.bsUDTLD5__idVQuv5SeqQO9wxL-ZpNVRPWAhF16XQkk
```

**Then click "Generate Value" for:**
```
ENCRYPTION_KEY
```

---

## 🚀 Summary

**The key point:** You can't use `render.yaml` to auto-populate Supabase credentials. You must:

1. Deploy with Blueprint (will fail initially - that's OK!)
2. Immediately add DATABASE_URL and other variables
3. Save changes (triggers rebuild)
4. Build succeeds! ✅

**This is the ONLY way to deploy with external database (Supabase).**

---

**Ready? Commit, push, deploy Blueprint, add variables, and you're done!** 🎉
