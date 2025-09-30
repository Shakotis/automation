# Homework Scraper - Setup Guide

This guide will help you set up the complete homework scraper system with Google OAuth authentication, Supabase user storage, secure credential management, and Google Calendar/Tasks integration.

## Features Implemented

✅ **Google OAuth Authentication** - Users sign in with their Google accounts
✅ **Supabase User Management** - All user data is stored in Supabase
✅ **Secure Credential Storage** - Site credentials are encrypted and stored securely
✅ **Site Selection Interface** - First-time users select which sites to scrape
✅ **Credential Input & Verification** - Users input and verify their site credentials
✅ **Google Calendar Integration** - Sync homework and exams to Google Calendar
✅ **Google Tasks Integration** - Alternative sync target for homework and exams
✅ **Exam Date Management** - Create and manage exam events

## Prerequisites

1. **Python 3.13+** and **Node.js 18+**
2. **Google Cloud Project** with OAuth2 and Calendar/Tasks APIs enabled
3. **Supabase Project** (free tier available)
4. **Redis Server** (for background tasks)

## Setup Instructions

### 1. Clone and Install Dependencies

```bash
# Backend setup
cd homework-scraper/backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Frontend setup
cd ../frontend
npm install
```

### 2. Environment Configuration

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

### 3. Google Cloud Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable APIs:
   - Google OAuth2 API
   - Google Calendar API
   - Google Tasks API
4. Create OAuth2 credentials:
   - Go to "Credentials" → "Create Credentials" → "OAuth 2.0 Client ID"
   - Application type: Web application
   - Authorized redirect URIs: `http://localhost:8000/auth/google/callback/`
5. Copy Client ID and Secret to your `.env` file

### 4. Supabase Setup

1. Go to [Supabase](https://supabase.com/) and create a new project
2. Copy your project URL and anon key to `.env`
3. In Supabase SQL Editor, run this SQL to create tables:

```sql
-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,
    django_user_id INTEGER UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    first_name VARCHAR(150),
    last_name VARCHAR(150),
    username VARCHAR(150),
    is_active BOOLEAN DEFAULT true,
    preferences JSONB DEFAULT '{}',
    date_joined TIMESTAMP WITH TIME ZONE,
    last_login TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create user_site_selections table
CREATE TABLE IF NOT EXISTS user_site_selections (
    id BIGSERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(django_user_id) ON DELETE CASCADE,
    site_name VARCHAR(100) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_users_django_id ON users(django_user_id);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_site_selections_user ON user_site_selections(user_id);
```

### 5. Database Migration

```bash
cd homework-scraper/backend
python manage.py migrate
python manage.py migrate authentication
```

### 6. Start Services

```bash
# Start Redis (required for background tasks)
redis-server

# Start Django backend
cd homework-scraper/backend
python manage.py runserver

# Start Next.js frontend
cd homework-scraper/frontend
npm run dev
```

### 7. First Time Setup

1. Navigate to `http://localhost:3000`
2. Click "Sign in with Google"
3. Complete the onboarding flow:
   - Select sites you want to scrape
   - Enter credentials for each site
   - Verify credentials work
4. Configure your integration preferences (Google Tasks vs Calendar)

## API Endpoints

### Authentication
- `GET /auth/google/login/` - Initiate Google OAuth
- `GET /auth/google/callback/` - OAuth callback
- `GET /auth/user/` - Get user profile
- `POST /auth/logout/` - Logout

### Site Management
- `GET /auth/sites/` - Get available sites
- `POST /auth/sites/` - Save site selections

### Credential Management
- `GET /auth/credentials/` - Get user credentials (without passwords)
- `POST /auth/credentials/` - Store credentials
- `PUT /auth/credentials/` - Update verification status
- `DELETE /auth/credentials/` - Delete credentials
- `POST /auth/verify-credentials/` - Verify credentials

### Google Integration
- `POST /tasks/sync/` - Sync to Google Tasks
- `POST /tasks/calendar/sync/` - Sync to Google Calendar
- `GET /tasks/calendar/calendars/` - Get user calendars
- `POST /tasks/calendar/exam/` - Create exam event
- `GET /tasks/preferences/` - Get integration preferences
- `POST /tasks/preferences/` - Update integration preferences

## Security Features

1. **Encrypted Credential Storage** - All site passwords are encrypted using Fernet encryption
2. **Secure OAuth Flow** - Proper state validation and token management
3. **Environment-based Secrets** - All sensitive data in environment variables
4. **CORS Protection** - Frontend/backend communication secured
5. **Session Management** - Secure user sessions with Django

## Supported Sites

Currently supports credential verification for:
- Blackboard
- Canvas
- Moodle
- Google Classroom (OAuth-based)
- Microsoft Teams for Education
- Schoology

## Troubleshooting

### OAuth Issues
- Ensure redirect URIs match exactly in Google Cloud Console
- Check that APIs are enabled in Google Cloud
- Verify client ID and secret are correct

### Database Issues
- Make sure Supabase tables are created
- Check database connection settings
- Run migrations if models change

### Credential Verification Issues
- Ensure Selenium WebDriver is installed
- Check site URLs are correct
- Some sites may have CAPTCHA or 2FA enabled

### Integration Issues
- Verify Google Calendar/Tasks APIs are enabled
- Check OAuth scopes include calendar and tasks permissions
- Ensure proper token refresh handling

## Development Notes

- Frontend uses Next.js with HeroUI components
- Backend uses Django REST Framework
- Credential verification uses Selenium for site login testing
- Background tasks handled by Celery with Redis
- User data synchronized between Django and Supabase

## Security Considerations

1. Always use HTTPS in production
2. Regularly rotate encryption keys
3. Implement rate limiting for credential verification
4. Monitor for suspicious login patterns
5. Keep dependencies updated

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review API endpoint documentation
3. Check Django and Next.js logs
4. Verify environment configuration