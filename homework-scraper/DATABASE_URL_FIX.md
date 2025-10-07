# DATABASE_URL Error Fix

## The Problem

You're seeing this error:
```
ValueError: Port could not be cast to integer value as 'port'
```

This means your `DATABASE_URL` environment variable is malformed. It likely looks like:
```
postgresql://user:password@host:port/database
```

Where `port` is literally the text "port" instead of a number like `5432`.

---

## The Solution

### Option 1: Use Render Blueprint (RECOMMENDED)

If you deployed using `render.yaml`, the DATABASE_URL should be automatically set. Check:

1. Go to Render Dashboard
2. Click on your web service
3. Go to "Environment" tab
4. Look for `DATABASE_URL`
5. It should say: `${postgres.database_url}` or show a full connection string

**If it's missing or wrong:**
- Delete the current deployment
- Re-deploy using Blueprint
- Make sure `render.yaml` is in your repository root

### Option 2: Link Database Service Manually

1. **Create PostgreSQL Database** (if not already created):
   - Dashboard → New → PostgreSQL
   - Name: `homework-scraper-db`
   - Database: `homework_scraper`
   - User: `homework_scraper`
   - Click "Create Database"
   - Wait for provisioning (~2 minutes)

2. **Link Database to Web Service**:
   - Go to your web service settings
   - Scroll to "Environment Variables"
   - Click "Add Environment Variable"
   - Key: `DATABASE_URL`
   - Value: Click "Add from Service" or "Add from Database"
   - Select your PostgreSQL service
   - Select `Internal Database URL` or `External Database URL`
   - Click "Add"

3. **Verify**:
   - The DATABASE_URL should now show as: `${postgres.database_url}`
   - This tells Render to use the internal reference
   - Save and redeploy

### Option 3: Manual URL Entry (NOT RECOMMENDED)

If you must enter manually, get the FULL connection string:

1. Go to your PostgreSQL service
2. Copy the "Internal Database URL" 
3. It should look like:
   ```
   postgresql://homework_scraper:aBc123...@dpg-xxx-a.oregon-postgres.render.com:5432/homework_scraper
   ```
4. Paste this EXACT string into DATABASE_URL

**Critical**: The port MUST be a number (usually `5432`), not the text "port"

---

## Verification

After fixing, your build should succeed at this step:
```bash
Collecting static files...
X static files copied to '/opt/render/project/src/staticfiles'
Running migrations...
Operations to perform:
  Apply all migrations...
```

---

## Using render.yaml (Best Practice)

Your `render.yaml` should have:

```yaml
databases:
  - name: postgres
    databaseName: homework_scraper
    user: homework_scraper
    plan: free

services:
  - type: web
    name: homework-scraper-backend
    env: python
    buildCommand: "chmod +x build.sh && ./build.sh"
    startCommand: "gunicorn homework_scraper.wsgi:application --bind 0.0.0.0:$PORT"
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: postgres
          property: connectionString
      - key: DJANGO_SETTINGS_MODULE
        value: homework_scraper.settings_production
```

The key part:
```yaml
- key: DATABASE_URL
  fromDatabase:
    name: postgres
    property: connectionString
```

This automatically links the database!

---

## Still Having Issues?

### Check Environment Variables:
```bash
# In Render shell (Services → Shell):
echo $DATABASE_URL
```

Should output something like:
```
postgresql://user:random_password@dpg-xxx.oregon-postgres.render.com:5432/database
```

### Check render.yaml syntax:
- Make sure indentation is correct (use spaces, not tabs)
- Verify database name matches in both places
- Check that `property: connectionString` is specified

### Last Resort - SQLite for Testing:
If you just want to test deployment without PostgreSQL:

Edit `settings_production.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

**WARNING**: SQLite is NOT suitable for production with Celery!

---

## Summary

✅ **DO**: Use Render Blueprint with render.yaml
✅ **DO**: Link database service through Render UI
✅ **DO**: Use `${postgres.database_url}` syntax

❌ **DON'T**: Manually type database URLs
❌ **DON'T**: Leave literal "port" in DATABASE_URL
❌ **DON'T**: Use SQLite in production
