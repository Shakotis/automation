# Credential Verification Fix - October 8, 2025

## Issues Identified

### 1. 403 Forbidden Error
- **Problem**: Manodienynas.lt was blocking verification requests with 403 status
- **Cause**: Single user agent being flagged as bot traffic or Cloudflare protection

### 2. CORS Error on 500 Response
- **Problem**: When backend crashed with 500 error, CORS headers were not added to response
- **Cause**: Error occurred before CORS middleware could process response
- **Result**: Frontend couldn't read error message from API

### 3. Production Settings Not Applied
- **Problem**: Production environment was using `settings.py` instead of `settings_production.py`
- **Cause**: Missing `DJANGO_SETTINGS_MODULE` environment variable in render.yaml

## Fixes Applied

### 1. Enhanced Error Handling in Verification Service
**File**: `backend/authentication/verification_service.py`

**Changes**:
- Added retry logic with multiple user agents to bypass 403 blocks
- Wrapped network requests in try-catch blocks to prevent crashes
- Added timeout parameters (15 seconds) to prevent hanging requests
- Added comprehensive error logging with traceback information
- Improved error messages for better debugging

**User Agents Tried** (in order):
1. Chrome on Windows 10
2. Firefox on Windows 10  
3. Chrome on macOS

**Benefits**:
- Prevents 500 errors from crashing the API
- Automatically retries with different user agents if blocked
- Graceful fallback with informative error messages
- Better debugging information in logs

### 2. Manual CORS Headers on Error Responses
**File**: `backend/authentication/views.py`

**Changes**:
- Added `_add_cors_headers()` helper method to `CredentialVerificationView`
- Manually adds CORS headers to ALL responses (success and error)
- Checks origin against allowed origins list
- Supports subdomain wildcards (*.dovydas.space)

**Headers Added**:
```
Access-Control-Allow-Origin: <origin>
Access-Control-Allow-Credentials: true
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
Access-Control-Allow-Headers: accept, accept-encoding, authorization, content-type, dnt, origin, user-agent, x-csrftoken, x-requested-with
```

**Benefits**:
- Frontend can now read error messages even when backend returns 500
- Consistent CORS headers across all response types
- Better error reporting to users

### 3. Production Settings Configuration
**File**: `render.yaml`

**Changes**:
Added `DJANGO_SETTINGS_MODULE` environment variable to all services:
- Web service: `homework_scraper.settings_production`
- Celery worker: `homework_scraper.settings_production`
- Celery beat: `homework_scraper.settings_production`

**Benefits**:
- Proper CORS configuration for production domains
- SSL/HTTPS enforcement
- PostgreSQL database connection (instead of SQLite)
- Production-grade security headers
- Proper session and CSRF cookie settings

## Testing Recommendations

### Update (October 8, 2025 - 19:18 UTC)
**Status**: Initial fix deployed successfully! ✅
- CORS errors are now fixed - frontend can read error messages
- 403 errors are properly handled without crashing the API
- However, Manodienynas.lt is still blocking `requests` library

**Additional Fix Applied**: Switched from `requests` library to **Playwright** for Manodienynas verification
- Playwright mimics a real browser much better than requests
- Passes Cloudflare and bot detection more reliably
- Same approach used by production scraper

### 1. Test Credential Verification
```bash
# Test with valid credentials
curl -X POST https://api.dovydas.space/api/auth/verify-credentials \
  -H "Content-Type: application/json" \
  -H "Cookie: sessionid=<your-session-id>" \
  -d '{"site": "manodienynas"}'
```

**Expected responses**:
- Success: `{"success": true, "message": "Credentials verified successfully", "site": "manodienynas", "verified": true}`
- 403 Block: `{"success": false, "message": "Access denied (403) - site may be blocking automated requests", "verified": false}`
- Invalid creds: `{"success": false, "message": "Login failed: Invalid credentials", "verified": false}`

### 2. Test CORS Headers
```bash
# Test OPTIONS preflight
curl -X OPTIONS https://api.dovydas.space/api/auth/verify-credentials \
  -H "Origin: https://nd.dovydas.space" \
  -H "Access-Control-Request-Method: POST" \
  -v
```

**Expected headers**:
```
Access-Control-Allow-Origin: https://nd.dovydas.space
Access-Control-Allow-Credentials: true
```

### 3. Monitor Logs
After deployment, check Render logs for:
- "✓ Connecting to Supabase" - confirms production settings loaded
- "Verifying Manodienynas credentials" - confirms verification attempts
- "Got 403 with user agent" - shows retry logic working
- No more unhandled 500 errors

## Deployment Steps

1. **Commit changes**:
```bash
git add backend/authentication/verification_service.py
git add backend/authentication/views.py
git add render.yaml
git commit -m "Fix credential verification 403 errors and CORS issues"
```

2. **Push to production**:
```bash
git push origin main
```

3. **Verify deployment**:
- Check Render dashboard for successful build
- Test credential verification from frontend
- Monitor logs for any errors

4. **If issues persist**:
- Check Render environment variables are set correctly
- Ensure `DATABASE_URL` is using Supabase (port 6543)
- Verify `CORS_ALLOWED_ORIGINS` includes your frontend domain
- Check `ENCRYPTION_KEY` is a valid Fernet key

## Additional Notes

### Why 403 Errors Happen
Manodienynas.lt likely uses:
- Cloudflare bot protection
- Rate limiting
- User-agent filtering
- IP-based blocking

### Retry Strategy
Our fix tries 3 different user agents before giving up. This should handle most temporary blocks while being respectful of the site's resources.

### Future Improvements
If 403 errors persist, consider:
1. Using Playwright instead of requests (more browser-like)
2. Adding exponential backoff between retries
3. Rotating proxy servers (if available)
4. Implementing request throttling on our end

### CORS Security
The CORS configuration is secure because:
- Only whitelisted origins are allowed
- Credentials are required (prevents CSRF)
- Specific methods and headers are defined
- Proper preflight handling

## Files Modified

1. `backend/authentication/verification_service.py` - Enhanced error handling and retry logic
2. `backend/authentication/views.py` - Manual CORS header addition
3. `render.yaml` - Production settings configuration

## No Breaking Changes

All changes are backwards compatible:
- API endpoints remain the same
- Response format is consistent
- Error codes are appropriate (401, 400, 500)
- Frontend code should work without changes
