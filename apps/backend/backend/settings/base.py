"""
Base settings for TidyGen ERP project.
"""

import os
from pathlib import Path
from datetime import timedelta
from decouple import config
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-me-in-production')

# Application definition
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework_simplejwt',
    # 'rest_framework_simplejwt.token_blacklist',  # Disabled due to custom user model
    'corsheaders',
    'django_filters',
    'drf_spectacular',
    'django_extensions',
    'model_utils',
    'import_export',
    'crispy_forms',
    'crispy_bootstrap5',
    'django_bootstrap5',
    'widget_tweaks',
    'django_tables2',
    'colorfield',
    'django_json_widget',
    'jazzmin',
    'axes',
    # 'django_ratelimit',  # Disabled for development
    'ipware',
]

LOCAL_APPS = [
    'apps.core',
    'apps.accounts',
    'apps.web3',
    'apps.ledger',
    'apps.wallet',
    'apps.audit_trail',
    'apps.did_auth', # Added DID authentication
    'apps.inventory',
    'apps.sales',
    'apps.purchasing',
    'apps.finance',
    'apps.hr',
    'apps.payroll',
    'apps.scheduling',
    'apps.analytics',
    'apps.facility_management',
    'apps.field_operations',
    'apps.freelancers', # Community edition: Individual contractor management
    'apps.gig_management', # Community edition: Job posting and assignment
    'apps.contractor_payments', # Community edition: Payment processing for freelancers
    'apps.freelancer_web3', # Community edition: Advanced Web3 features for freelancers
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'axes.middleware.AxesMiddleware',
        # 'django_ratelimit.middleware.RatelimitMiddleware',  # Disabled for development
]

ROOT_URLCONF = 'backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'backend.wsgi.application'

# Database
DATABASES = {
    'default': dj_database_url.parse(
        config('DATABASE_URL', default='sqlite:///db.sqlite3')
    )
}

# Custom User Model
AUTH_USER_MODEL = 'core.User'

# Cache Configuration
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': config('REDIS_URL', default='redis://localhost:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Session Configuration
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
SESSION_COOKIE_AGE = 86400  # 24 hours
SESSION_COOKIE_SECURE = False  # Will be overridden in production
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Django REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.MultiPartParser',
        'rest_framework.parsers.FormParser',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'EXCEPTION_HANDLER': 'apps.core.exceptions.custom_exception_handler',
}

# JWT Configuration
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    'JWK_URL': None,
    'LEEWAY': 0,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'TOKEN_USER_CLASS': 'rest_framework_simplejwt.models.TokenUser',
    'JTI_CLAIM': 'jti',
    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
}

# CORS Configuration
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
]

CORS_ALLOW_CREDENTIALS = True

# Security Settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# CSRF Settings
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# Web3 Configuration
WEB3_CONTRACTS = {
    'TidyGenERP': {
        'address': config('TIDYGEN_ERP_CONTRACT_ADDRESS', default=''),
        'abi': [],  # Will be loaded from contract artifacts
    },
    'TidyGenToken': {
        'address': config('TIDYGEN_TOKEN_CONTRACT_ADDRESS', default=''),
        'abi': [],  # Will be loaded from contract artifacts
    },
    'TidyGenDAO': {
        'address': config('TIDYGEN_DAO_CONTRACT_ADDRESS', default=''),
        'abi': [],  # Will be loaded from contract artifacts
    },
    'ERC20': {
        'abi': [
            {
                "constant": True,
                "inputs": [{"name": "_owner", "type": "address"}],
                "name": "balanceOf",
                "outputs": [{"name": "balance", "type": "uint256"}],
                "type": "function"
            },
            {
                "constant": True,
                "inputs": [],
                "name": "decimals",
                "outputs": [{"name": "", "type": "uint8"}],
                "type": "function"
            },
            {
                "constant": True,
                "inputs": [],
                "name": "symbol",
                "outputs": [{"name": "", "type": "string"}],
                "type": "function"
            },
            {
                "constant": True,
                "inputs": [],
                "name": "name",
                "outputs": [{"name": "", "type": "string"}],
                "type": "function"
            },
            {
                "constant": False,
                "inputs": [
                    {"name": "_to", "type": "address"},
                    {"name": "_value", "type": "uint256"}
                ],
                "name": "transfer",
                "outputs": [{"name": "", "type": "bool"}],
                "type": "function"
            },
            {
                "constant": False,
                "inputs": [
                    {"name": "_spender", "type": "address"},
                    {"name": "_value", "type": "uint256"}
                ],
                "name": "approve",
                "outputs": [{"name": "", "type": "bool"}],
                "type": "function"
            },
            {
                "constant": True,
                "inputs": [
                    {"name": "_owner", "type": "address"},
                    {"name": "_spender", "type": "address"}
                ],
                "name": "allowance",
                "outputs": [{"name": "", "type": "uint256"}],
                "type": "function"
            },
            {
                "constant": False,
                "inputs": [
                    {"name": "_from", "type": "address"},
                    {"name": "_to", "type": "address"},
                    {"name": "_value", "type": "uint256"}
                ],
                "name": "transferFrom",
                "outputs": [{"name": "", "type": "bool"}],
                "type": "function"
            }
        ]
    }
}

# Web3 Network Configuration
WEB3_NETWORKS = {
    'ethereum': {
        'rpc_url': config('ETHEREUM_RPC_URL', default='https://mainnet.infura.io/v3/YOUR_INFURA_KEY'),
        'chain_id': 1,
        'name': 'Ethereum Mainnet'
    },
    'sepolia': {
        'rpc_url': config('SEPOLIA_RPC_URL', default='https://sepolia.infura.io/v3/YOUR_INFURA_KEY'),
        'chain_id': 11155111,
        'name': 'Ethereum Sepolia'
    },
    'polygon': {
        'rpc_url': config('POLYGON_RPC_URL', default='https://polygon-rpc.com'),
        'chain_id': 137,
        'name': 'Polygon'
    },
    'mumbai': {
        'rpc_url': config('MUMBAI_RPC_URL', default='https://rpc-mumbai.maticvigil.com'),
        'chain_id': 80001,
        'name': 'Polygon Mumbai'
    },
    'moonbeam': {
        'rpc_url': config('MOONBEAM_RPC_URL', default='https://rpc.api.moonbeam.network'),
        'chain_id': 1284,
        'name': 'Moonbeam'
    },
    'moonbase': {
        'rpc_url': config('MOONBASE_RPC_URL', default='https://rpc.api.moonbase.moonbeam.network'),
        'chain_id': 1287,
        'name': 'Moonbase Alpha'
    },
    'astar': {
        'rpc_url': config('ASTAR_RPC_URL', default='https://evm.astar.network'),
        'chain_id': 592,
        'name': 'Astar'
    },
    'shiden': {
        'rpc_url': config('SHIDEN_RPC_URL', default='https://evm.shiden.astar.network'),
        'chain_id': 336,
        'name': 'Shiden'
    }
}

# IPFS Configuration
IPFS_URL = config('IPFS_URL', default='http://localhost:5001')
IPFS_GATEWAY = config('IPFS_GATEWAY', default='https://ipfs.io/ipfs/')

# Web3 Message Configuration
WEB3_MESSAGE_PREFIX = config('WEB3_MESSAGE_PREFIX', default='TidyGen ERP Login')

# API Documentation
SPECTACULAR_SETTINGS = {
    'TITLE': 'TidyGen ERP API',
    'DESCRIPTION': 'Web3-enabled Enterprise Resource Planning API',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'SCHEMA_PATH_PREFIX': '/api/',
    'SERVERS': [
        {'url': 'http://localhost:8000', 'description': 'Development server'},
        {'url': 'https://api.tidygen.com', 'description': 'Production server'},
    ],
    'TAGS': [
        {'name': 'Authentication', 'description': 'User authentication and authorization'},
        {'name': 'Users', 'description': 'User management and profiles'},
        {'name': 'Web3', 'description': 'Blockchain and Web3 integration'},
        {'name': 'Inventory', 'description': 'Inventory management'},
        {'name': 'Sales', 'description': 'Sales and CRM'},
        {'name': 'Finance', 'description': 'Financial management'},
        {'name': 'HR', 'description': 'Human resources'},
        {'name': 'Analytics', 'description': 'Analytics and reporting'},
        {'name': 'Audit Trail', 'description': 'Audit trail and logging'},
        {'name': 'Contractor Payments', 'description': 'Contractor and freelancer payments'},
        {'name': 'Payroll', 'description': 'Payroll management'},
        {'name': 'Purchasing', 'description': 'Procurement and purchasing'},
        {'name': 'Scheduling', 'description': 'Resource and appointment scheduling'},
        {'name': 'Facility Management', 'description': 'Facility and asset management'},
        {'name': 'Field Operations', 'description': 'Field operations and dispatch'},
        {'name': 'Freelancers', 'description': 'Freelancer and contractor management'},
        {'name': 'Gig Management', 'description': 'Job posting and gig management'},
        {'name': 'Freelancer Web3', 'description': 'Web3 features for freelancers'},
        {'name': 'Ledger', 'description': 'Blockchain ledger management'},
        {'name': 'Wallet', 'description': 'Web3 wallet management'},
        {'name': 'DID Auth', 'description': 'Decentralized identity authentication'},
    ],
    'SWAGGER_UI_SETTINGS': {
        'deepLinking': True,
        'persistAuthorization': True,
        'displayOperationId': True,
    },
    'REDOC_UI_SETTINGS': {
        'hideDownloadButton': False,
        'expandResponses': '200,201',
    },
}

# Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
        'json': {
            'format': '{"level": "%(levelname)s", "time": "%(asctime)s", "module": "%(module)s", "message": "%(message)s"}',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'formatter': 'json',
        },
        # 'audit': {
        #     'class': 'logging.FileHandler',
        #     'filename': BASE_DIR / 'logs' / 'audit.log',
        #     'formatter': 'json',
        # },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'apps': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        # 'auditlog': {
        #     'handlers': ['audit'],
        #     'level': 'INFO',
        #     'propagate': False,
        # },
    },
}

# Celery Configuration
CELERY_BROKER_URL = config('CELERY_BROKER_URL', default='redis://localhost:6379/0')
CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND', default='redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

# Email Configuration
EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = config('EMAIL_HOST', default='localhost')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@tidygen.com')

# File Storage
DEFAULT_FILE_STORAGE = config('DEFAULT_FILE_STORAGE', default='django.core.files.storage.FileSystemStorage')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Rate Limiting
RATELIMIT_ENABLE = True
RATELIMIT_USE_CACHE = 'default'

# Django Axes (Brute Force Protection)
AXES_ENABLED = True
AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = 1  # 1 hour
# AXES_LOCKOUT_CALLABLE = 'axes.lockout.database_lockout'
AXES_LOCKOUT_PARAMETERS = ['ip_address', 'user_agent']
AXES_LOCKOUT_TEMPLATE = 'axes/lockout.html'
AXES_VERBOSE = True

# Add Axes backend to authentication backends
AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesStandaloneBackend',
    'django.contrib.auth.backends.ModelBackend',
]

# Audit Log Configuration (Custom implementation)
# AUDITLOG_INCLUDE_ALL_MODELS = True
# AUDITLOG_EXCLUDE_TRACKING_FIELDS = ['password', 'secret_key', 'token']

# Self-hosted Configuration (Community Edition)
# All users belong to the same organization context

# Web3 Configuration
WEB3_PROVIDER_URL = config('WEB3_PROVIDER_URL', default='https://goerli.infura.io/v3/YOUR_INFURA_KEY')
WEB3_PRIVATE_KEY = config('WEB3_PRIVATE_KEY', default='')
WEB3_NETWORK_ID = config('WEB3_NETWORK_ID', default=5, cast=int)  # Goerli testnet
