import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-your-secret-key-here'

DEBUG = True

ALLOWED_HOSTS = ['*']


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

    # Third-party apps
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    

    # Local apps
    'his_grace_drugshop.users',
    'his_grace_drugshop.medicines',
    'his_grace_drugshop.sales',
    'his_grace_drugshop.reports',
    'his_grace_drugshop.credit',
    'his_grace_drugshop.expenses',
    'his_grace_drugshop.prescriptions',
    'his_grace_drugshop.stock',
]
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]


# =========================
# MIDDLEWARE
# =========================
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',

    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',

    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# =========================
# ROOT URLS
# =========================
ROOT_URLCONF = 'pharmacy_backend.urls'


# =========================
# TEMPLATES
# =========================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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


# =========================
# WSGI
# =========================
WSGI_APPLICATION = 'pharmacy_backend.wsgi.application'


# =========================
# DATABASE
# =========================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# =========================
# PASSWORD VALIDATORS
# =========================
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


# =========================
# INTERNATIONALIZATION
# =========================
LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# =========================
# STATIC FILES
# =========================
STATIC_URL = 'static/'

STATIC_ROOT = os.path.join(BASE_DIR, 'static')


# =========================
# DEFAULT PRIMARY KEY
# =========================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# =========================
# CUSTOM USER MODEL
# =========================
AUTH_USER_MODEL = 'users.User'


# =========================
# CORS SETTINGS
# =========================
CORS_ALLOW_ALL_ORIGINS = True

CORS_ALLOW_CREDENTIALS = True


# =========================
# CSRF TRUSTED ORIGINS
# =========================
CSRF_TRUSTED_ORIGINS = []

# Allow all localhost ports (Flutter/React dev)
for port in range(3000, 60000):
    CSRF_TRUSTED_ORIGINS.append(f"http://localhost:{port}")
    CSRF_TRUSTED_ORIGINS.append(f"http://127.0.0.1:{port}")


# =========================
# CORS METHODS
# =========================
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]


# =========================
# CORS HEADERS
# =========================
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


# =========================
# CSRF SETTINGS
# =========================
CSRF_COOKIE_SECURE = False

CSRF_COOKIE_HTTPONLY = False

CSRF_COOKIE_SAMESITE = 'Lax'


# =========================
# REST FRAMEWORK
# =========================
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],

    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],

    'UNAUTHENTICATED_USER': None,
}


# =========================
# EMAIL SETTINGS
# =========================
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

EMAIL_HOST_USER = 'gloriousainembabazi16@gmail.com'
EMAIL_HOST_PASSWORD = 'nanr dgbp zfql wkdm' 

DEFAULT_FROM_EMAIL = 'His Grace Drugshop <gloriousainembabazi16@gmail.com>'

# =========================
# FRONTEND SETTINGS (For Email Verification)
# =========================
# Use a flexible approach that accepts any localhost port
# The actual port will be captured from the request
FRONTEND_BASE_URL = 'http://localhost'  # Base URL without port

# Email verification token expiry (24 hours)
EMAIL_VERIFICATION_TOKEN_EXPIRY = 86400  # 24 hours in seconds

# For development, you can also use console backend by changing the above EMAIL_BACKEND to:
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'