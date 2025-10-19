# Login and Playwright Browser Fix

## Issues Fixed

### 1. Frontend Not Recognizing Logged-In State ✅

**Problem:** After OAuth callback redirect, the frontend still showed "Login with Google" button even though user was authenticated.

**Root Cause:** The OAuth callback was returning an HTML page with JavaScript that set localStorage, but the frontend doesn't check localStorage for authentication. It only checks the `/api/auth/user` endpoint with session cookies.

**Solution:**
- Changed OAuth callback to use simple `HttpResponseRedirect` instead of HTML page
- Removed unnecessary localStorage manipulation
- Ensured session cookie is explicitly set with correct domain (`.dovydas.space`)
- Set `SameSite=None` for cross-subdomain cookies in production
- Set `httponly=False` to allow JavaScript access (needed for cross-origin)

**Files Changed:**
- `backend/authentication/views.py` - Simplified redirect logic in `GoogleOAuthCallbackView`

**Key Settings (already correct in `settings_production.py`):**
```python
SESSION_COOKIE_DOMAIN = '.dovydas.space'  # Share across subdomains
SESSION_COOKIE_SECURE = True              # HTTPS only
SESSION_COOKIE_SAMESITE = 'None'          # Cross-domain allowed
SESSION_COOKIE_HTTPONLY = False           # Allow JS access
CORS_ALLOW_CREDENTIALS = True             # Allow cookies in CORS
```

### 2. Playwright Browser Not Found on Render ✅

**Problem:** 
```
playwright._impl._errors.Error: BrowserType.launch: Executable doesn't exist at /opt/render/.cache/ms-playwright/chromium-1140/chrome-linux/chrome
```

**Root Cause:** Playwright browsers weren't being installed during the build process, or system dependencies were missing.

**Solution:**

#### Updated `backend/build.sh`:
1. Added system dependency installation for Chromium:
   - libnss3, libnspr4, libatk1.0-0, libatk-bridge2.0-0
   - libcups2, libdrm2, libdbus-1-3, libxkbcommon0
   - libxcomposite1, libxdamage1, libxfixes3, libxrandr2
   - libgbm1, libpango-1.0-0, libcairo2, libasound2, libatspi2.0-0

2. Enhanced Playwright installation with fallback:
   ```bash
   playwright install chromium --with-deps || playwright install chromium
   ```

3. Added verification and debugging output

#### Updated `backend/Dockerfile`:
- Added all required system dependencies for Chromium
- Removed old Selenium/ChromeDriver setup (no longer used)
- Added Playwright browser installation step

#### Updated `backend/authentication/verification_service.py`:
- Added environment variable support for `PLAYWRIGHT_BROWSERS_PATH`
- Enhanced browser launch with better error logging
- Added more browser flags for stability:
  - `--disable-software-rasterizer`
  - `--disable-dev-tools`

#### Updated `backend/homework_scraper/settings.py`:
- Added Playwright browser path configuration:
  ```python
  PLAYWRIGHT_BROWSERS_PATH = os.environ.get('PLAYWRIGHT_BROWSERS_PATH', 
                                           os.path.join(BASE_DIR, '.playwright-browsers'))
  ```

## Deployment Steps

### For Render.com:

1. **Push changes to GitHub**
   ```bash
   git add .
   git commit -m "Fix: OAuth redirect and Playwright browser installation"
   git push
   ```

2. **Trigger Redeploy**
   - Go to Render Dashboard → Your Service
   - Click "Manual Deploy" → "Deploy latest commit"
   - Or wait for automatic deployment if auto-deploy is enabled

3. **Monitor Build Logs**
   Watch for these success indicators:
   - ✓ Installing Playwright browsers...
   - ✓ Browsers installed successfully at /opt/render/project/src/.playwright-browsers
   - ✓ Chromium executable found at: [path]

4. **Test Authentication Flow**
   - Visit https://nd.dovydas.space
   - Click "Login with Google"
   - Complete OAuth flow
   - Should redirect to onboarding/dashboard
   - Frontend should recognize logged-in state (no more "Login with Google" button)

5. **Test Credential Verification**
   - Go to Settings → Add Credentials
   - Add Manodienynas or Eduka credentials
   - Click "Verify"
   - Should succeed without browser errors

## Environment Variables (if needed)

If browsers still aren't found, add this environment variable in Render:

```
PLAYWRIGHT_BROWSERS_PATH=/opt/render/project/src/.playwright-browsers
```

## Troubleshooting

### If login still doesn't work:
1. Check browser cookies - make sure `sessionid` cookie is set for `.dovydas.space`
2. Check CORS settings - make sure `nd.dovydas.space` is in `CORS_ALLOWED_ORIGINS`
3. Check browser console for CORS errors
4. Try clearing cookies and logging in again

### If Playwright still fails:
1. Check build logs for "playwright install" output
2. SSH into Render shell: `cd /opt/render/project/src/backend && playwright install chromium`
3. Check if browsers are in `/opt/render/project/src/.cache/ms-playwright/`
4. Verify system dependencies are installed: `apt list --installed | grep -E "libnss3|libgbm1"`

## Testing Locally

### Test OAuth Flow:
```bash
cd backend
python manage.py runserver
```
Then visit http://localhost:3000 and test login

### Test Playwright:
```bash
cd backend
python -c "from playwright.sync_api import sync_playwright; p = sync_playwright().start(); browser = p.chromium.launch(); print('✓ Playwright works!'); browser.close()"
```

## Notes

- Session cookies are now shared across `nd.dovydas.space` and `api.dovydas.space` using domain `.dovydas.space`
- `SameSite=None` requires `Secure=True` (HTTPS only)
- Playwright browsers are ~200MB, build may take longer
- Browsers are cached in build, so subsequent builds are faster
