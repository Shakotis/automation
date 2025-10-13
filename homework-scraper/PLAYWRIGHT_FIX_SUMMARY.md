# Playwright Browser Fix - Summary

## Issue
```
Error: Verification failed: BrowserType.launch: Executable doesn't exist at /opt/render/.cache/ms-playwright/chromium-1140/chrome-linux/chrome
```

## Root Cause
Playwright browsers installed during build were not accessible at runtime because:
- Build-time `$HOME` ≠ Runtime `$HOME` (different users)
- Default location `~/.cache/ms-playwright` wasn't persisted between build and runtime phases

## Solution Applied

### 1. Use Persistent Project Directory Path
Changed from: `~/.cache/ms-playwright` (ephemeral)  
Changed to: `/opt/render/project/src/.playwright-browsers` (persistent)

### 2. Files Modified

#### `backend/build.sh`
- Set `PLAYWRIGHT_BROWSERS_PATH=/opt/render/project/src/.playwright-browsers`
- Create directory before installing browsers
- Added verification to confirm browser installation and find executable

#### `render.yaml`
**Web Service:**
- Added environment variable: `PLAYWRIGHT_BROWSERS_PATH=/opt/render/project/src/.playwright-browsers`

**Celery Worker:**
- Updated build command to set `PLAYWRIGHT_BROWSERS_PATH` and create directory
- Added environment variable: `PLAYWRIGHT_BROWSERS_PATH=/opt/render/project/src/.playwright-browsers`

#### `docs/PLAYWRIGHT_BROWSER_FIX.md`
- Updated documentation to reflect the persistent path solution
- Added troubleshooting section

## Why This Works
✅ Path is within project directory → persists after build  
✅ Same absolute path used during build and runtime  
✅ No dependency on `$HOME` environment variable  
✅ Skips system dependency validation to avoid sudo issues  

## Deployment Steps
1. Commit and push these changes to your repository
2. Render will automatically rebuild with the new configuration
3. Monitor build logs for:
   - `✓ Browsers installed successfully at /opt/render/project/src/.playwright-browsers`
   - `✓ Chromium executable found at: [path]`
4. Test credential verification endpoint after deployment

## Verification
After deployment, check:
1. Build logs show successful browser installation
2. Credential verification works without "Executable doesn't exist" errors
3. Both web service and Celery worker can use Playwright

## Related Files
- `backend/build.sh` - Build script with browser installation
- `render.yaml` - Render deployment configuration
- `docs/PLAYWRIGHT_BROWSER_FIX.md` - Detailed documentation
