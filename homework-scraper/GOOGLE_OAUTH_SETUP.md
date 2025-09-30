# Google OAuth Setup Instructions

To fix the "Network error occurred" issue, you need to configure Google OAuth credentials. Follow these steps:

## 1. Google Cloud Console Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the required APIs:
   - Go to "APIs & Services" → "Library"
   - Search for and enable:
     - Google OAuth2 API
     - Google Calendar API  
     - Google Tasks API

## 2. Create OAuth Credentials

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth 2.0 Client ID"
3. Configure the OAuth consent screen if prompted
4. Choose "Web application" as the application type
5. Add these URLs to "Authorized redirect URIs":
   ```
   http://localhost:8000/api/auth/google/callback/
   http://127.0.0.1:8000/api/auth/google/callback/
   ```
6. Click "Create"
7. Copy the Client ID and Client Secret

## 3. Update Environment Variables

Open `W:\automation\homework-scraper\.env` and add your credentials:

```env
# Google OAuth2 Settings
GOOGLE_OAUTH2_CLIENT_ID=your-client-id-here
GOOGLE_OAUTH2_CLIENT_SECRET=your-client-secret-here
```

## 4. Test the Setup

1. Make sure the Django server is running: http://localhost:8000
2. Make sure the Next.js frontend is running: http://localhost:3001
3. Navigate to the frontend and try the "Sign in with Google" button

## Current Status

✅ Django backend is running on http://localhost:8000
✅ Next.js frontend is running on http://localhost:3001  
✅ Database migrations applied
✅ CORS configured for both ports
❌ Google OAuth credentials need to be configured

## Testing the API

You can test if the backend is working by visiting:
http://localhost:8000/api/auth/google/login/

This should return an error about missing OAuth credentials, which confirms the API is accessible.

## Troubleshooting

If you still get network errors after setting up credentials:

1. Check that both servers are running
2. Verify the .env file has the correct credentials
3. Check browser developer tools for specific error messages
4. Ensure no firewall is blocking the connections