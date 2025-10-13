# Supabase Connection String Quick Reference

## For Render Deployment

### Option 1: Session Pooler (Port 6543) - Requires IPv4 Add-on ⭐

**Best for:** Django applications with long-running connections  
**Requires:** Supabase IPv4 Add-on enabled ($0.04/month)

```
postgresql://postgres.[PROJECT-REF]:[YOUR-PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres
```

**Example:**
```
postgresql://postgres.kcixuytszyzgvcybxyym:MySecurePassword123@aws-0-eu-north-1.pooler.supabase.com:6543/postgres
```

**How to get it:**
1. Supabase Dashboard → Settings → Database
2. Scroll to "Connection string"
3. Select **"Session mode"**
4. **Important:** Enable IPv4 Add-on first!

---

### Option 2: Direct Connection (Port 5432) - Works without IPv4 ✅

**Best for:** When IPv4 add-on is not available  
**Note:** Has connection limits (no pooling)

```
postgresql://postgres.[PROJECT-REF]:[YOUR-PASSWORD]@aws-0-[REGION].supabase.com:5432/postgres
```

**Example:**
```
postgresql://postgres.kcixuytszyzgvcybxyym:MySecurePassword123@aws-0-eu-north-1.supabase.com:5432/postgres
```

**How to get it:**
1. Supabase Dashboard → Settings → Database
2. Scroll to "Connection string"
3. Select **"Direct connection"** or **"URI"**
4. Port should be **5432**
5. Hostname should NOT include "pooler"

---

### Option 3: Transaction Pooler (Port 5432) - Not Recommended for Django ⚠️

```
postgresql://postgres.[PROJECT-REF]:[YOUR-PASSWORD]@aws-0-[REGION].pooler.supabase.com:5432/postgres
```

**Why not recommended:**
- Transaction mode can cause issues with Django ORM
- Connections are terminated after each transaction
- May cause "connection already closed" errors

---

## Key Differences

| Type | Port | Hostname | IPv4 Required | Best For |
|------|------|----------|---------------|----------|
| Session Pooler | 6543 | pooler.supabase.com | ✅ Yes | Django apps |
| Direct | 5432 | supabase.com | ❌ No | Small apps, testing |
| Transaction Pooler | 5432 | pooler.supabase.com | ✅ Yes | API backends (not Django) |

---

## Current Issue: "Connection Refused"

If you see:
```
connection to server at "aws-1-eu-north-1.pooler.supabase.com" (13.60.102.132), port 6543 failed: Connection refused
```

**You need to:**
1. ✅ Enable IPv4 Add-on in Supabase, OR
2. ✅ Switch to Direct Connection (port 5432, no pooler)

---

## How to Update in Render

1. Go to **Render Dashboard**
2. Select your service → **Environment** tab
3. Find `DATABASE_URL` variable
4. Click **Edit**
5. Paste the new connection string
6. Click **Save Changes** (this will trigger a redeploy)

---

## Testing the Connection

After updating, test in Render Shell:

```bash
# Check database configuration
python manage.py check --database default

# Test connection
python manage.py dbshell --command "SELECT version();"

# Run migrations
python manage.py migrate
```

---

## Common Mistakes

❌ **Wrong:** Using transaction pooler (5432) with Django  
✅ **Right:** Use session pooler (6543) with IPv4 enabled

❌ **Wrong:** Using session pooler (6543) without IPv4 add-on  
✅ **Right:** Enable IPv4 add-on OR switch to direct connection (5432)

❌ **Wrong:** Including "pooler" in hostname for direct connections  
✅ **Right:** Use direct hostname (aws-0-region.supabase.com)

---

## Need Help?

See `DATABASE_CONNECTION_FIX.md` for detailed troubleshooting steps.
