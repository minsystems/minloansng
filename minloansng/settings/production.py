"""
Django settings for minloansng project.

Generated by 'django-admin startproject' using Django 3.0.2.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '(=vw2)fyh)4uit)gty2z7g-icg$3a^zc3w-eb)v+)@tncxd%))'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

BASE_URL = 'https://www.minloans.com.ng'

MANAGERS = (
    ('Minloans NG', "minloansnigeria@gmail.com"),
    ('Minloans NG', "customer@minloans.com.ng")
)

ADMINS = MANAGERS

AUTH_USER_MODEL = 'accounts.User'

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django_jenkins',

    # third party apps
    'phonenumber_field',
    'crispy_forms',
    'rest_framework',
    'corsheaders',
    'debug_toolbar',
    'widget_tweaks',

    # apps
    'accounts',
    'banks',
    'borrowers',
    'comments',
    'company',
    'loans',
    'mincore',
    'minmarkets',
]

FORCE_SESSION_TO_ONE = False
FORCE_INACTIVE_USER_ENDSESSION = False

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'minloansng.urls'
from corsheaders.defaults import default_headers

CORS_ALLOW_HEADERS = default_headers + (
    'Access-Control-Allow-Origin',
)

INTERNAL_IPS = [
    '127.0.0.1',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')]
        ,
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

WSGI_APPLICATION = 'minloansng.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'd7epjljjk3gfm0',
        'USER': 'sjefusmocigoqw',
        'PASSWORD': '43845d756c8c04404dc20e947aacd783852725ba7271dd5b641d6d8106dc2f82',
        'HOST': 'ec2-23-22-156-110.compute-1.amazonaws.com',
        'PORT': '5432'
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

from minloansng.cloudinary_settings import *

STATIC_URL = '/static/'
LOGIN_REDIRECT_URL = '/account/<username>/'
LOGOUT_REDIRECT_URL = '/'

STATIC_ROOT = os.path.join(BASE_DIR, 'static_root')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, "static", "media_root")

PROTECTED_ROOT = os.path.join(BASE_DIR, "static", "protected_media")

# from minloansng.ssl_config import *
