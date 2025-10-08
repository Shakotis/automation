# 🔥 QUICK FIX: Render Database Connection Error

## The Problem
```
psycopg2.OperationalError: connection to server at "13.60.102.132", port 5432 failed: Connection refused
```

## The Solution (2 minutes)

### Step 1: Get the Correct Connection String

1. Go to your [Supabase Dashboard](https://supabase.com/dashboard)
2. Open your project: `kcixuytszyzgvcybxyym`
3. Click **Settings** → **Database** (left sidebar)
4. Scroll to **Connection string** section
5. Click **Session pooler** tab (NOT Transaction pooler)
6. Copy the connection string that looks like:
   ```
   postgresql://postgres.kcixuytszyzgvcybxyym:[YOUR-PASSWORD]@aws-0-eu-north-1.pooler.supabase.com:6543/postgres
   ```
   **Notice the port is 6543, NOT 5432** ✅

### Step 2: Update Render Environment Variable

1. Go to your [Render Dashboard](https://dashboard.render.com)
2. Click on your `homework-scraper-backend` service
3. Click **Environment** in the left sidebar
4. Find the `DATABASE_URL` variable (or add it if missing)
5. Replace the value with the Session pooler connection string from Step 1
6. **Make sure it uses port 6543**
7. Click **Save Changes**

### Step 3: Wait for Redeploy

Render will automatically redeploy your service. Wait for it to complete.

In the logs, you should see:
```
✓ Connecting to Supabase: aws-0-eu-north-1.pooler.supabase.com:6543
✓ Using port 6543 (Session pooler - recommended for Django)
Running database migrations...
Operations to perform:
  Apply all migrations...
✓ Deployment successful
```

## What Changed?

- **Old**: Port 5432 (Transaction pooler) - ❌ Connection refused
- **New**: Port 6543 (Session pooler) - ✅ Works with Django

## Why This Works

Supabase uses pgBouncer for connection pooling:
- **Port 5432** = Transaction mode (doesn't work well with Django)
- **Port 6543** = Session mode (recommended for Django ORM)

## Still Having Issues?

Check the detailed guide: [docs/SUPABASE_CONNECTION_FIX.md](docs/SUPABASE_CONNECTION_FIX.md)

## Files Updated

1. ✅ `backend/homework_scraper/settings_production.py` - Better connection handling
2. ✅ `render.yaml` - Updated documentation
3. ✅ `docs/SUPABASE_CONNECTION_FIX.md` - Detailed troubleshooting guide

---

**TL;DR**: Change DATABASE_URL port from **5432** to **6543** in Render environment variables.
