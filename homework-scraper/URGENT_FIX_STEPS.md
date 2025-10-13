# 🚨 URGENT: Fix CORS and Database Connection

## Root Cause Analysis

Your application has **TWO critical issues** that are interconnected:

### Issue 1: Database Connection Failure (Primary Issue)
```
psycopg2.OperationalError: connection to server at "aws-1-eu-north-1.pooler.supabase.com" 
(51.21.18.29), port 5432 failed: Connection refused
```

**Cause:** You're using port 5432 (direct connection) which is being refused by Supabase.

### Issue 2: CORS Error (Secondary - caused by Issue 1)
```
Access to fetch at 'https://api.dovydas.space/api/auth/user' from origin 'https://nd.dovydas.space' 
has been blocked by CORS policy: No 'Access-Control-Allow-Origin' header is present
```

**Cause:** The database connection fails BEFORE Django can process the request and add CORS headers. Django returns a 500 error without CORS headers, causing the browser to block the response.

## 🔧 IMMEDIATE FIX (5 minutes)

### Step 1: Update DATABASE_URL on Render

1. **Go to Supabase Dashboard**
   - URL: https://supabase.com/dashboard/project/[your-project-id]/settings/database
   - Navigate to: **Settings** → **Database**
   - Scroll to **Connection string** section

2. **Get Session Pooler Connection String**
   - Click on **"Session mode"** dropdown
   - Copy the connection string
   - Should look like: `postgresql://postgres.xxx:password@aws-0-eu-north-1.pooler.supabase.com:6543/postgres`
   - **IMPORTANT: Port must be 6543, NOT 5432**

3. **Update Render Environment Variable**
   - Go to: https://dashboard.render.com
   - Select your backend service
   - Click **"Environment"** tab
   - Find `DATABASE_URL`
   - Click **"Edit"**
   - Paste the new connection string (with port 6543)
   - Click **"Save Changes"**
   - **Service will auto-redeploy** (takes 2-3 minutes)

### Step 2: Verify the Fix

After redeployment completes:

1. **Check Render Logs**
   ```
   Look for: ✓ Using port 6543 (Session pooler - recommended for Django)
   ```

2. **Test Your Application**
   - Visit: https://nd.dovydas.space
   - Try logging in
   - Check browser console - CORS errors should be gone
   - API calls should work

## 📋 Pre-Flight Checklist

Before making the change, verify you have:

- [ ] Supabase project is NOT paused (free tier auto-pauses)
- [ ] Correct Supabase password
- [ ] Access to Render dashboard
- [ ] Session mode connection string (port 6543)

## 🎯 Expected Results After Fix

### ✅ What should work:
- Database connections stable
- CORS errors resolved
- User authentication working
- Settings page loads credentials
- API calls succeed

### 📊 Render Logs Should Show:
```
✓ Connecting to Supabase: aws-0-eu-north-1.pooler.supabase.com:6543
✓ Using port 6543 (Session pooler - recommended for Django)
[timestamp] "GET /api/auth/user HTTP/1.1" 200 [bytes]
```

### 🌐 Browser Console Should Show:
```
✅ No CORS errors
✅ Successful API responses
✅ Session cookies set properly
```

## 🔍 Troubleshooting

### If still getting "Connection refused":

1. **Check Supabase is Active**
   - Free tier projects pause after 1 week of inactivity
   - Go to Supabase Dashboard and wake it up

2. **Verify Connection String Format**
   ```bash
   # ✅ CORRECT
   postgresql://postgres.xxx:password@aws-0-eu-north-1.pooler.supabase.com:6543/postgres
   
   # ❌ WRONG (port 5432)
   postgresql://postgres.xxx:password@aws-0-eu-north-1.pooler.supabase.com:5432/postgres
   ```

3. **Check Password Encoding**
   - If password has special characters, they must be URL-encoded
   - Example: `p@ss` becomes `p%40ss`

### If CORS errors persist after database fix:

1. **Clear Browser Cache**
   - Hard refresh: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)
   - Or use incognito/private mode

2. **Verify Frontend URL**
   - Make sure you're accessing `https://nd.dovydas.space` (not `http://`)
   - SSL must be enabled for SameSite=None cookies

3. **Check Environment Variables on Render**
   ```bash
   CORS_ALLOWED_ORIGINS=https://nd.dovydas.space,https://api.dovydas.space
   FRONTEND_URL=https://nd.dovydas.space
   ```

## 📚 Why Port 6543 Instead of 5432?

| Feature | Port 5432 (Direct) | Port 6543 (Session Pooler) |
|---------|-------------------|---------------------------|
| Connection Limit | ⚠️ 20-50 connections | ✅ Unlimited (pooled) |
| Django Compatibility | ❌ May fail under load | ✅ Recommended |
| Connection Stability | ❌ Refused when full | ✅ Always available |
| Use Case | Admin, Migrations | **Production Web Apps** |

**For Django web applications, ALWAYS use port 6543 with Session mode.**

## 🆘 Still Need Help?

### Check These Files Were Updated:
- [x] `backend/homework_scraper/settings_production.py` - CORS settings updated
- [x] `CORS_AND_DATABASE_FIX.md` - Detailed guide created

### Review the Changes:
```bash
git status
git diff backend/homework_scraper/settings_production.py
```

### View Render Logs:
```bash
# On Render Dashboard → Your Service → Logs
# Look for database connection messages and error tracebacks
```

## 🎬 Next Steps After Fix

Once everything is working:

1. **Test All Features**
   - Login/Logout
   - Credential storage
   - Scraping
   - Settings page

2. **Monitor Performance**
   - Check Render logs for any new errors
   - Watch Supabase dashboard for connection stats

3. **Document Any Issues**
   - Note down any remaining problems
   - Check browser console for warnings

---

**Estimated Time to Fix: 5 minutes**

**Priority: CRITICAL** 🔴

The fix is simple: Update DATABASE_URL to use port 6543. This will resolve both the database connection AND CORS issues simultaneously.
