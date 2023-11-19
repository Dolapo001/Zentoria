"""
Django settings for Zentoria project.

Generated by 'django-admin startproject' using Django 4.2.6.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from datetime import timedelta
from pathlib import Path
import os
from dotenv import load_dotenv

from rest_framework import authtoken

from .jazzmin import JAZZMIN_SETTINGS

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-)z@f0k(bz25!5470=u0b+%gji!ya^_1+o#4_^*8j)mdywu2u6i'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    #thirdparty
    'rest_framework',
    'drf_spectacular',
    'allauth',
    'allauth.account',
    'corsheaders',
    'rest_framework.authtoken',
    'rest_framework_simplejwt',

    #local_apps
    'Products.apps.ProductsConfig',
    'accounts.apps.AccountsConfig',
]


REST_FRAMEWORK = {
    "COERCE_DECIMAL_TO_STRING": False,
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.AllowAny",),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",

    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "social_core.backends.google.GoogleOAuth2",
    ],
}


SIMPLE_JWT = {
    "AUTH_HEADER_TYPES": ("Bearer",),
    "ACCESS_TOKEN_LIFETIME": timedelta(days=30),
}

SPECTACULAR_SETTINGS = {
    "TITLE": "ZENTORIA API",
    "DESCRIPTION": """""",
    "VERSION": "1.0.0",
    "SCHEMA_PATH_PREFIX": r'/api/v[0-9]',
    "SERVE_INCLUDE_SCHEMA": False,
    "DISABLE_ERRORS_AND_WARNINGS": True,
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'social_django.middleware.SocialAuthExceptionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

CORS_ORIGIN_WHITELIST = (
    "http://localhost:8000",
    "http://localhost:3000",
)

CSRF_TRUSTED_ORIGINS = ["http://localhost:3000"]

AUTH_USER_MODEL = "accounts.User"

ROOT_URLCONF = 'Zentoria.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates']
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.request',
            ],
        },
    },
]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

SITE_ID = 1

WSGI_APPLICATION = 'Zentoria.wsgi.application'

AUTHENTICATION_BACKENDS = (
    'allauth.account.auth_backends.AuthenticationBackend',
    'social_core.backends.google.GoogleOAuth2',
    'django.contrib.auth.backends.ModelBackend',
)


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


JAZZMIN_SETTINGS = JAZZMIN_SETTINGS


load_dotenv()
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.getenv('SOCIAL_AUTH_GOOGLE_OAUTH2_KEY')
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.getenv('SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET')


ACCOUNT_EMAIL_VERIFICATION = 'mandatory'


ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 7


ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_USERNAME_REQUIRED = False


ACCOUNT_EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL = '/login/'
ACCOUNT_EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL = '/profile/'
