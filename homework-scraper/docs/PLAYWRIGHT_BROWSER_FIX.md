# Playwright Browser Installation Fix for Render.com

## Problem
Playwright browsers weren't being found at runtime, showing error:
```
Executable doesn't exist at /opt/render/.cache/ms-playwright/chromium-1140/chrome-linux/chrome
```

## Root Cause
The `PLAYWRIGHT_BROWSERS_PATH` environment variable was set to `/opt/render/.cache/ms-playwright`, but:
1. This directory might not be writable during build
2. The browsers were being installed to a different location (default `~/.cache/ms-playwright`)
3. At runtime, Playwright was looking in the wrong location

## Solution
**Remove custom `PLAYWRIGHT_BROWSERS_PATH` and use Playwright's default location**

### Changes Made:

#### 1. `backend/build.sh`
- Install browsers to default location (`~/.cache/ms-playwright`)
- Added verification step to confirm browser installation
- Use `PLAYWRIGHT_SKIP_VALIDATE_HOST_REQUIREMENTS=true` to skip system dep checks

#### 2. `render.yaml`
- Removed `PLAYWRIGHT_BROWSERS_PATH` environment variable from web service
- Removed `PLAYWRIGHT_BROWSERS_PATH` environment variable from Celery worker
- Updated Celery worker build command to use `PLAYWRIGHT_SKIP_VALIDATE_HOST_REQUIREMENTS=true`

#### 3. Other fixes from previous iteration:
- Created `backend/package.json` to prevent Node.js auto-detection
- Created `backend/.renderignore` to ignore Node.js files
- Created `backend/.python-version` to explicitly set Python 3.11

## Why This Works

1. **Default Path is Reliable**: Playwright's default path (`~/.cache/ms-playwright`) is guaranteed to be writable during build and accessible at runtime
2. **Consistent Paths**: Both build-time and runtime now use the same default location
3. **No Sudo Required**: By skipping host requirements validation, we avoid the authentication failure
4. **Render Provides Dependencies**: Render's environment already has the necessary system libraries for Chromium

## Testing
After deploying, verify:
1. Check build logs for: `✓ Browsers installed successfully`
2. Test credential verification endpoint
3. Confirm no "Executable doesn't exist" errors in logs

## Alternative Approach (if still failing)
If the default path still has issues, you can explicitly set it during both build and runtime:

```bash
# In build.sh
export PLAYWRIGHT_BROWSERS_PATH=/opt/render/project/.cache/ms-playwright
playwright install chromium

# In render.yaml envVars
- key: PLAYWRIGHT_BROWSERS_PATH
  value: /opt/render/project/.cache/ms-playwright
```

The key is ensuring the **same path** is used during both build and runtime.
