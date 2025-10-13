# 🎉 Database Connection Working - Missing Tables Fix

## Current Status

✅ **Database connection is working!**
✅ **Port 6543 is correct**
✅ **Password authentication successful**
❌ **Database tables don't exist yet**

## Error

```
psycopg2.errors.UndefinedTable: relation "django_session" does not exist
```

This means Django tables haven't been created in your Supabase PostgreSQL database yet.

## 🔧 Quick Fix: Run Migrations on Render

### Option 1: Use Render Shell (Fastest - 2 minutes)

1. **Go to Render Dashboard**
   - Visit: https://dashboard.render.com
   - Select your `homework-scraper-backend` service

2. **Open Shell**
   - Click the **"Shell"** tab (or button)
   - Wait for shell to connect

3. **Run Migration Commands**
   ```bash
   cd /opt/render/project/src/backend
   python manage.py migrate
   ```

4. **Create Superuser (Optional)**
   ```bash
   python manage.py createsuperuser
   ```

5. **Test Your App**
   - Visit https://nd.dovydas.space
   - CORS and 500 errors should be gone! 🎉

### Option 2: Trigger Manual Redeploy

1. **Go to Render Dashboard** → Your backend service
2. Click **"Manual Deploy"** → **"Deploy latest commit"**
3. The `build.sh` script should run migrations automatically
4. Check deployment logs for: `✓ Database migrations completed successfully`

### Option 3: Add Migration as Separate Command (If Option 1 & 2 Fail)

If migrations keep failing during build, you can run them as a one-time job:

1. **In Render Dashboard**
   - Go to your service → **Settings**
   - Scroll to **"Deploy Hook"**

2. **Create a Migration Job** (Advanced)
   - Or use the Shell option above

## ✅ Expected Result

After running migrations successfully:

### In Render Logs:
```
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  Applying admin.0001_initial... OK
  Applying sessions.0001_initial... OK
  Applying authentication.0001_initial... OK
  ...
✓ Database migrations completed successfully
```

### In Your Browser:
```
✅ No CORS errors
✅ No 500 errors
✅ /api/auth/user returns proper response
✅ Login works
✅ Settings page loads
```

## 🔍 Verify Tables Were Created

After running migrations, you can verify in Supabase:

1. **Go to Supabase Dashboard**
2. Click **"Table Editor"**
3. You should see Django tables:
   - `auth_user`
   - `django_session`
   - `authentication_googleoauth`
   - `authentication_schoolcredentials`
   - `scraper_homework`
   - And many more...

## 📋 Common Issues

### Issue 1: Permission Denied
**Error:** `permission denied for schema public`

**Fix:** Grant permissions in Supabase:
```sql
-- Run in Supabase SQL Editor
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON ALL TABLES IN SCHEMA public TO postgres;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO postgres;
```

### Issue 2: Migrations Fail During Build
**Error:** Migrations timeout or fail

**Fix:** Use the Shell method (Option 1) to run migrations manually after deployment.

### Issue 3: "No migrations to apply"
**Symptom:** Migration command says nothing to apply but tables still don't exist

**Fix:** Check if you're connected to the right database:
```bash
python manage.py dbshell
# Should connect to Supabase PostgreSQL
# Type \dt to list tables
# Type \q to quit
```

## 🚀 After Fix - What's Next?

Once migrations are complete and tables exist:

1. **Test Full Flow:**
   - Visit https://nd.dovydas.space
   - Click "Login with Google"
   - Complete OAuth flow
   - Navigate to Settings
   - Add school credentials
   - Test scraping

2. **Monitor Logs:**
   - Check Render logs for any errors
   - All API calls should return 200 OK

3. **Verify Session Management:**
   - Browser cookies should be set
   - Session persists across page refreshes
   - Logout works properly

## 💡 Why Did This Happen?

The `build.sh` script includes migration commands, but they might have failed silently during the first deployment because:

1. **Database wasn't ready** when migrations ran
2. **Migrations timed out** during build
3. **Build script continued** even after migration failure (intentional for resilience)

The fix is simple: manually run migrations once using the Shell.

## 📝 Prevention for Future

To ensure migrations always run, you can:

1. **Check build logs** after every deployment
2. **Run migrations manually** after major schema changes
3. **Use Render's pre-deploy command** (if available in your plan)

---

**Time to Fix:** 2 minutes (using Shell)

**Result:** Everything will work - CORS fixed, database connected, tables created! 🎉
