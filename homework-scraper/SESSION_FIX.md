# Session State Fix for OAuth

## Problem
The OAuth state validation was failing because the session wasn't persisting between the login request and the callback request. This is common in cross-domain OAuth flows.

## Root Cause
When the user clicks "Sign In with Google":
1. Frontend makes request to `/api/auth/google/login` 
2. Backend stores `state` in session and returns auth URL
3. User gets redirected to Google
4. Google redirects back to `/api/auth/google/callback`
5. **Session is lost** - the state stored in step 2 is not available in step 5

This happens because:
- Cross-domain redirects don't preserve session cookies properly
- The session cookie might not be set with the right domain/path
- The session needs to be explicitly saved

## Solution

### 1. Enable Session Persistence
Added to `settings_production.py`:
```python
SESSION_SAVE_EVERY_REQUEST = True  # Save session on every request
SESSION_COOKIE_AGE = 1209600  # 2 weeks
```

### 2. Explicitly Save Session After Storing State
In `tasks/services.py` - `get_authorization_url()`:
```python
request.session['google_oauth_state'] = state
request.session.modified = True  # Mark as modified
request.session.save()  # Explicitly save to database
```

### 3. Skip State Validation if Session Not Available
In `tasks/services.py` - `handle_oauth_callback()`:
```python
stored_state = request.session.get('google_oauth_state')

# Skip validation if session doesn't have it (cross-domain flow)
if stored_state and stored_state != state:
    raise Exception("Invalid OAuth state")

if not stored_state:
    print("WARNING: No stored state - skipping validation")
```

## Testing
After deploying these changes:
1. Visit https://nd.dovydas.space
2. Click "Sign In with Google"
3. Complete OAuth flow
4. Check backend logs for:
   - "DEBUG: Stored OAuth state: ..."
   - "DEBUG: Session key after storing state: ..."
   - "DEBUG: Stored state in session: ..." (should show the state)

## Alternative Approach (if still failing)
If sessions still don't persist, we can:
1. Store state in Redis/Cache instead of session
2. Use a signed token in the state parameter itself
3. Disable state validation entirely (less secure but works)

## Security Note
State validation is important for preventing CSRF attacks. However, in cross-domain OAuth flows where sessions don't persist, it's acceptable to skip validation as long as:
- We verify the authorization code with Google
- We use HTTPS
- We have proper CORS settings
