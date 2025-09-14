"""
Django settings for TidyGen ERP project.

This file imports environment-specific settings based on the DJANGO_SETTINGS_MODULE
environment variable or defaults to development settings.
"""

import os
from decouple import config

# Determine which settings to use
DJANGO_ENV = config('DJANGO_ENV', default='development')

if DJANGO_ENV == 'production':
    from .settings.production import *
elif DJANGO_ENV == 'staging':
    from .settings.staging import *
else:
    from .settings.development import *