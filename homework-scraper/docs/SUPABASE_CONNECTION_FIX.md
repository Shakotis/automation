# Supabase Connection Fix for Render Deployment

## Problem
Getting `Connection refused` error when trying to connect to Supabase from Render:
```
psycopg2.OperationalError: connection to server at "13.60.102.132", port 5432 failed: Connection refused
```

## Root Cause
Supabase offers two connection modes via pgBouncer:
- **Port 5432** - Transaction pooler (may be blocked or unstable)
- **Port 6543** - Session pooler (recommended for Django)

The connection on port 5432 is being refused, likely due to firewall rules or pooler configuration.

## Solution Options

### Option 1: Use Session Pooler (Port 6543) - RECOMMENDED ✅

This is the recommended approach for Django applications.

1. Go to your Supabase project dashboard
2. Navigate to **Settings** → **Database**
3. Find the **Connection string** section
4. Look for the **Session pooler** connection string (uses port 6543)
5. Copy the connection string and update your Render environment variable

**Example format:**
```
postgresql://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres
```

**In Render Dashboard:**
1. Go to your service → **Environment**
2. Find the `DATABASE_URL` variable
3. Update it to use port **6543** instead of 5432
4. Click **Save** to trigger a redeploy

### Option 2: Use Direct Connection (Port 5432)

If you want to use port 5432, you need to use the **direct connection** (not pooler):

1. In Supabase dashboard → **Settings** → **Database**
2. Find the **Direct connection** string (not pooler)
3. Use this format:
```
postgresql://postgres:[password]@db.[project-ref].supabase.co:5432/postgres
```

**Note:** Direct connections may be slower and less reliable than the pooler.

### Option 3: Use IPv6 Pooler (Port 5432) with Transaction Mode

If you must use port 5432:

1. Make sure your Render service supports IPv6
2. Use the Transaction pooler URL with port 5432
3. This may require additional Render configuration

## Implementation Steps

### Step 1: Get the Correct Connection String

Go to Supabase → Settings → Database and copy the **Session pooler** connection string.

It should look like:
```
postgresql://postgres.kcixuytszyzgvcybxyym:[YOUR-PASSWORD]@aws-0-eu-north-1.pooler.supabase.com:6543/postgres
```

### Step 2: Update Render Environment Variable

1. Go to Render Dashboard
2. Select your `homework-scraper-backend` service
3. Click **Environment** in the left sidebar
4. Find or add the `DATABASE_URL` variable
5. Paste the Session pooler connection string (port 6543)
6. Click **Save Changes**

### Step 3: Verify the Change

After deployment, check the logs for this message:
```
✓ Connecting to Supabase: aws-0-eu-north-1.pooler.supabase.com:6543
✓ Using port 6543 (Session pooler - recommended for Django)
```

## Why Port 6543 Works Better

- **Session Mode**: Maintains a persistent connection pool suitable for Django ORM
- **Better Compatibility**: Works with Django's connection pooling
- **More Stable**: Less likely to be blocked by firewalls
- **Recommended by Supabase**: Official recommendation for frameworks like Django

## Additional Troubleshooting

### If port 6543 also fails:

1. **Check Supabase Network Restrictions**:
   - Go to Supabase → Settings → Database
   - Check if there are IP restrictions
   - Make sure Render's IP ranges are allowed

2. **Verify SSL Settings**:
   - The updated code requires SSL (`sslmode=require`)
   - This is correct for Supabase

3. **Check Connection Limits**:
   - Free tier has connection limits
   - Session pooler helps manage this

4. **Review Supabase Logs**:
   - Check Supabase dashboard for connection attempt logs
   - Look for any blocked connections

## What Changed in the Code

Updated `settings_production.py`:
- Removed IPv4 resolution hack (not needed with correct port)
- Added better connection options (keepalives, increased timeout)
- Added helpful diagnostic messages
- Improved error messages to guide toward correct solution

## References

- [Supabase Database Connection Guide](https://supabase.com/docs/guides/database/connecting-to-postgres)
- [pgBouncer Connection Pooling](https://www.pgbouncer.org/)
- [Django Database Configuration](https://docs.djangoproject.com/en/stable/ref/settings/#databases)
