# Using Supabase Database with Render

## 🎯 Overview

Instead of using Render's PostgreSQL service, you can use **Supabase** as your database. This gives you:
- ✅ Free tier with 500MB database
- ✅ Built-in auth (if needed)
- ✅ Real-time subscriptions
- ✅ Auto-generated REST API
- ✅ No provisioning delays

---

## 📝 What I Need from Your Supabase Project

To configure the database connection, I need these details from your Supabase project:

### 1. Database Connection String

**Where to find it:**
1. Go to https://supabase.com/dashboard
2. Select your project: `kcixuytszyzgvcybxyym`
3. Click "Project Settings" (gear icon)
4. Go to "Database" section
5. Look for **"Connection string"** → **"URI"**

**It should look like:**
```
postgresql://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres
```

Or the **direct connection** (not pooled):
```
postgresql://postgres:[password]@db.[project-ref].supabase.co:5432/postgres
```

### 2. Supabase URL (Already have: `https://kcixuytszyzgvcybxyym.supabase.co`)

### 3. Supabase Anon Key

**Where to find it:**
1. Same "Project Settings" page
2. Go to "API" section
3. Look for **"Project API keys"** → **"anon" "public"**

**It should look like:**
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtjaXh1...
```

### 4. Supabase Service Role Key (Optional, for admin operations)

**Where to find it:**
1. Same "API" section
2. Look for **"service_role" "secret"**

⚠️ **Keep this secret!** It bypasses all security rules.

---

## 🔧 Configuration Steps

### Step 1: Update render.yaml

Remove or comment out the PostgreSQL database service:

```yaml
# Render Blueprint Configuration

# Comment out or remove this section:
# databases:
#   - name: homework-scraper-db
#     databaseName: homework_scraper
#     user: homework_user
#     plan: free

services:
  - type: web
    name: homework-scraper-backend
    # ... rest of config ...
    
    envVars:
      # Replace DATABASE_URL reference
      - key: DATABASE_URL
        value: [YOUR_SUPABASE_CONNECTION_STRING]  # Add manually in Render dashboard
      
      # Add Supabase credentials
      - key: SUPABASE_URL
        value: https://kcixuytszyzgvcybxyym.supabase.co
      
      - key: SUPABASE_KEY
        value: [YOUR_SUPABASE_ANON_KEY]  # Add in Render dashboard
      
      - key: SUPABASE_SERVICE_KEY
        sync: false  # Set manually in Render dashboard
      
      # ... rest of your envVars ...
```

### Step 2: Set Environment Variables in Render

1. **Go to Render Dashboard**
2. **Open your web service**: `homework-scraper-backend`
3. **Go to "Environment" tab**
4. **Add these variables:**

```bash
# Database Connection
DATABASE_URL=postgresql://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres

# Supabase API
SUPABASE_URL=https://kcixuytszyzgvcybxyym.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Django Settings (already set)
SECRET_KEY=[auto-generated]
DEBUG=False
ALLOWED_HOSTS=.onrender.com,api.dovydas.space
DJANGO_SETTINGS_MODULE=homework_scraper.settings_production

# CORS (already set)
CORS_ALLOWED_ORIGINS=https://nd.dovydas.space,http://localhost:3000
CSRF_TRUSTED_ORIGINS=https://nd.dovydas.space,https://api.dovydas.space

# Redis (if using)
REDIS_URL=[from Redis service]
CELERY_BROKER_URL=[from Redis service]
```

4. **Click "Save Changes"** (triggers redeploy)

### Step 3: Update settings_production.py (Already Done ✅)

The file now correctly reads from `DATABASE_URL` environment variable.

### Step 4: Run Migrations

After successful deployment, run migrations to create tables in Supabase:

**Option A: Using Render Shell**
1. Go to Render Dashboard → Your service
2. Click "Shell" tab
3. Run:
   ```bash
   python manage.py migrate
   ```

**Option B: Automatic during build**
Already configured in `build.sh` - migrations run automatically!

---

## 🔐 Connection String Format

### Pooled Connection (Recommended for Production)
```
postgresql://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres
```

**Use this for:**
- High-traffic apps
- Serverless functions
- Multiple workers

**Port:** `6543` (pooler)

### Direct Connection (Simpler)
```
postgresql://postgres:[password]@db.[project-ref].supabase.co:5432/postgres
```

**Use this for:**
- Development
- Simple deployments
- Lower traffic

**Port:** `5432` (standard PostgreSQL)

---

## 🧪 Testing Connection Locally

Test the connection string before deploying:

```powershell
# Set environment variable temporarily
$env:DATABASE_URL = "postgresql://postgres.[project-ref]:[password]@..."

# Test connection
cd backend
python manage.py check --database default

# If successful, try migrations
python manage.py migrate

# Run development server
python manage.py runserver
```

---

## ✅ Advantages of Supabase vs Render PostgreSQL

| Feature | Supabase | Render PostgreSQL |
|---------|----------|-------------------|
| **Provisioning Time** | Instant | 2-5 minutes |
| **Free Tier** | 500MB, unlimited duration | 90 days, then expires |
| **Connection Pooling** | Built-in (PgBouncer) | Not included |
| **Backups** | Automatic daily | Manual setup needed |
| **Dashboard** | Full SQL editor, table view | Basic management |
| **Extensions** | Many pre-installed | Limited |
| **Real-time** | Built-in subscriptions | Not available |

---

## 📊 Supabase Project Configuration

### Enable Extensions (if needed)

In Supabase Dashboard → SQL Editor, run:

```sql
-- UUID support (likely already enabled)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Full-text search
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- PostGIS (if using geo features)
-- CREATE EXTENSION IF NOT EXISTS "postgis";
```

### Check Connection Limits

Free tier limits:
- **Direct connections**: 60
- **Pooled connections**: 200

If you hit limits, use the pooled connection string.

---

## 🚀 Deployment Checklist with Supabase

### Before Deploying:
- [ ] Get Supabase connection string (pooled or direct)
- [ ] Get Supabase anon key
- [ ] Get Supabase service role key (optional)
- [ ] Test connection locally
- [ ] Update render.yaml (remove PostgreSQL service)

### In Render Dashboard:
- [ ] Set `DATABASE_URL` environment variable
- [ ] Set `SUPABASE_URL` environment variable
- [ ] Set `SUPABASE_KEY` environment variable
- [ ] Set `SUPABASE_SERVICE_KEY` (if needed)
- [ ] Click "Save Changes" to trigger redeploy

### After Deployment:
- [ ] Check build logs for successful migration
- [ ] Test health endpoint: `/api/health`
- [ ] Verify database tables created in Supabase dashboard
- [ ] Test API endpoints
- [ ] Check Supabase dashboard for data

---

## 🐛 Troubleshooting

### Error: "could not connect to server"
**Cause**: Wrong connection string or firewall

**Solution**:
1. Check connection string is correct
2. Ensure no extra spaces or quotes
3. Try direct connection instead of pooled
4. Check Supabase project is active (not paused)

### Error: "password authentication failed"
**Cause**: Wrong password in connection string

**Solution**:
1. Reset database password in Supabase dashboard
2. Settings → Database → Reset database password
3. Update `DATABASE_URL` in Render
4. Redeploy

### Error: "SSL connection required"
**Cause**: Supabase requires SSL by default

**Solution**:
Add `?sslmode=require` to connection string:
```
postgresql://postgres:[password]@db.[project-ref].supabase.co:5432/postgres?sslmode=require
```

### Migrations Not Running
**Cause**: Build script failing before migrations

**Solution**:
1. Check build logs in Render
2. Verify `DATABASE_URL` is set
3. Try running migrations manually in Shell
4. Check Supabase database is accessible

---

## 📝 Example: Complete DATABASE_URL

Replace placeholders with your actual values:

```bash
# Pooled (recommended)
DATABASE_URL=postgresql://postgres.kcixuytszyzgvcybxyym:[YOUR_PASSWORD]@aws-0-us-east-1.pooler.supabase.com:6543/postgres

# Or Direct
DATABASE_URL=postgresql://postgres:[YOUR_PASSWORD]@db.kcixuytszyzgvcybxyym.supabase.co:5432/postgres
```

**Where to find password:**
- Go to Supabase Dashboard
- Settings → Database
- "Connection string" section
- Look for `[YOUR-PASSWORD]` placeholder
- Click "Reset database password" if you don't know it

---

## 🎯 What to Send Me

To complete the configuration, please provide:

1. **Database Connection String** (mask the password if sharing publicly):
   ```
   postgresql://postgres.kcixuytszyzgvcybxyym:***@aws-0-us-east-1.pooler.supabase.com:6543/postgres
   ```

2. **Supabase Anon Key** (first 20 chars):
   ```
   eyJhbGciOiJIUzI1NiIsInR...
   ```

3. **Connection Type**: Pooled or Direct?

4. **Any custom extensions or settings** you've configured in Supabase?

I'll help you update the configuration files accordingly! 🚀

---

## Alternative: Keep Render PostgreSQL

If you prefer to use Render's PostgreSQL instead:

1. **Wait for database provisioning** (2-5 min)
2. **Don't modify render.yaml** (keep database section)
3. **Let Render auto-link** the database
4. **Redeploy** once database is "Available"

The choice is yours - Supabase is faster to set up and has better free tier, but Render PostgreSQL keeps everything in one place!
