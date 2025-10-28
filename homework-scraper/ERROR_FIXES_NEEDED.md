# Server Errors Summary & Fixes

## ✅ FIXED: CSRF 403 Errors on Monitoring API
**Issue:** Monitoring endpoints returning 403 Forbidden
**Fix Applied:** Added `@csrf_exempt` decorator to all monitoring views
**Status:** ✅ Fixed - Restart applied

---

## ⚠️ DNS/Network Errors - "[Errno -2] Name or service not known"

### Problem:
```
Error getting site selections for user: [Errno -2] Name or service not known
Error getting user profile from Supabase: [Errno -2] Name or service not known
```

### Root Cause:
Your `.env` file has a placeholder Supabase URL:
```
SUPABASE_URL=https://your-project.supabase.co
```

### Fix Required:
1. Get your actual Supabase project URL from https://app.supabase.com
2. Update `.env` file on the RPI server:
   ```bash
   ssh -i ~/.ssh/rpi_3 dovydukas@192.168.0.88
   cd /home/dovydukas/homework-scraper-backend
   nano .env
   # Replace: SUPABASE_URL=https://your-project.supabase.co
   # With: SUPABASE_URL=https://YOUR_ACTUAL_PROJECT.supabase.co
   sudo systemctl restart homework-scraper.service
   ```

---

## ⚠️ Credential Decryption Errors

### Problem:
```
Error decrypting credentials:
Error decrypting credentials for eduka:
Error getting credentials for user 1 on site eduka:
```

### Possible Causes:
1. **Encryption key changed** - Credentials encrypted with different key
2. **Corrupted credential data** - Database contains invalid encrypted data
3. **Wrong encryption key format** - Key not properly formatted

### Fix Options:

#### Option 1: Verify Encryption Key
```bash
ssh -i ~/.ssh/rpi_3 dovydukas@192.168.0.88
cd /home/dovydukas/homework-scraper-backend
# Check key length (should be 32 bytes base64 encoded)
python3 << EOF
import os
from decouple import config
key = config('ENCRYPTION_KEY')
print(f"Key length: {len(key)} characters")
# Should be 44 characters for Fernet key (32 bytes base64)
EOF
```

#### Option 2: Re-encrypt Credentials
If encryption key was changed, users need to re-enter credentials through the settings page.

#### Option 3: Generate New Encryption Key
If starting fresh:
```bash
python3 << EOF
from cryptography.fernet import Fernet
print(Fernet.generate_key().decode())
EOF
# Update .env with new key
# Users will need to re-enter credentials
```

---

## ⚠️ Missing Python Module - brotli

### Problem:
```
Failed to scrape exams: No module named 'brotli'
```

### Fix:
```bash
ssh -i ~/.ssh/rpi_3 dovydukas@192.168.0.88
cd /home/dovydukas/homework-scraper-backend
source venv/bin/activate
pip install brotli
sudo systemctl restart homework-scraper.service
sudo systemctl restart homework-scraper-celery.service
```

---

## 🔍 Recommended Actions (Priority Order)

### 1. Install Missing Module (URGENT)
This is preventing scraping from working.

### 2. Fix Supabase URL (IMPORTANT)
This causes errors on every API request trying to sync with Supabase.

### 3. Investigate Encryption Issues (IMPORTANT)
Users can't save/retrieve credentials until fixed.

---

## Quick Fix Script

Run this on the RPI server:

```bash
#!/bin/bash
echo "=== Installing brotli module ==="
cd /home/dovydukas/homework-scraper-backend
source venv/bin/activate
pip install brotli

echo ""
echo "=== Current .env Configuration ==="
echo "SUPABASE_URL: $(grep SUPABASE_URL .env | cut -d'=' -f2 | sed 's|https://||' | cut -d'/' -f1)"
echo "ENCRYPTION_KEY length: $(grep ENCRYPTION_KEY .env | cut -d'=' -f2 | wc -c) characters"

echo ""
echo "⚠️  ACTION REQUIRED:"
echo "1. Update SUPABASE_URL in .env with your actual project URL"
echo "2. Verify ENCRYPTION_KEY is 44 characters long"
echo "3. Have users re-enter credentials in Settings if decryption fails"

echo ""
echo "Restarting services..."
sudo systemctl restart homework-scraper.service
sudo systemctl restart homework-scraper-celery.service

echo ""
echo "✓ Done! Check status:"
echo "  sudo systemctl status homework-scraper.service"
```

---

## Testing After Fixes

1. **Test Monitoring Dashboard:**
   - Visit: http://192.168.0.88/logs/ or https://api.dovydas.space/logs
   - All tabs should load without 403 errors ✅

2. **Test Supabase Connection:**
   ```bash
   journalctl -u homework-scraper.service -f | grep -i supabase
   ```
   Should not show DNS errors after URL fix.

3. **Test Credential Storage:**
   - Log in to https://dovydas.space/settings
   - Try saving Eduka credentials
   - Should not show decryption errors

4. **Test Scraping:**
   ```bash
   journalctl -u homework-scraper-celery.service -f
   ```
   Should not show "No module named 'brotli'" errors.
