# 🔐 Database Password Authentication Failed

## Current Status

✅ **GOOD NEWS:** You're now using port 6543 (Session Pooler) - Connection is working!

❌ **NEW ISSUE:** Password authentication is failing

```
psycopg2.OperationalError: connection to server at "aws-1-eu-north-1.pooler.supabase.com" 
(51.21.18.29), port 6543 failed: FATAL: password authentication failed for user "postgres"
```

## Root Cause

Your `DATABASE_URL` on Render contains an **incorrect or outdated password** for your Supabase database.

## 🔧 IMMEDIATE FIX (3 minutes)

### Step 1: Get the Correct Password from Supabase

1. **Go to Supabase Dashboard**
   - Visit: https://supabase.com/dashboard
   - Select your project

2. **Get Database Password**
   - Go to: **Settings** → **Database**
   - Scroll to **Connection string** section
   - Click on **Session mode** dropdown
   - **Click the eye icon** to reveal the full connection string with the password
   - Copy the entire connection string

   It should look like:
   ```
   postgresql://postgres.abcdefghijk:[YOUR-PASSWORD]@aws-0-eu-north-1.pooler.supabase.com:6543/postgres
   ```

### Step 2: Update DATABASE_URL on Render

1. **Go to Render Dashboard**
   - Visit: https://dashboard.render.com
   - Select your backend service

2. **Update Environment Variable**
   - Click **"Environment"** tab
   - Find `DATABASE_URL`
   - Click **"Edit"**
   - **Paste the complete connection string** from Supabase (including the password)
   - Click **"Save Changes"**
   - Service will automatically redeploy (2-3 minutes)

### Step 3: Verify the Fix

After redeployment:

1. **Check Render Logs** for:
   ```
   ✓ Connecting to Supabase: aws-0-eu-north-1.pooler.supabase.com:6543
   ✓ Using port 6543 (Session pooler - recommended for Django)
   ```

2. **Should NOT see:**
   ```
   ❌ password authentication failed
   ```

3. **Test your app:**
   - Visit https://nd.dovydas.space
   - Try logging in
   - API calls should now work!

## 🔍 Common Password Issues

### Issue 1: Wrong Password
**Cause:** Password in DATABASE_URL doesn't match Supabase
**Solution:** Copy the connection string directly from Supabase Dashboard

### Issue 2: Special Characters Not Encoded
**Cause:** Password contains special characters like `@`, `#`, `!`, etc.
**Solution:** Supabase provides the connection string with the password already URL-encoded. Use it as-is.

Example:
```bash
# If your password is: p@ss!word#123
# Supabase gives you: postgresql://postgres.xxx:p%40ss%21word%23123@...
# Use the encoded version from Supabase
```

### Issue 3: Placeholder Password
**Cause:** You manually edited the connection string
**Solution:** Always copy the complete string from Supabase Dashboard

### Issue 4: Password Changed
**Cause:** You reset your Supabase database password
**Solution:** Update DATABASE_URL with the new connection string

## 📋 Pre-Flight Checklist

- [ ] Supabase project is active (not paused)
- [ ] You have access to Supabase Dashboard
- [ ] You have access to Render Dashboard
- [ ] Connection string copied from Supabase (not manually typed)

## 🎯 Expected Result

Once fixed, your Render logs should show:

```
✓ Connecting to Supabase: aws-0-eu-north-1.pooler.supabase.com:6543
✓ Using port 6543 (Session pooler - recommended for Django)
[timestamp] "GET /api/auth/user HTTP/1.1" 200 [bytes]
[timestamp] "GET /api/auth/google/login HTTP/1.1" 200 [bytes]
```

And browser console should show:
```
✅ No CORS errors
✅ No 500 errors
✅ Successful API responses
```

## 🆘 If Password is Definitely Correct

If you're 100% sure the password is correct but still getting authentication errors:

### Option A: Reset Database Password

1. **In Supabase Dashboard:**
   - Settings → Database
   - Click **"Reset database password"**
   - Copy the new password
   - Get the new connection string

2. **Update on Render:**
   - Update DATABASE_URL with the new connection string
   - Save and redeploy

### Option B: Check Connection String Format

Make sure your DATABASE_URL looks like this:
```
postgresql://postgres.[PROJECT-REF]:[PASSWORD]@aws-0-eu-north-1.pooler.supabase.com:6543/postgres
```

**Common mistakes:**
- Missing `postgres.` prefix before project ref
- Wrong region (should match your project)
- Port 5432 instead of 6543
- `postgres://` instead of `postgresql://`

### Option C: Test Connection String Locally

Before updating Render, test the connection string:

```python
# Test in Python locally
import psycopg2

conn_string = "your-connection-string-here"
try:
    conn = psycopg2.connect(conn_string)
    print("✅ Connection successful!")
    conn.close()
except Exception as e:
    print(f"❌ Connection failed: {e}")
```

## 📚 Understanding the Error

```
FATAL: password authentication failed for user "postgres"
```

This PostgreSQL error means:
- ✅ Network connection is working
- ✅ Port 6543 is correct
- ✅ Host is reachable
- ❌ Username/password combination is wrong

The "user" is `postgres.[your-project-ref]` and it's embedded in the connection string.

## 🔐 Security Note

**Never commit DATABASE_URL to git!**

- Store it only in Render Environment Variables
- The password is sensitive
- Supabase can rotate passwords if compromised

---

## Summary

**What happened:**
1. ✅ Fixed port from 5432 → 6543 
2. ✅ Connection now reaches Supabase
3. ❌ Password authentication is failing

**What to do:**
1. Get complete connection string from Supabase Dashboard
2. Update DATABASE_URL on Render
3. Wait for redeploy
4. Test your app

**Time to fix:** 3 minutes

---

**Once this is fixed, both CORS and database errors will be resolved! 🎉**
