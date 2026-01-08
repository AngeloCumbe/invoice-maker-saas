# core/apps.py
from django.apps import AppConfig
import os
import logging

logger = logging.getLogger(__name__)


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        """
        This method is called when Django starts.
        We use it to start our scheduler.
        """
        import sys
        
        # Check if DATABASE_URL is set (required for scheduler to work)
        if not os.getenv('DATABASE_URL'):
            logger.warning("DATABASE_URL not set - skipping scheduler startup")
            return
        
        # Only start scheduler if we're running the server
        # Don't start it for management commands like makemigrations, migrate, etc.
        if 'runserver' in sys.argv or 'gunicorn' in sys.argv[0]:
            try:
                from . import scheduler
                scheduler.start_scheduler()
            except Exception as e:
                logger.error(f"Error starting scheduler: {str(e)}")