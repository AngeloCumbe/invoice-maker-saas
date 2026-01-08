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
    # Fallback for build time or local dev without DATABASE_URL
    # Use a dummy in-memory SQLite DB to allow commands like collectstatic to run without errors
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',  # In-memory database (no file/connection needed)
        }
    }
    # Optional: Log a warning for local dev (but don't raise an error during build)
    import logging
    logging.warning(
        "DATABASE_URL is not set. Using dummy SQLite DB for build/local dev. "
        "For Railway, ensure your PostgreSQL service is linked. "
        "For local dev, set DATABASE_URL in your .env file."
    )