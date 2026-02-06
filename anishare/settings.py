"""
Django settings for anishare project.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/nan
"""

import os
import ldap
from django_auth_ldap.config import LDAPSearch

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# The following settings must be set in local_settings.py
AUTH_LDAP_BIND_DN = ''
AUTH_LDAP_BIND_PASSWORD = ''
EMAIL_HOST = ''
# SECURITY WARNING: keep the secret key used in production secret!
SYNC_WITH_OTHER_SYSTEMS = False
SECRET_KEY = ''
ALLOWED_HOSTS = [ ]
STATIC_URL = ''
DEBUG = False # SECURITY WARNING: don't run with debug turned on in production!
ADMIN_EMAIL = ''
LINES_PROHIBIT_SACRIFICE =[]
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/




# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_filters',  # https://github.com/carltongibson/django-filter
    'rangefilter',
    'animals',
    'widget_tweaks',
    'import_export',
    'admin_reorder',
   # 'admin_interface',  # https://github.com/fabiocaccamo/django-admin-interface
    'colorfield',
    'django_admin_listfilter_dropdown',
    'django_extensions', # for jobs scheduling
    'simple_history',
    'adminrestrict',
    'defender',
    'crispy_forms',
    'crispy_bootstrap4'
]

X_FRAME_OPTIONS='SAMEORIGIN'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'adminrestrict.middleware.AdminPagesRestrictMiddleware',
    #'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.common.CommonMiddleware',
    #'django.middleware.cache.FetchFromCacheMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'admin_reorder.middleware.ModelAdminReorder',
    'simple_history.middleware.HistoryRequestMiddleware',
    'defender.middleware.FailedLoginMiddleware',
    'django_currentuser.middleware.ThreadLocalUserMiddleware',
]

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

IMPORT_EXPORT_USE_TRANSACTIONS = True #  It determines if the library will use database transactions on data import, just to be on the safe side.

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

AUTH_LDAP_CONNECTION_OPTIONS = { ldap.OPT_REFERRALS: 0 }
AUTH_LDAP_SERVER_URI = ""
AUTH_LDAP_USER_SEARCH = LDAPSearch(
    "",
    ldap.SCOPE_SUBTREE,
    "(sAMAccountName=%(user)s)")
AUTH_LDAP_BIND_AS_AUTHENTICATING_USER = True
AUTH_LDAP_USER_ATTR_MAP = {
    "email": "mail",
    "first_name": "givenName",
    "last_name": "sn",
}
AUTH_LDAP_PROFILE_ATTR_MAP = {
}

ENVIRONMENT = "Production server"

import logging
logger = logging.getLogger('django_auth_ldap')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)


ROOT_URLCONF = 'anishare.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'animals/templates/')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django_settings_export.settings_export',
            ],
        },
    },
]


WSGI_APPLICATION = 'anishare.wsgi.application'




# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

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

TIME_ZONE = 'Europe/Berlin'

USE_I18N = False
USE_L10N = False

DATETIME_FORMAT = 'd.m.Y H:i:sO'
DATE_FORMAT = 'd.m.Y'
DATE_INPUT_FORMATS =\
[
    '%d.%m.%Y', '%d.%m.%Y',
    '%Y-%m-%d', '%m/%d/%Y', '%m/%d/%y', # '2006-10-25', '10/25/2006', '10/25/06'
    '%b %d %Y', '%b %d, %Y',            # 'Oct 25 2006', 'Oct 25, 2006'
    '%d %b %Y', '%d %b, %Y',            # '25 Oct 2006', '25 Oct, 2006'
    '%B %d %Y', '%B %d, %Y',            # 'October 25 2006', 'October 25, 2006'
    '%d %B %Y', '%d %B, %Y',            # '25 October 2006', '25 October, 2006'
]

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

ADMINRESTRICT_ENABLE_CACHE=True # https://github.com/robromano/django-adminrestrict
ADMINRESTRICT_BLOCK_GET=True

MIN_SHARE_DURATION = 14
MIN_SHARE_DURATION_PUPS = 6
MAX_AGE_PUPS = 22

#CACHES = {
#    'default': {
#        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
#        'LOCATION': 'my_cache_table',
#    }
#}

def FILTERS_VERBOSE_LOOKUPS():
    from django_filters.conf import DEFAULTS

    verbose_lookups = DEFAULTS['VERBOSE_LOOKUPS'].copy()
    verbose_lookups.update({
        'icontains': '',
    })
    return verbose_lookups

SHOW_ORGANS = False # if 1 there is a link to view offered Organs
TEST_ENVIRONMENT = False # if 1 there will be a hint for the users that it is a test environment
MOUSEDB = False  # Name of the mouse database AniShare uses to connect
FISHDB = False # True if there is a connection to a fish database / False if there isn't a connection
try:
    from .local_settings import *
#except ImportError:
except BaseException as e:
    print("Could not import local_settings!:{} ".format(e))
    pass

ADMIN_REORDER = (
    # Keep original label and models
    'sites',   
    {'app': 'animals', 'models': ('animals.Animal', 'animals.Organ','animals.Organtype', 'animals.Location', 'animals.Person', 'animals.Lab','animals.SacrificeIncidentToken')},
    # Rename app
    {'app': 'auth', 'label': 'Authentication and Authorization'},
    # Reorder app models
    {'app': 'animals', 'label': 'Change History', 'models': (
        {'model': 'animals.Change', 'label': 'Anishare change history'},
    )},
    'admin_interface',  
)

CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap4'
CRISPY_TEMPLATE_PACK = 'bootstrap4'

# https://github.com/jakubroztocil/django-settings-export
SETTINGS_EXPORT = [
    'SHOW_ORGANS',
    'MOUSEDB',
    'TEST_ENVIRONMENT',
    'FISHDB',
    'IMPORT_QUESTION'
]