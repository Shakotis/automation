# Homework Scraper

A web application that automatically scrapes homework from Lithuanian educational websites (Manodienynas.lt and Eduka.lt) and syncs them to Google Tasks.

## Features

- 🤖 **Automated Scraping**: Automatically scrape homework from Manodienynas.lt and Eduka.lt
- 📋 **Google Tasks Integration**: Sync homework directly to your Google Tasks "Homework" list
- 🎨 **Modern UI**: Clean, minimalistic interface built with HeroUI and TailwindCSS
- 🔐 **Secure Authentication**: Google OAuth2 for secure access
- 💾 **Data Backup**: Supabase integration for data storage and backup
- ⚙️ **Configurable**: Customize scraping frequency and site preferences

## Tech Stack

### Frontend
- **Next.js 14** with App Router
- **HeroUI** component library
- **TailwindCSS** for styling
- **TypeScript** for type safety

### Backend
- **Django** with Django REST Framework
- **Selenium** for web scraping
- **Google APIs** for Tasks integration
- **Supabase** for database storage
- **Celery** for background tasks (optional)

## Setup Instructions

### Prerequisites

- Node.js 18+ and npm
- Python 3.11+
- Google Cloud Console project with Tasks API enabled
- Supabase account and project

### 1. Clone and Setup

```bash
git clone <repository-url>
cd homework-scraper
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
.\venv\Scripts\Activate.ps1
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
```

### 3. Configure Backend Environment

Edit `backend/.env`:

```env
# Django settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Google OAuth2 settings
GOOGLE_OAUTH2_CLIENT_ID=your-google-client-id
GOOGLE_OAUTH2_CLIENT_SECRET=your-google-client-secret

# Supabase settings
SUPABASE_URL=your-supabase-url
SUPABASE_KEY=your-supabase-anon-key
```

### 4. Google Cloud Console Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the Google Tasks API
4. Create OAuth 2.0 credentials:
   - Application type: Web application
   - Authorized redirect URIs: `http://localhost:3000/auth/google/callback/`
5. Copy the Client ID and Client Secret to your `.env` files

### 5. Supabase Setup

1. Create a new Supabase project
2. Get your project URL and anon key
3. Run the SQL scripts from `backend/scraper/supabase_service.py` to create tables

### 6. Run Django Migrations

```bash
cd backend
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser  # Optional: for admin access
```

### 7. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Copy environment file
cp .env.example .env.local
```

### 8. Configure Frontend Environment

Edit `frontend/.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
NEXT_PUBLIC_SITE_URL=http://localhost:3000
NEXT_PUBLIC_GOOGLE_CLIENT_ID=your-google-client-id
```

### 9. Start Development Servers

**Terminal 1 - Backend:**
```bash
cd backend
python manage.py runserver
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

### 10. Access the Application

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/api
- Django Admin: http://localhost:8000/admin

## Usage

1. **Sign In**: Click "Sign in with Google" to authenticate
2. **Configure Settings**: Go to Settings to enable sites and configure scraping frequency
3. **View Dashboard**: See overview of scraped homework and sync status
4. **Manage Homework**: Browse, filter, and manually sync homework items
5. **Auto Sync**: Enable automatic syncing to Google Tasks in Settings

## Important Notes

### Web Scraping Compliance

- This application is designed for personal educational use
- Ensure you comply with the terms of service of the target websites
- The scrapers may need updates if website structures change
- Consider implementing rate limiting and respectful scraping practices

### Authentication & Security

- OAuth tokens are stored securely in the database
- Use environment variables for all sensitive configuration
- In production, ensure HTTPS is enabled
- Consider implementing additional security measures for production deployment

### Data Privacy

- User data is stored in your Supabase instance
- No data is shared with third parties except for Google Tasks API calls
- Users can revoke access at any time through their Google account settings

## Deployment

### Backend Deployment (Heroku Example)

1. Install Heroku CLI
2. Create Heroku app: `heroku create homework-scraper-api`
3. Add environment variables: `heroku config:set SECRET_KEY=...`
4. Deploy: `git push heroku main`

### Frontend Deployment (Vercel Example)

1. Install Vercel CLI: `npm i -g vercel`
2. Deploy: `vercel --prod`
3. Set environment variables in Vercel dashboard

## Development

### Backend Structure
```
backend/
├── homework_scraper/     # Django project settings
├── authentication/       # Google OAuth handling
├── scraper/             # Web scraping logic and models
├── tasks/               # Google Tasks integration
└── requirements.txt
```

### Frontend Structure
```
frontend/
├── app/                 # Next.js 14 app directory
├── components/          # Reusable UI components
├── lib/                 # API client and utilities
└── config/              # Application configuration
```

### Adding New Scrapers

To add support for additional educational websites:

1. Create a new scraper class in `backend/scraper/scrapers.py`
2. Inherit from `BaseScraper`
3. Implement the `scrape_homework()` method
4. Add the site to `SITE_CHOICES` in models
5. Update the frontend UI to include the new site

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is for educational purposes. Please ensure compliance with website terms of service.

## Troubleshooting

### Common Issues

1. **Chrome Driver Issues**: Install ChromeDriver and ensure it's in PATH
2. **OAuth Errors**: Verify redirect URIs match exactly in Google Console
3. **CORS Issues**: Check Django CORS settings in `settings.py`
4. **Database Errors**: Ensure Supabase connection details are correct

### Logs

- Django logs: Check console output
- Next.js logs: Check browser console and terminal
- Scraping logs: Check Django console for scraper errors

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review Django and Next.js documentation
3. Check Google APIs documentation for Tasks API
4. Create an issue in the repository