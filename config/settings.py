"""
Django settings for LogMyOJT project.

Production-hardened configuration supporting environment variables,
Supabase PostgreSQL with SQLite fallback, WhiteNoise static file serving,
Content Security Policy, and login rate limiting.
"""

import sys
from pathlib import Path
import os
from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env if present
load_dotenv(BASE_DIR / '.env')

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/6.1/howto/deployment/checklist/

RUNNING_TESTS = any('test' in arg for arg in sys.argv)
IS_RUNSERVER = any('runserver' in arg for arg in sys.argv)
IS_DEPLOY_CHECK = any('--deploy' in arg for arg in sys.argv)

# DEBUG mode: explicit env var if provided.
# Defaults to False during deployment check (--deploy) or production;
# defaults to True for local development commands so the app runs with zero extra setup.
raw_debug = os.environ.get('DJANGO_DEBUG')
if raw_debug is not None:
    # Strip whitespace, quotes, comments, or stray tildes (e.g. True~)
    clean_debug = raw_debug.strip().strip("'\"").rstrip('~# ;\r\n\t').lower()
    DEBUG = clean_debug in ('true', '1', 'yes') or clean_debug.startswith('true')
else:
    DEBUG = not IS_DEPLOY_CHECK

# SECRET_KEY handling: require env var when DEBUG is False
DJANGO_SECRET_KEY = (os.environ.get('DJANGO_SECRET_KEY') or os.environ.get('SECRET_KEY', '')).strip()
if DJANGO_SECRET_KEY:
    SECRET_KEY = DJANGO_SECRET_KEY
elif DEBUG or RUNNING_TESTS or IS_RUNSERVER:
    SECRET_KEY = 'django-insecure-dev-only-fallback-change-in-production-logmyojt'
else:
    raise ImproperlyConfigured(
        "DJANGO_SECRET_KEY environment variable is required when DEBUG is False."
    )

# Host validation
raw_allowed_hosts = os.environ.get('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1')
ALLOWED_HOSTS = [h.strip() for h in raw_allowed_hosts.split(',') if h.strip()]

# CSRF Trusted Origins
raw_csrf_origins = os.environ.get('DJANGO_CSRF_TRUSTED_ORIGINS', '')
CSRF_TRUSTED_ORIGINS = [o.strip() for o in raw_csrf_origins.split(',') if o.strip()]
if DEBUG or IS_RUNSERVER:
    for dev_origin in ['http://localhost:8000', 'http://127.0.0.1:8000', 'http://localhost:8080', 'http://127.0.0.1:8080']:
        if dev_origin not in CSRF_TRUSTED_ORIGINS:
            CSRF_TRUSTED_ORIGINS.append(dev_origin)


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic',
    'django.contrib.staticfiles',
    # Security & Rate Limiting
    'axes',
    # Feature apps (vertical slices)
    'apps.login',
    'apps.register',
    'apps.home',
    'apps.user_profile',
    'apps.user_settings',
    'apps.placement',
    'apps.time_log',
    'apps.reminders',
    'apps.reports',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'axes.middleware.AxesMiddleware',
    'config.middleware.ContentSecurityPolicyMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.user_settings.context_processors.dark_mode',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# Reads the Supabase PostgreSQL connection string from DATABASE_URL in .env.
# Automatically falls back to local SQLite if DATABASE_URL is unset or invalid.

import urllib.parse

DATABASE_URL = os.environ.get('DATABASE_URL', '').strip()
sqlite_default_url = f"sqlite:///{ (BASE_DIR / 'db.sqlite3').as_posix() }"

database_config = None
if DATABASE_URL:
    try:
        database_config = dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=600,
            ssl_require=DATABASE_URL.startswith('postgres'),
        )
    except Exception:
        # Gracefully handle unquoted passwords or template brackets [password]
        try:
            if '://' in DATABASE_URL and '@' in DATABASE_URL:
                prefix, rest = DATABASE_URL.split('://', 1)
                userinfo, hostinfo = rest.rsplit('@', 1)
                if ':' in userinfo:
                    user_part, pass_part = userinfo.split(':', 1)
                    clean_pass = urllib.parse.quote(pass_part.strip('[]'), safe='')
                    reconstructed_url = f"{prefix}://{user_part}:{clean_pass}@{hostinfo}"
                    database_config = dj_database_url.parse(
                        reconstructed_url,
                        conn_max_age=600,
                        ssl_require=reconstructed_url.startswith('postgres'),
                    )
        except Exception:
            database_config = None

if not database_config:
    database_config = dj_database_url.parse(
        sqlite_default_url,
        conn_max_age=600,
    )

DATABASES = {
    'default': database_config,
}

# When running automated tests, use local SQLite so tests execute fast and don't
# require CREATE/DROP DATABASE privileges on Supabase's connection pooler.
if RUNNING_TESTS:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': str(BASE_DIR / 'test_db.sqlite3'),
        }
    }


# Authentication Backends (with django-axes rate limiting)

AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesStandaloneBackend',
    'django.contrib.auth.backends.ModelBackend',
]

# Axes Configuration: 5 failed attempts per username+IP, 15 minute lockout
AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = 0.25  # hours (15 minutes)
AXES_LOCKOUT_CALLABLE = 'apps.login.views.lockout_view'
AXES_RESET_ON_SUCCESS = True
AXES_LOCKOUT_PARAMETERS = [['username', 'ip_address']]


# Password validation
# https://docs.djangoproject.com/en/6.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
        'OPTIONS': {
            'max_similarity': 0.85,
        },
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        },
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# Philippines standard timezone for OJT logging

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Manila'
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# WhiteNoise handles static assets in production without an external CDN

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
os.makedirs(STATIC_ROOT, exist_ok=True)
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

WHITENOISE_MANIFEST_STRICT = False

STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedStaticFilesStorage'
        if not DEBUG and not RUNNING_TESTS
        else 'django.contrib.staticfiles.storage.StaticFilesStorage',
    },
}

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# Auth redirects
LOGIN_URL = 'login:login'
LOGIN_REDIRECT_URL = 'home:home'
LOGOUT_REDIRECT_URL = 'login:login'


# Email Configuration
EMAIL_BACKEND = os.environ.get(
    'EMAIL_BACKEND',
    'django.core.mail.backends.console.EmailBackend' if DEBUG else 'django.core.mail.backends.smtp.EmailBackend',
)
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'localhost')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True').lower() in ('true', '1', 'yes')
EMAIL_USE_SSL = os.environ.get('EMAIL_USE_SSL', 'False').lower() in ('true', '1', 'yes')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'LogMyOJT <noreply@logmyojt.local>')


# Production Security Headers
if not DEBUG and not RUNNING_TESTS and not IS_RUNSERVER:
    SECURE_SSL_REDIRECT = os.environ.get('DJANGO_SECURE_SSL_REDIRECT', 'True').lower() in ('true', '1', 'yes')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = int(os.environ.get('DJANGO_SECURE_HSTS_SECONDS', '3600'))
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = os.environ.get('DJANGO_SECURE_HSTS_PRELOAD', 'True').lower() in ('true', '1', 'yes')
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    X_FRAME_OPTIONS = 'DENY'
    SECURE_REFERRER_POLICY = 'same-origin'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    CSRF_COOKIE_HTTPONLY = True
    CSRF_COOKIE_SAMESITE = 'Lax'
else:
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    SECURE_HSTS_SECONDS = 0
