import os
from datetime import datetime
from pathlib import Path

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent

# Security settings
SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "django-insecure-8ew7hf41c8b__6r(p1*md@a-m=2%sq^)^an=awx7zr9saf4%)h",
)
DEBUG = os.environ.get("DJANGO_DEBUG", "True") == "True"
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

# Application definition
INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "rest_framework",
    "transformer",
    "corsheaders",
]

# DRF settings (no need for authentication due to the PoC nature of the project)
REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [],
    "UNAUTHENTICATED_USER": None,
    "EXCEPTION_HANDLER": "transformer.base.exception_handler.custom_exception_handler",
}

# Middleware configuration
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "transformer.base.middleware.RequestLoggingMiddleware",
]

# Template configuration
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
            ],
        },
    },
]

# CORS settings
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
]

# URL configuration
ROOT_URLCONF = "transformer.urls"
WSGI_APPLICATION = "transformer.wsgi.application"

# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": os.environ.get("DATABASE_NAME", "postgres"),
        "HOST": os.environ.get("DATABASE_HOST", "localhost"),
        "USER": os.environ.get("DATABASE_USER", "postgres"),
        "PORT": "5432",
        "CONN_MAX_AGE": 60,
        "OPTIONS": {
            "connect_timeout": 5,
        },
    }
}

# Timezone settings
USE_TZ = True
TIME_ZONE = "UTC"

# Redis settings
REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = os.environ.get("REDIS_PORT", "6379")

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"redis://{REDIS_HOST}:{REDIS_PORT}/2",  # DB 2 for caching
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "PARSER_CLASS": "redis.connection.HiredisParser",
            "CONNECTION_POOL_CLASS": "redis.BlockingConnectionPool",
            "CONNECTION_POOL_CLASS_KWARGS": {
                "max_connections": 50,
                "timeout": 20,
            },
        },
    },
}

# Celery settings
BROKER_URL = os.environ.get("BROKER_URL", "redis://localhost:6379")
CELERY_BROKER_URL = f"{BROKER_URL}/0"
CELERY_RESULT_BACKEND = f"{BROKER_URL}/1"
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True

# File upload and storage settings
FILE_STORAGE_BASE_DIR = Path.home() / ".transformer" / "uploads"
FILE_STORAGE_BASE_DIR.mkdir(parents=True, exist_ok=True)
DEFAULT_FILE_STORAGE = "transformer.base.storage.CSVFileStorage"

MEDIA_ROOT = FILE_STORAGE_BASE_DIR
MEDIA_URL = "/media/"
FILE_UPLOAD_MAX_MEMORY_SIZE = 104857600  # 100 MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 104857600  # 100 MB

# Logging configuration
LOGS_DIR = os.path.join(BASE_DIR, 'logs')
os.makedirs(LOGS_DIR, exist_ok=True)

# Logging configuration
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        "file": {
            "level": "DEBUG",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(LOGS_DIR, f"transformer-{datetime.now().strftime('%Y-%m-%d')}.log"),
            "maxBytes": 1024 * 1024 * 5,  # 5 MB
            "backupCount": 5,
            "formatter": "verbose",
        },
        "error_file": {
            "level": "ERROR",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(LOGS_DIR, f"transformer-errors-{datetime.now().strftime('%Y-%m-%d')}.log"),
            "maxBytes": 1024 * 1024 * 5,  # 5 MB
            "backupCount": 5,
            "formatter": "verbose",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": True,
        },
        "transformer": {
            "handlers": ["console", "file", "error_file"],
            "level": "DEBUG",
            "propagate": True,
        },
    },
}
