# IPv6 Network Unreachable Fix 🔧

## Problem

Build failed with error:
```
django.db.utils.OperationalError: connection to server at "db.kcixuytszyzgvcybxyym.supabase.co" 
(2a05:d016:571:a427:517f:cd9a:93de:641a), port 5432 failed: Network is unreachable
```

**Root Cause:** Render's build environment tries to connect using IPv6 (`2a05:...`), but IPv6 is not available on Render.

## Solution Options

### ✅ Option 1: Use Supabase Pooler (RECOMMENDED)

**Why?** The pooler connection is designed for serverless/platform environments and uses IPv4.

**Change in Render Dashboard:**
```bash
# OLD (Direct connection - uses IPv6):
DATABASE_URL=postgresql://postgres:3BH6CyUl5OpWDqtD@db.kcixuytszyzgvcybxyym.supabase.co:5432/postgres

# NEW (Pooler connection - uses IPv4):
DATABASE_URL=postgresql://postgres.kcixuytszyzgvcybxyym:3BH6CyUl5OpWDqtD@aws-0-eu-central-1.pooler.supabase.com:6543/postgres
```

**⚠️ Note the differences:**
1. Different hostname: `aws-0-eu-central-1.pooler.supabase.com` (not `db.kcix...supabase.co`)
2. Different port: `6543` (not `5432`)
3. Different username format: `postgres.kcixuytszyzgvcybxyym` (includes project ref)
4. Different password: `3BH6CyUl5OpWDqtD` (transaction pooler password)

**Steps:**
1. Go to Supabase Dashboard → Project Settings → Database
2. Copy the "Connection pooling" → "Connection string" (mode: Transaction)
3. Replace `[YOUR-PASSWORD]` with your actual password: `3BH6CyUl5OpWDqtD`
4. Update `DATABASE_URL` in Render dashboard
5. Trigger redeploy

### ✅ Option 2: Force IPv4 Resolution (CODE FIX - ALREADY APPLIED)

I've updated `settings_production.py` to automatically resolve the hostname to IPv4:

```python
# Extract hostname and resolve to IPv4 only
ipv4_addresses = [
    addr[4][0] for addr in socket.getaddrinfo(
        db_host, None, socket.AF_INET, socket.SOCK_STREAM
    )
]
# Use hostaddr parameter to force IPv4
db_config['OPTIONS'] = {
    'sslmode': 'require',
    'hostaddr': ipv4_addresses[0],
}
```

**This should work with your current connection string!**

### Option 3: Use IPv4 Address Directly

Get the IPv4 address of your Supabase server and use it in DATABASE_URL:

```bash
# Find IPv4 address:
nslookup -type=A db.kcixuytszyzgvcybxyym.supabase.co

# Then use it in DATABASE_URL (example):
DATABASE_URL=postgresql://postgres:3BH6CyUl5OpWDqtD@52.18.123.45:5432/postgres
```

**⚠️ Warning:** IP addresses can change, making this less reliable.

## Recommended Action

### Try This First (Code Fix Already Applied) ✅

The code fix in Option 2 is already applied. Just commit and redeploy:

```powershell
cd W:\automation\homework-scraper
git add .
git commit -m "Fix IPv6 connection issue with IPv4 resolution"
git push origin main
```

Then watch the Render build logs. You should see:
```
✓ Resolved db.kcixuytszyzgvcybxyym.supabase.co to IPv4: x.x.x.x
```

### If That Doesn't Work (Use Pooler)

Update DATABASE_URL in Render Dashboard to use the pooler connection:

1. **Get the correct pooler URL from Supabase:**
   - Go to https://supabase.com/dashboard
   - Select your project
   - Settings → Database
   - Connection pooling → Connection string
   - Mode: Transaction
   - Copy the string

2. **Format should be:**
   ```
   postgresql://postgres.kcixuytszyzgvcybxyym:3BH6CyUl5OpWDqtD@aws-0-eu-central-1.pooler.supabase.com:6543/postgres
   ```

3. **Update in Render:**
   - Dashboard → Your service → Environment
   - Edit DATABASE_URL
   - Paste the new value
   - Save (this triggers redeploy)

## Why This Happens

1. **Supabase DNS** returns both IPv4 and IPv6 addresses
2. **psycopg2** (PostgreSQL driver) prefers IPv6 when available
3. **Render build environment** doesn't have IPv6 connectivity
4. **Result:** Connection fails with "Network is unreachable"

## How the Fix Works

### Code Fix (Option 2 - Already Applied)
```python
# Force DNS resolution to IPv4 only using socket.AF_INET
ipv4_addresses = socket.getaddrinfo(host, None, socket.AF_INET, socket.SOCK_STREAM)

# Use hostaddr parameter to bypass DNS during connection
db_config['OPTIONS'] = {'hostaddr': ipv4_address}
```

This tells psycopg2: "Use this specific IPv4 address, don't do DNS lookup"

### Pooler Fix (Option 1 - Recommended if code fix doesn't work)
The pooler uses a different infrastructure that's optimized for IPv4 connections from serverless environments.

## Verification

After deploying, check build logs for:

**Success indicators:**
```
✓ Resolved db.kcixuytszyzgvcybxyym.supabase.co to IPv4: 52.18.123.45
Checking database connection...
Running database migrations...
Operations to perform:
  Apply all migrations...
✅ Migrations complete
```

**If still failing:**
```
⚠ DNS resolution failed for db.kcixuytszyzgvcybxyym.supabase.co
psycopg2.OperationalError: connection to server at ... (2a05:...) failed: Network is unreachable
```

→ Use the pooler connection string (Option 1)

## Testing Locally

To test the IPv4 resolution locally:

```powershell
cd W:\automation\homework-scraper\backend

# Windows (PowerShell)
$env:DATABASE_URL="postgresql://postgres:3BH6CyUl5OpWDqtD@db.kcixuytszyzgvcybxyym.supabase.co:5432/postgres"
$env:DJANGO_SETTINGS_MODULE="homework_scraper.settings_production"
python manage.py check --database default
```

You should see output showing IPv4 resolution.

## Additional Resources

- **Supabase Connection Pooling:** https://supabase.com/docs/guides/database/connecting-to-postgres#connection-pooler
- **Render IPv6 Support:** https://render.com/docs/ipv6 (currently limited)
- **psycopg2 Connection Parameters:** https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-PARAMKEYWORDS

---

**Status:** Code fix applied ✅  
**Next Step:** Commit and push, then monitor build logs  
**Fallback:** Use pooler connection string if code fix doesn't work
