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
        "3. Use your Supabase connection string:\n"
        "   postgresql://postgres:3BH6CyUl5OpWDqtD@db.kcixuytszyzgvcybxyym.supabase.co:5432/postgres\n"
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
        "4. Value: postgresql://postgres:3BH6CyUl5OpWDqtD@db.kcixuytszyzgvcybxyym.supabase.co:5432/postgres\n"
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
    
    # Force IPv4 to avoid "Network is unreachable" errors on Render
    # Render's build environment doesn't support IPv6
    # Solution: Resolve the hostname to IPv4 and use hostaddr parameter
    import socket
    
    # Extract hostname from the database config
    db_host = db_config.get('HOST', '')
    
    if db_host and 'supabase.co' in db_host:
        try:
            # Try to get IPv4 address only
            ipv4_addresses = [
                addr[4][0] for addr in socket.getaddrinfo(
                    db_host, None, socket.AF_INET, socket.SOCK_STREAM
                )
            ]
            if ipv4_addresses:
                # Use the first IPv4 address
                db_config['OPTIONS'] = {
                    'sslmode': 'require',
                    'connect_timeout': 10,
                    'hostaddr': ipv4_addresses[0],  # Force IPv4 address
                }
                print(f"✓ Resolved {db_host} to IPv4: {ipv4_addresses[0]}")
            else:
                print(f"⚠ No IPv4 address found for {db_host}, using hostname")
                db_config['OPTIONS'] = {
                    'sslmode': 'require',
                    'connect_timeout': 10,
                }
        except socket.gaierror as e:
            print(f"⚠ DNS resolution failed for {db_host}: {e}")
            print(f"  Falling back to hostname without IPv4 resolution")
            db_config['OPTIONS'] = {
                'sslmode': 'require',
                'connect_timeout': 10,
            }
    else:
        db_config['OPTIONS'] = {
            'sslmode': 'require',
            'connect_timeout': 10,
        }
    
    DATABASES = {'default': db_config}
    
except ValueError as e:
    raise ValueError(
        f"Failed to parse DATABASE_URL: {str(e)}. "
        f"This usually means the port is invalid or the URL is malformed. "
        f"\n\nCurrent DATABASE_URL starts with: {DATABASE_URL[:60]}..."
        f"\n\nExpected format: postgresql://user:pass@host:5432/dbname"
    )

# Static files with WhiteNoise
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'

# CORS settings for production
CORS_ALLOWED_ORIGINS = os.environ.get('CORS_ALLOWED_ORIGINS', '').split(',')
if not CORS_ALLOWED_ORIGINS or CORS_ALLOWED_ORIGINS == ['']:
    CORS_ALLOWED_ORIGINS = ['https://nd.dovydas.space', 'https://api.dovydas.space']
CORS_ALLOW_CREDENTIALS = True

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
