"""
Django Project Settings for NLP-to-SQL POC
Minimal configuration for running the chatbot backend.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent.parent / '.env')

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'dev-secret-key-change-in-prod')
DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
ALLOWED_HOSTS = ['*']

# Application definition
INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'corsheaders',
    'chatbot',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
]

# CORS Configuration - Allow React frontend
CORS_ALLOW_ALL_ORIGINS = True  # For POC only - restrict in production
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

ROOT_URLCONF = 'config.urls'

# Database (using environment variables)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
        'NAME': os.getenv('DB_NAME', 'davinci'),
        'USER': os.getenv('DB_USER', 'davinci'),
        'PASSWORD': os.getenv('DB_PASSWORD', ''),
    }
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Logging
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
}
