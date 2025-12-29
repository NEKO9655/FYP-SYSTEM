# --- File: backend/backend/settings.py (FINAL EXPLICIT & SECURE VERSION) ---

from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = '...' # Your secret key
DEBUG = True
ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'api',
    'rest_framework',
    'corsheaders',
    'django_filters',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware', # Must be high up
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'backend.urls'

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

WSGI_APPLICATION = 'backend.wsgi.application'

DATABASES = { 'default': { 'ENGINE': 'django.db.backends.sqlite3', 'NAME': BASE_DIR / 'db.sqlite3' } }

AUTH_PASSWORD_VALIDATORS = []
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kuala_Lumpur'
USE_I1N = True
USE_TZ = True
STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTHENTICATION_BACKENDS = ['django.contrib.auth.backends.ModelBackend']

REST_FRAMEWORK = {
    # 'DEFAULT_AUTHENTICATION_CLASSES': [ ... ], # Temporarily comment this out
    'DEFAULT_PERMISSION_CLASSES': [
        # --- Temporarily allow anyone to access the API for development ---
        'rest_framework.permissions.AllowAny',
    ],
}

# --- 【THE FINAL FIX IS HERE】 ---
# We are making the CORS and CSRF settings extremely explicit for development.

# 1. CORS Configuration
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# 2. CSRF Trusted Origins Configuration
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# 3. Explicitly set the SameSite attribute and HttpOnly for cookies.
# This is often the key to making cross-origin cookies work in modern browsers.
CSRF_COOKIE_HTTPONLY = False  # Allows frontend JS to read the CSRF token
CSRF_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_SAMESITE = 'Lax'

SESSION_COOKIE_SECURE = False # Must be False for http (localhost)
CSRF_COOKIE_SECURE = False   # Must be False for http (localhost)
# --- 【END OF FIX】 ---

# Email Configuration
# ... (your email settings)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com' # 记得替换
EMAIL_HOST_PASSWORD = 'your-app-password' # 记得替换