# Playwright Browser Installation Fix for Render.com

## Problem
Playwright browsers weren't being found at runtime, showing error:
```
Executable doesn't exist at /opt/render/.cache/ms-playwright/chromium-1140/chrome-linux/chrome
```

## Root Cause
The browsers installed during the build phase were not persisted or accessible at runtime because:
1. The default location (`~/.cache/ms-playwright`) is tied to the build-time home directory
2. At runtime, the application runs under a different user context where `$HOME` points to a different location
3. Render's ephemeral build environment doesn't persist files outside the project directory

## Solution
**Install browsers to a persistent location within the project directory**

### Changes Made:

#### 1. `backend/build.sh`
```bash
# Install browsers to a persistent location in the project directory
export PLAYWRIGHT_BROWSERS_PATH=/opt/render/project/src/.playwright-browsers
mkdir -p "$PLAYWRIGHT_BROWSERS_PATH"
PLAYWRIGHT_SKIP_VALIDATE_HOST_REQUIREMENTS=true playwright install chromium
```

#### 2. `render.yaml`
**Web Service:**
```yaml
envVars:
  - key: PLAYWRIGHT_BROWSERS_PATH
    value: /opt/render/project/src/.playwright-browsers
```

**Celery Worker:**
```yaml
buildCommand: |
  export PLAYWRIGHT_BROWSERS_PATH=/opt/render/project/src/.playwright-browsers
  mkdir -p "$PLAYWRIGHT_BROWSERS_PATH"
  PLAYWRIGHT_SKIP_VALIDATE_HOST_REQUIREMENTS=true playwright install chromium

envVars:
  - key: PLAYWRIGHT_BROWSERS_PATH
    value: /opt/render/project/src/.playwright-browsers
```

## Why This Works

1. **Persistent Location**: `/opt/render/project/src/` is the project root directory that persists between build and runtime
2. **Same Path for Build & Runtime**: By setting `PLAYWRIGHT_BROWSERS_PATH` during both build and runtime, Playwright uses the exact same location
3. **No Sudo Required**: By skipping host requirements validation, we avoid authentication failures
4. **Render Provides Dependencies**: Render's environment already has the necessary system libraries for Chromium

## Key Insight
The critical issue was that Playwright defaults to `~/.cache/ms-playwright`, but:
- During **build**: `$HOME` = build user's home directory
- During **runtime**: `$HOME` = application user's home directory (different user!)

By using an absolute path within the project directory (`/opt/render/project/src/`), we ensure the browsers are:
- Installed during build ✓
- Persisted after build ✓
- Accessible at runtime ✓

## Testing
After deploying, verify:
1. Check build logs for: `✓ Browsers installed successfully at /opt/render/project/src/.playwright-browsers`
2. Check for: `✓ Chromium executable found at: [path]`
3. Test credential verification endpoint
4. Confirm no "Executable doesn't exist" errors in logs

## Troubleshooting
If issues persist:
1. Check that `PLAYWRIGHT_BROWSERS_PATH` is set in environment variables
2. Verify browser directory exists: Check build logs for the directory listing
3. Ensure the path is consistent between build.sh and render.yaml
4. Check file permissions in the project directory
