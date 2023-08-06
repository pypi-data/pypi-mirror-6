"""
Django settings for DPL1 project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'z**2kk-)t8s%w6q+^&ojrmetqlrvirisg5#p@7o6ee_ptxzf&4'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    # #sessions are stored in cookies. this setting implies
    # DB storage of sessions - but we don't need it, since we keep it only
    # in memory - or we DO need it
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'dpl1_main.testing_app',
    'south'
)

MIDDLEWARE_CLASSES = (
    #Could use my custom class here - and SHOULD if i want to create custom
    #..sessions
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'dpl1_main.DPL1.urls'

WSGI_APPLICATION = 'dpl1_main.DPL1.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': os.path.join(BASE_DIR, 'vwhdb.sqlite3'),
#     }
# }
DATABASES = {
    # 'default': {
    #     'ENGINE': 'django.db.backends.mysql',
    #     'NAME': 'vwh_db',
    #     'PORT': '3306',
    #     'USER': 'root',
    #     'PASSWORD': 'qwer',
    #     'HOST': 'localhost'
    # }
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'default.sqlite3',
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Vlad was here: custom settings introduced by me
## Pycharm `reference not resolved` is OK - works actually, because  this
## is relative to the BASE_DIR
TEMPLATE_DIRS = (os.path.join(BASE_DIR, 'testing_app/templates'),)

#Should reorder the domain objects on the admin site... the order needs to
# be this:
# ADMIN_REORDER = ( ('testing_app', ('Test', 'Page', 'Question')))
#Should use this module to store my session classes, to instantiate inside the
#..custom middleware class
##Cache only session cookies
SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'
# SESSION_ENGINE = ''

#This prevents changing the cookie data via Javascript
SESSION_COOKIE_HTTPONLY = True
# SESSION_ENGINE = 'testing_app.session_util'
SESSION_SAVE_EVERY_REQUEST = True