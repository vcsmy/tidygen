"""
Test settings for TidyGen ERP.
"""
from .base import *

# Use SQLite for testing
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Disable migrations for faster tests
class DisableMigrations:
    def __contains__(self, item):
        return True
    
    def __getitem__(self, item):
        return None

MIGRATION_MODULES = DisableMigrations()

# Use locmem cache for testing
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# Disable password hashing for faster tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Disable logging during tests
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'null': {
            'class': 'logging.NullHandler',
        },
    },
    'root': {
        'handlers': ['null'],
    },
}

# Disable security features for testing
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Disable rate limiting for tests
RATELIMIT_ENABLE = False

# Disable axes for tests
AXES_ENABLED = False

# Remove problematic apps for tests
INSTALLED_APPS = [app for app in INSTALLED_APPS if app not in ['ratelimit', 'axes', 'drf_spectacular']]

# Remove problematic middleware for tests
MIDDLEWARE = [m for m in MIDDLEWARE if m not in [
    'ratelimit.middleware.RatelimitMiddleware',
    'axes.middleware.AxesMiddleware'
]]

# Test-specific settings
TEST_RUNNER = 'django.test.runner.DiscoverRunner'
