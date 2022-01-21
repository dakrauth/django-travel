import os
import sys
from django import VERSION

ALLOWED_HOSTS = []
AUTH_PASSWORD_VALIDATORS = []
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEBUG = not any('pytest' in arg for arg in sys.argv)
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
LANGUAGE_CODE = 'en-us'
ROOT_URLCONF = 'demo_proj.urls'
SECRET_KEY = '!%^#zpaq92v$s#fb^8$i(u+_(ba$^t2$3u*uwhv*tgf1z19zzj'
SITE_ID = 1
STATIC_URL = '/static/'
TIME_ZONE = 'UTC'
USE_I18N = True
if VERSION < (4,):
    USE_L10N = True
USE_TZ = True
WSGI_APPLICATION = 'demo_proj.wsgi.application'

DATABASES = {'default': {
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
}}

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django.contrib.sites',
    'bootstrap5',
    'travel',
    'demo_proj',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [os.path.join(BASE_DIR, 'templates')],
    'APP_DIRS': True,
    'OPTIONS': {
        'context_processors': [
            'django.template.context_processors.debug',
            'django.template.context_processors.request',
            'django.contrib.auth.context_processors.auth',
            'django.contrib.messages.context_processors.messages',
            'travel.context_processors.search',
        ],
    },
}]
