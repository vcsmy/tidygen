"""
Settings package for TidyGen ERP.
Dynamically loads environment-specific settings.
"""

import os
from .base import *

# Get the environment from environment variable
DJANGO_ENV = os.environ.get('DJANGO_ENV', 'development')

if DJANGO_ENV == 'production':
    from .production import *
elif DJANGO_ENV == 'staging':
    from .staging import *
else:
    from .development import *
