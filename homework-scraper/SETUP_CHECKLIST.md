# Quick Setup Checklist ✅

Use this checklist to get your Homework Scraper up and running!

## Prerequisites

- [ ] Python 3.10+ installed
- [ ] Node.js 18+ installed  
- [ ] Git repository cloned
- [ ] Google account for OAuth

## Backend Setup

- [ ] Create Python virtual environment
- [ ] Install Python dependencies (`pip install -r requirements.txt`)
- [ ] Create `.env` file in `backend/` directory
- [ ] Add `SECRET_KEY` to `.env`
- [ ] Run migrations (`python manage.py migrate`)
- [ ] Create superuser (optional: `python manage.py createsuperuser`)

## Google Cloud Console Setup

- [ ] Create/select Google Cloud project
- [ ] Enable APIs:
  - [ ] Google Tasks API
  - [ ] Google Calendar API
  - [ ] Google People API
- [ ] Configure OAuth consent screen
- [ ] Add your email as test user
- [ ] Create OAuth 2.0 credentials
- [ ] Copy Client ID and Client Secret
- [ ] Add redirect URIs:
  - [ ] `http://127.0.0.1:8000/api/auth/google/callback/`
  - [ ] `http://localhost:8000/api/auth/google/callback/`

## Environment Configuration

- [ ] Add `GOOGLE_OAUTH2_CLIENT_ID` to backend `.env`
- [ ] Add `GOOGLE_OAUTH2_CLIENT_SECRET` to backend `.env`
- [ ] Configure Supabase (if using):
  - [ ] Add `SUPABASE_URL`
  - [ ] Add `SUPABASE_KEY`

## Frontend Setup

- [ ] Install Node.js dependencies (`npm install`)
- [ ] No `.env` configuration needed (uses API proxy)

## Start Servers

- [ ] Run `.\start-servers.ps1` (Windows) or `./start-servers.sh` (Linux/Mac)
- [ ] Or start manually:
  - [ ] Backend: `cd backend && python manage.py runserver`
  - [ ] Frontend: `cd frontend && npm run dev`

## Verify Setup

- [ ] Run health check: `.\health-check.ps1`
- [ ] Open http://localhost:3000 in browser
- [ ] Click "Sign in with Google"
- [ ] Complete OAuth flow successfully
- [ ] Access dashboard at http://localhost:3000/dashboard

## Troubleshooting

If something doesn't work:

1. **Check logs** in both terminal windows
2. **Run health check**: `.\health-check.ps1`
3. **See** `TROUBLESHOOTING.md` for common issues
4. **See** `GOOGLE_OAUTH_SETUP.md` for OAuth setup details

## First-Time User Flow

After setup:

1. ✅ Sign in with Google
2. ✅ Grant permissions for Google Tasks and Calendar  
3. ✅ Complete onboarding (add school credentials)
4. ✅ Select sites to scrape (Manodienynas or Eduka)
5. ✅ Verify credentials
6. ✅ Start scraping homework!

---

## Current Status

**Your current issue**: 
> "You can't sign in to this app because it doesn't comply with Google's OAuth 2.0 policy"

**Next step**: 
1. Follow `GOOGLE_OAUTH_SETUP.md` to configure Google OAuth
2. Add the redirect URI in Google Cloud Console
3. Update your `.env` file with credentials
4. Restart servers
5. Try signing in again!
