# OAuth Flow & User Profile Management

## Current OAuth Implementation

### Single OAuth Process ✅
**You only need to authenticate with Google once.** All user data is pulled from the Google OAuth response.

## How It Works

### 1. User Signs In with Google
```
User clicks "Login with Google" 
  → Frontend calls `/api/auth/google/login/`
  → Backend generates Google OAuth URL
  → User redirected to Google's sign-in page
```

### 2. Google OAuth Callback
```
User approves access
  → Google redirects to `/api/auth/google/callback/`
  → Backend exchanges code for access tokens
  → Backend fetches user info from Google:
      - email
      - first_name
      - last_name
  → Backend creates/updates User in database
  → Backend stores OAuth tokens in GoogleOAuth table
  → User session created
```

### 3. User Profile Data Source
**All profile data comes from Google OAuth:**
- ✅ `email` - from Google account
- ✅ `first_name` - from Google account  
- ✅ `last_name` - from Google account
- ✅ `has_google_oauth` - checked from database (always true after OAuth)

**No separate profile creation needed!**

### 4. Smart Redirect After OAuth
After successful OAuth, the system checks:

```python
if user has no site credentials:
    redirect to /settings?setup=credentials
    # Shows banner: "🔐 Setup Your Site Credentials"
elif user has unverified credentials:
    redirect to /settings?setup=credentials
    # Prompts to verify credentials
else:
    redirect to /dashboard
    # Ready to use!
```

## User Journey

### First-Time User
1. **Visit site** → http://localhost:3000
2. **Click "Login with Google"** (navbar or homepage)
3. **Authenticate with Google** (one time)
4. **Automatic redirect to Settings** with prompt to add site credentials
5. **Add Manodienynas/Eduka credentials** (username & password)
6. **Click "Save & Verify"** to test credentials
7. **Go to Dashboard** → Ready to scrape!

### Returning User
1. **Visit site** → Already signed in (session cookie)
2. **Profile data automatically loaded** from session
3. **Dashboard available immediately**

## API Endpoints

### Authentication Flow
```typescript
// 1. Get Google OAuth URL
GET /api/auth/google/login/
Response: { authorization_url: "https://accounts.google.com/..." }

// 2. OAuth callback (handled automatically)
GET /api/auth/google/callback/?code=xxx&state=xxx
Response: Redirects to /settings or /dashboard

// 3. Get user profile (anytime)
GET /api/auth/user/
Response: {
  user: {
    id: 1,
    email: "user@gmail.com",
    first_name: "John",
    last_name: "Doe",
    has_google_oauth: true,
    selected_sites: ["manodienynas", "eduka"],
    preferences: {}
  }
}

// 4. Logout
POST /api/auth/logout/
Response: { message: "Logged out successfully" }
```

### Site Credentials (Separate from OAuth)
```typescript
// Add site credentials
POST /api/auth/credentials/
Body: {
  site: "manodienynas",
  username: "student123",
  password: "password123"
}
Response: {
  message: "Credentials saved successfully",
  site: "manodienynas",
  username: "student123",
  is_verified: false
}

// Verify credentials
POST /api/auth/verify-credentials/
Body: { site: "manodienynas" }
Response: {
  success: true,
  message: "Credentials verified successfully",
  site: "manodienynas",
  verified: true
}

// Get credentials
GET /api/auth/credentials/
Response: {
  credentials: {
    manodienynas: {
      username: "student123",
      is_verified: true,
      last_verified: "2025-10-01T12:00:00Z"
    },
    eduka: {
      username: "student456",
      is_verified: true,
      last_verified: "2025-10-01T13:00:00Z"
    }
  }
}
```

## Data Storage

### Google OAuth Data
Stored in `authentication_googleoauth` table:
- `user_id` - Link to User
- `access_token` - Google API access token
- `refresh_token` - For renewing access
- `token_expiry` - When token expires
- Automatically refreshed when needed

### User Profile
Stored in `auth_user` table (Django default):
- `id` - Primary key
- `email` - From Google OAuth
- `first_name` - From Google OAuth
- `last_name` - From Google OAuth
- `username` - Set to email
- No password needed (OAuth only)

### Site Credentials
Stored in `authentication_usercredential` table:
- `user_id` - Link to User
- `site` - "manodienynas" or "eduka"
- `username` - Site login username
- `encrypted_password` - Encrypted password
- `is_verified` - Whether credentials work
- `last_verified` - Last verification time

### Session Data
Stored in Django sessions (cookies):
- `sessionid` cookie
- Automatically includes user authentication
- Persists across page reloads
- Secure HTTP-only cookies

## Frontend Implementation

### Checking Auth Status
```typescript
// In any component
import { authAPI } from '@/lib/api';

const checkAuth = async () => {
  try {
    const { user } = await authAPI.getUserProfile();
    // user.email, user.first_name, etc. all from OAuth
  } catch (error) {
    // Not authenticated
  }
};
```

### Google Sign-In
```typescript
// Unified sign-in function (used everywhere)
const handleGoogleSignIn = async () => {
  try {
    const { authorization_url } = await authAPI.getGoogleAuthUrl();
    window.location.href = authorization_url;
  } catch (error) {
    console.error('Sign-in failed:', error);
  }
};
```

### Components Using Auth
- ✅ `components/navbar.tsx` - Shows user profile, logout
- ✅ `app/page.tsx` - Homepage sign-in button
- ✅ `app/settings/page.tsx` - User profile card
- ✅ `app/dashboard/page.tsx` - Protected route

All use the **same OAuth flow** - no duplicate authentication!

## Security Features

### Token Management
- ✅ Access tokens auto-refresh when expired
- ✅ Refresh tokens securely stored
- ✅ Token expiry tracked and handled

### Credential Security
- ✅ Site passwords encrypted before storage
- ✅ Credentials never sent to frontend
- ✅ Verification happens server-side

### Session Security
- ✅ HTTP-only cookies (not accessible via JavaScript)
- ✅ Secure cookies (HTTPS in production)
- ✅ CSRF protection enabled
- ✅ CORS restricted to localhost

## Troubleshooting

### "User not authenticated" after OAuth
**Cause**: Session cookies not being sent
**Fix**: Ensure all fetch calls include `credentials: 'include'`
```typescript
fetch('/api/auth/user/', {
  credentials: 'include' // ← Important!
})
```

### Profile not loading in navbar
**Cause**: API base URL bypassing proxy
**Fix**: Already fixed! API now uses `/api` (proxy) instead of `http://localhost:8000/api`

### "Failed to fetch" errors
**Cause**: Next.js proxy not active or servers not running
**Fix**: 
1. Ensure both servers running: `.\start-servers.ps1`
2. Check Next.js on port 3000
3. Check Django on port 8000
4. Verify proxy in `next.config.js`

### OAuth redirects to wrong URL
**Cause**: Callback URL mismatch in Google Cloud Console
**Fix**: Ensure redirect URI is `http://localhost:3000/api/auth/google/callback/` in Google Console

## Summary

### ✅ Single OAuth Process
- **One Google sign-in** gets all user data
- **Profile automatically populated** from Google
- **No duplicate authentication** needed
- **Session persists** across page reloads

### ✅ Site Credentials Separate
- **Added after OAuth** in Settings
- **Used only for scraping** Manodienynas/Eduka
- **Verified independently** of OAuth
- **Encrypted and secure**

### ✅ Clean User Experience
1. Sign in with Google once
2. Add site credentials once
3. Everything works!

**No confusion, no duplicate OAuth, no manual profile creation!**

---

**Last Updated**: October 1, 2025
