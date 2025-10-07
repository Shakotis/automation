# Quick Fix: DATABASE_URL Port Error

## The Error You're Seeing
```
ValueError: Port could not be cast to integer value as 'port'
```

## What It Means
Your web service is trying to build **before** the database is ready. The `DATABASE_URL` has placeholder text instead of real credentials.

---

## ⏱️ Quick Fix (2 Steps)

### Step 1: Check Database Status
Go to Render Dashboard → Find `homework-scraper-db`

- **Status: "Provisioning"** → ⏳ **Wait 5 more minutes**
- **Status: "Available"** → ✅ **Go to Step 2**

### Step 2: Redeploy Web Service
Go to `homework-scraper-backend` service

- Click **"Manual Deploy"** → **"Deploy latest commit"**
- Or wait for automatic retry (happens within 10 minutes)

---

## ✅ Expected Result

**Build logs should show:**
```bash
Collecting static files...
127 static files copied...
Running migrations...
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
✓ Build complete!
```

**Test URL:**
`https://your-backend.onrender.com/api/health`

Should return:
```json
{"status": "ok"}
```

---

## 🔥 If Still Failing After 15 Minutes

### Option A: Manual Database Link

1. Go to web service → **Environment** tab
2. Find `DATABASE_URL` variable
3. Click edit → **"Add from Database"**
4. Select `homework-scraper-db`
5. Choose **"Internal Database URL"**
6. Click **"Save Changes"** (auto-redeploys)

### Option B: Start Fresh

1. **Delete** web service ONLY (keep database!)
2. Wait 2 minutes
3. **Redeploy** using Blueprint
4. This time database is already ready

---

## 📱 Need More Help?

See detailed guides:
- `DATABASE_PLACEHOLDER_FIX.md` - Complete troubleshooting
- `DATABASE_URL_ERROR_FIXED.md` - What we've fixed
- `CUSTOM_DOMAIN_SETUP.md` - Domain configuration

---

**Key Point**: First deployment failure is NORMAL with Render Blueprint. Just wait and retry! 🚀
