"""
Production settings for Render.com deployment
"""
import os
import dj_database_url
from .settings import *

# Security settings
DEBUG = False
SECRET_KEY = os.environ.get('SECRET_KEY')

# Allowed hosts
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')
ALLOWED_HOSTS += ['.onrender.com', 'api.dovydas.space', '.dovydas.space']

# Database - PostgreSQL on Supabase
# Handle DATABASE_URL more robustly
DATABASE_URL = os.environ.get('DATABASE_URL', '')

# Check if DATABASE_URL contains placeholder text
if 'user:password@host:port' in DATABASE_URL or ':port/' in DATABASE_URL:
    raise ValueError(
        "DATABASE_URL contains placeholder text! "
        "This means the database is not properly configured. "
        "\n\n"
        "SOLUTION:\n"
        "1. Go to Render Dashboard → Your service → Environment\n"
        "2. Add environment variable: DATABASE_URL\n"
        "3. Use your Supabase connection string with DIRECT connection (port 5432):\n"
        "   postgresql://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:5432/postgres\n"
        "   OR use Session Pooler (port 6543):\n"
        "   postgresql://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres\n"
        "\n"
        f"Current DATABASE_URL: {DATABASE_URL[:80]}..."
    )

# Check if DATABASE_URL is properly set
if not DATABASE_URL or DATABASE_URL == '':
    raise ValueError(
        "DATABASE_URL environment variable is not set. "
        "\n\n"
        "SOLUTION:\n"
        "1. Go to Render Dashboard → Your service → Environment\n"
        "2. Click 'Add Environment Variable'\n"
        "3. Key: DATABASE_URL\n"
        "4. Value: Get from Supabase Dashboard → Settings → Database → Session pooler (port 6543)\n"
        "   Format: postgresql://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres\n"
        "5. Click 'Save Changes' to trigger rebuild\n"
    )

if 'postgresql://' not in DATABASE_URL and 'postgres://' not in DATABASE_URL:
    raise ValueError(
        f"DATABASE_URL must be a PostgreSQL connection string. "
        f"Current value: {DATABASE_URL[:50]}..."
    )

try:
    db_config = dj_database_url.config(
        default=DATABASE_URL,
        conn_max_age=600,
        conn_health_checks=True,
        ssl_require=True,  # Supabase requires SSL
    )
    
    # Supabase connection options
    # Important: Supabase Pooler has two modes:
    # - Port 6543: Session mode (pgBouncer) - RECOMMENDED for Django (best for long connections)
    # - Port 5432: Direct connection - may have connection limits
    # If you're getting "Connection refused" on port 5432, switch to port 6543
    
    db_host = db_config.get('HOST', '')
    db_port = db_config.get('PORT', 5432)
    
    # Configure SSL and connection options for Supabase
    db_config['OPTIONS'] = {
        'sslmode': 'require',
        'connect_timeout': 30,  # Increased timeout for pooler connections
        'keepalives': 1,
        'keepalives_idle': 30,
        'keepalives_interval': 10,
        'keepalives_count': 5,
    }
    
    # Provide helpful debugging info
    if 'supabase' in db_host.lower():
        print(f"✓ Connecting to Supabase: {db_host}:{db_port}")
        if int(db_port) == 5432:
            print(f"  ⚠ WARNING: Using port 5432 (Direct connection)")
            print(f"  ⚠ If you're getting 'Connection refused', update DATABASE_URL to use port 6543")
            print(f"  ⚠ Port 6543 (Session pooler) is recommended for Django applications")
        elif int(db_port) == 6543:
            print(f"  ✓ Using port 6543 (Session pooler - recommended for Django)")
        else:
            print(f"  ⚠ Unexpected port: {db_port}")
            print(f"  ⚠ Supabase typically uses port 6543 (pooler) or 5432 (direct)")
    
    DATABASES = {'default': db_config}
    
except ValueError as e:
    raise ValueError(
        f"Failed to parse DATABASE_URL: {str(e)}. "
        f"This usually means the port is invalid or the URL is malformed. "
        f"\n\n❌ SOLUTION - Fix your DATABASE_URL:"
        f"\n1. Go to Render Dashboard → Environment Variables"
        f"\n2. Update DATABASE_URL to use port 6543 (Session Pooler)"
        f"\n3. Format: postgresql://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres"
        f"\n\nCurrent DATABASE_URL starts with: {DATABASE_URL[:60]}..."
    )

# Static files with WhiteNoise
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'

# CORS settings for production
CORS_ALLOWED_ORIGINS = os.environ.get('CORS_ALLOWED_ORIGINS', '').split(',')
if not CORS_ALLOWED_ORIGINS or CORS_ALLOWED_ORIGINS == ['']:
    CORS_ALLOWED_ORIGINS = [
        'https://nd.dovydas.space',
        'https://api.dovydas.space',
        'https://dovydas.space',
        'https://www.dovydas.space'
    ]

# Enable CORS with credentials
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = False  # Explicitly set to False for security

# Allow all standard headers
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
    'cookie',  # Important for session cookies
]

CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

# Expose headers that frontend might need
CORS_EXPOSE_HEADERS = [
    'content-type',
    'x-csrftoken',
]

# CSRF settings
CSRF_TRUSTED_ORIGINS = os.environ.get('CSRF_TRUSTED_ORIGINS', '').split(',')
if not CSRF_TRUSTED_ORIGINS or CSRF_TRUSTED_ORIGINS == ['']:
    CSRF_TRUSTED_ORIGINS = ['https://nd.dovydas.space', 'https://api.dovydas.space']
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_SAMESITE = 'None'

# Session settings
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_SAMESITE = 'None'
SESSION_COOKIE_HTTPONLY = False  # Allow JavaScript access
SESSION_COOKIE_DOMAIN = '.dovydas.space'  # Share cookies across subdomains
SESSION_COOKIE_NAME = 'sessionid'
SESSION_ENGINE = 'django.contrib.sessions.backends.db'  # Use PostgreSQL for sessions
SESSION_SAVE_EVERY_REQUEST = True  # Save session on every request
SESSION_COOKIE_AGE = 1209600  # 2 weeks in seconds

# Security headers
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
X_FRAME_OPTIONS = 'DENY'
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True

# Celery with Redis
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', os.environ.get('REDIS_URL'))
CELERY_RESULT_BACKEND = os.environ.get('CELERY_BROKER_URL', os.environ.get('REDIS_URL'))

# Frontend URL for OAuth redirects
FRONTEND_URL = os.environ.get('FRONTEND_URL', 'https://nd.dovydas.space')

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}
