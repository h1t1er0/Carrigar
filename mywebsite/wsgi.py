"""
WSGI config for mywebsite project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
import sys
import logging
from django.core.wsgi import get_wsgi_application

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mywebsite.settings')

try:
    application = get_wsgi_application()
    logger.info("Django application initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Django application: {e}")
    raise

# Vercel serverless function handler
def handler(request, response):
    try:
        return application(request, response)
    except Exception as e:
        logger.error(f"Error in WSGI handler: {e}")
        raise

# For compatibility
app = application
