import os
from pathlib import Path
import dj_database_url
from dotenv import load_dotenv

# =========================
# LOAD ENVIRONMENT VARIABLES
# =========================
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# =========================
# SECURITY
# =========================
SECRET_KEY = os.getenv("SECRET_KEY", "django-insecure-your-secret-key-here")

DEBUG = os.getenv("DEBUG", "False") == "True"

ALLOWED_HOSTS = os.getenv(
    "ALLOWED_HOSTS",
    "127.0.0.1,localhost,drugshop-backend-1.onrender.com"
).split(",")

# =========================
# INSTALLED APPS
# =========================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',

    'his_grace_drugshop.users',
    'his_grace_drugshop.medicines',
    'his_grace_drugshop.sales',
    'his_grace_drugshop.reports',
    'his_grace_drugshop.credit',
    'his_grace_drugshop.expenses',
    'his_grace_drugshop.prescriptions',
    'his_grace_drugshop.stock',
]

# =========================
# MIDDLEWARE (CORS MUST BE FIRST)
# =========================
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
]

ROOT_URLCONF = 'pharmacy_backend.urls'

# =========================
# DATABASE
# =========================
DATABASES = {
    "default": dj_database_url.config(
        default=os.getenv("DATABASE_URL"),
        conn_max_age=600,
        ssl_require=not DEBUG
    )
}

# =========================
# CORS SETTINGS
# =========================

# Enable during development (Flutter Web)
CORS_ALLOW_ALL_ORIGINS = True

# For production, set this to False and uncomment CORS_ALLOWED_ORIGINS below.
# CORS_ALLOW_ALL_ORIGINS = False
#
# CORS_ALLOWED_ORIGINS = [
#     "https://drugshop-backend-1.onrender.com",
# ]

CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_METHODS = [
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
]

CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
]

# =========================
# CSRF SETTINGS
# =========================
CSRF_TRUSTED_ORIGINS = [
    "https://drugshop-backend-1.onrender.com",
    "http://localhost",
    "http://127.0.0.1",
]

CSRF_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_SAMESITE = "Lax"

# =========================
# REST FRAMEWORK & OTHER SETTINGS
# =========================
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
}

AUTH_USER_MODEL = 'users.User'

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

STATIC_URL = '/static/'

STATIC_ROOT = BASE_DIR / 'staticfiles'

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'