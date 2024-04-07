"""
Django settings for nbl project on Heroku. For more info, see:
https://github.com/heroku/heroku-django-template

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""

import os
import dj_database_url
import django_heroku
from django.urls import reverse_lazy

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
print(PROJECT_ROOT)
TEMPLATE_PATH = os.path.join(BASE_DIR, 'templates')

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "9c*$u!gw0e1z_e1v5flu+ayumb6$lr^qs102y9x*j3hvo3*%=2"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True# False

# Application definition

INSTALLED_APPS = [
    'users',
    'generic',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.humanize',
    # Disable Django's own staticfiles handling in favour of WhiteNoise, for
    # greater consistency between gunicorn and `./manage.py runserver`. See:
    # http://whitenoise.evans.io/en/stable/django.html#using-whitenoise-in-development
    'whitenoise.runserver_nostatic',
    'django.contrib.staticfiles',
    'core.apps.CoreConfig',

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
]

ROOT_URLCONF = 'nbl.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'debug': DEBUG,
        },
    },
]

WSGI_APPLICATION = 'nbl.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases
""" 
    'default':{
        'ENGINE':'django.db.backends.mysql',
        'HOST': 'ukraine2020.mysql.pythonanywhere-services.com',
        'USER': 'ukraine2020',
        'PASSWORD': 'success12',
        'NAME': 'ukraine2020$nbl_db'
    } 
"""
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'nblbkup',# 'nbl',
        'HOST':'localhost',
        'USER':'crypto2',
        'PASSWORD':'wala2121',
        'PORT':''
    },
}
"""
    'default2': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'nbl',
        'HOST':'localhost',
        'USER':'crypto2',
        'PASSWORD':'wala2121',
        'PORT':''
    }
    
"""

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
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Change 'default' database configuration with $DATABASE_URL.
DATABASES['default'].update(dj_database_url.config(conn_max_age=500, ssl_require=True))

# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Allow all host headers
ALLOWED_HOSTS = ['*']

PREPEND_WWW = True
BASE_URL = "https://www.nblfinancial.com"
SECURE_SSL_REDIRECT = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

STATIC_ROOT = os.path.join(PROJECT_ROOT, 'static') #files
STATIC_URL = '/static/'

# Extra places for collectstatic to find static files.

STATICFILES_DIRS = [
    os.path.join(PROJECT_ROOT, 'static'), #
]

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Simplified static file serving.
# https://warehouse.python.org/project/whitenoise/
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Activate Django-Heroku.
django_heroku.settings(locals())

LOGIN_URL = reverse_lazy('users:login')
LOGOUT_URL = reverse_lazy('users:logout')
LOGIN_REDIRECT_URL = reverse_lazy('core:transactions')
LOGOUT_REDIRECT_URL = reverse_lazy('core:homepage')
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'#'django.core.mail.backends.console.EmailBackend'


EMAIL_HOST = 'smtp.zoho.com' #'mail.nblfinancial.com'
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER = 'info@nblfinancial.com'
EMAIL_HOST_PASSWORD = '?Process007' 

DEFAULT_FROM_EMAIL = 'info@nblfinancial.com'
EMAIL_BACKEND='django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.zoho.com'

ACCOUNT_SESSION_REMEMBER = False
PREPEND_WWW = True
BASE_URL = "https://wwww.nblfinancial.com"
SECURE_SSL_REDIRECT = True
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'


PREPEND_WWW = True
BASE_URL = "https://www.nblfinancial.com"
SECURE_SSL_REDIRECT = True
