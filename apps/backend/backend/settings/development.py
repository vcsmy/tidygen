"""
Development settings for TidyGen ERP project.
"""

from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

# Development-specific apps (only if installed)
# INSTALLED_APPS += [
#     'debug_toolbar',
#     'silk',
# ]

# Development-specific middleware (only if installed)
# MIDDLEWARE += [
#     'debug_toolbar.middleware.DebugToolbarMiddleware',
#     'silk.middleware.SilkyMiddleware',
# ]

# Debug toolbar configuration
INTERNAL_IPS = [
    '127.0.0.1',
    'localhost',
]

# DEBUG_TOOLBAR_CONFIG = {
#     'SHOW_TEMPLATE_CONTEXT': True,
# }

# Silk profiling configuration
# SILKY_PYTHON_PROFILER = True
# SILKY_PYTHON_PROFILER_BINARY = True
# SILKY_AUTHENTICATION = True
# SILKY_AUTHORISATION = True
# SILKY_PERMISSIONS = lambda user: user.is_superuser

# CORS settings for development
CORS_ALLOW_ALL_ORIGINS = True

# Security settings for development
SECURE_SSL_REDIRECT = False
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False

# Email backend for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Logging for development
LOGGING['handlers']['file']['class'] = 'logging.StreamHandler'
LOGGING['handlers']['file']['formatter'] = 'verbose'
# Remove filename for StreamHandler
if 'filename' in LOGGING['handlers']['file']:
    del LOGGING['handlers']['file']['filename']
LOGGING['loggers']['apps']['level'] = 'DEBUG'
LOGGING['loggers']['django']['level'] = 'DEBUG'

# Database configuration for development
# DATABASES['default'].update({
#     'OPTIONS': {
#         'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
#     }
# })

# Cache configuration for development (using local memory cache)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# Session configuration for development
SESSION_ENGINE = 'django.contrib.sessions.backends.db'

# JWT settings for development (shorter token lifetime for testing)
SIMPLE_JWT.update({
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(hours=1),
})

# Web3 settings for development
WEB3_PROVIDER_URL = 'http://localhost:8545'  # Local Ganache
WEB3_NETWORK_ID = 1337  # Ganache default

# Disable some security features for development
AXES_ENABLED = False
RATELIMIT_ENABLE = False
