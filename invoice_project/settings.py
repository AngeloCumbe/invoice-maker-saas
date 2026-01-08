import os
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url

# Load .env file if it exists (for local development only)
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-change-this-in-production')

# Auto-detect Railway environment
IS_RAILWAY = bool(os.getenv('RAILWAY_ENVIRONMENT'))
ENVIRONMENT = 'production' if IS_RAILWAY else os.getenv('ENVIRONMENT', 'development')

DEBUG = os.getenv('DEBUG', 'False') == 'True' if not IS_RAILWAY else False

# ALLOWED_HOSTS for Railway
if IS_RAILWAY:
    # Railway dynamic domains: e.g., <project>.up.railway.app
    railway_project_id = os.getenv('RAILWAY_PROJECT_ID')
    ALLOWED_HOSTS = [f'{railway_project_id}.up.railway.app'] if railway_project_id else ['*']
    ALLOWED_HOSTS += os.getenv('ALLOWED_HOSTS', '').split(',')  # Allow custom overrides
else:
    ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL')

if DATABASE_URL:
    # Railway or any environment with DATABASE_URL (prioritized)
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=500,
            conn_health_checks=True,
            ssl_require=True,  # Railway databases often require SSL
        )
    }
else:
    # No DATABASE_URL found - raise error to prevent localhost fallback
    raise ValueError(
        "DATABASE_URL is not set. For Railway, ensure your PostgreSQL service is linked to your app. "
        "Check your Railway project dashboard > Services > PostgreSQL > Variables. "
        "For local dev, set DATABASE_URL in your .env file."
    )

# Static files
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
if IS_RAILWAY or ENVIRONMENT == 'production':
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

ROOT_URLCONF = 'invoice_project.urls'

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',
    'crispy_forms',
    'crispy_bootstrap5',
    'django_apscheduler',  # For scheduled tasks
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware' if IS_RAILWAY or ENVIRONMENT == 'production' else None,
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
# Filter out None from MIDDLEWARE
MIDDLEWARE = [m for m in MIDDLEWARE if m is not None]

# Security settings for Railway/production
if IS_RAILWAY or ENVIRONMENT == 'production':
    SECURE_SSL_REDIRECT = os.getenv('SECURE_SSL_REDIRECT', 'True') == 'True'
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    # Railway-specific: Ensure HTTPS
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

LOGIN_REDIRECT_URL = 'dashboard'
LOGIN_URL = 'login'

# Email configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', 'your-email@gmail.com')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', 'your-password')
DEFAULT_FROM_EMAIL = os.getenv('EMAIL_HOST_USER', 'your-email@gmail.com')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Timezone settings
USE_TZ = True
TIME_ZONE = os.getenv('TIME_ZONE', 'UTC')  # Or your preferred timezone like 'Asia/Manila'

# APScheduler Configuration for automatic overdue updates
SCHEDULER_CONFIG = {
    "apscheduler.jobstores.default": {
        "class": "django_apscheduler.jobstores:DjangoJobStore"
    },
    'apscheduler.executors.processpool': {
        "type": "threadpool"
    },
}

SCHEDULER_AUTOSTART = True

# Logging configuration
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
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
        'apscheduler': {
            'handlers': ['console'],
            'level': 'INFO',
        },
    },
}

# WSGI Application
WSGI_APPLICATION = 'invoice_project.wsgi.application'