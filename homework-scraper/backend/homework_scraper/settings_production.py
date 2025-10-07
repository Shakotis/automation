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
ALLOWED_HOSTS += ['.onrender.com']

# Database - PostgreSQL on Render
# Handle DATABASE_URL more robustly
DATABASE_URL = os.environ.get('DATABASE_URL', '')

# Check if DATABASE_URL is properly set
if not DATABASE_URL or DATABASE_URL == '' or 'postgresql://' not in DATABASE_URL:
    raise ValueError(
        "DATABASE_URL environment variable is not properly set. "
        "Please configure it in Render Dashboard with format: "
        "postgresql://user:password@host:port/database"
    )

try:
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
except ValueError as e:
    raise ValueError(
        f"Failed to parse DATABASE_URL: {str(e)}. "
        f"Check that your DATABASE_URL is properly formatted. "
        f"Current value starts with: {DATABASE_URL[:30]}..."
    )

# Static files with WhiteNoise
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'

# CORS settings for production
CORS_ALLOWED_ORIGINS = os.environ.get('CORS_ALLOWED_ORIGINS', '').split(',')
CORS_ALLOW_CREDENTIALS = True

# CSRF settings
CSRF_TRUSTED_ORIGINS = os.environ.get('CSRF_TRUSTED_ORIGINS', '').split(',')
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
