# Basic settings for django. They should enable localhost-only development.
# These settings are extended for actual production use.

# Before go-live review: https://docs.djangoproject.com/en/dev/howto/deployment/checklist/

import os.path

TEMPLATE_DEBUG = DEBUG = True
# If development is set to true, all calls to Sailpoint are bypassed with stubbed returns.
DEVELOPMENT = True

DATABASES = {
    'default': {
        'ENGINE':   'django.db.backends.sqlite3',
        'NAME':     'sqlite.db',
    }
}

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.6/ref/settings/#allowed-hosts
ALLOWED_HOSTS = []

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'America/Los_Angeles'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = False

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = False

# MyInfo / OAM does not use user-uploaded media at any point.
MEDIA_ROOT = ''
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = '/var/www/html/static/'

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'developmentkey'

MIDDLEWARE_CLASSES = (
    'downtime.middleware.DowntimeMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django_cas.middleware.CASMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'lib.backends.OAMLoginBackend',
    'lib.backends.AccountPickupBackend',
    'lib.backends.ForgotPasswordBackend',
    'django_cas.backends.CASBackend',
)


ROOT_URLCONF = 'oam_base.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'oam_base.wsgi.application'

# django.core.context_processors moves in django 1.8
# to django.template.context_processors
TEMPLATE_CONTEXT_PROCESSORS = (
    # defaults
    "django.contrib.auth.context_processors.auth",  # provides 'user' and 'perms'
    "django.core.context_processors.debug",  # provides 'debug', 'sql_queries'
    "django.core.context_processors.i18n",  # provides language localization info
    "django.core.context_processors.media",  # provides 'MEDIA_URL'
    "django.core.context_processors.static",  # provides 'STATIC_URL'
    "django.core.context_processors.tz",  # provides 'TIME_ZONE'
    "django.contrib.messages.context_processors.messages",  # provides 'messages' and 'DEFAULT_MESSAGE_LEVELS'
    # Custom
    "oam_base.context_processors.identity",  # request.session['identity']
    "oam_base.context_processors.cancel",  # request.session['ALLOW_CANCEL']
)

TEMPLATE_DIRS = (
    os.path.join(os.path.dirname(__file__), 'templates').replace('\\', '/'),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'CustomUser',
    'MyInfo',
    'AccountPickup',
    'PasswordReset',
    'lib',
    # Apps related to plugins.
    'ajax',
    'localflavor',
    'downtime',
    'ods_integration',
    'Duo',
    'debug_toolbar.apps.DebugToolbarConfig',
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s - %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'RotatingFileHandler': {
            'filename': 'myinfo.log',
            'maxBytes': 262144,
            'backupCount': 5,
            'formatter': 'verbose',
            'class': 'logging.handlers.RotatingFileHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'oam_base': {
            'handlers': ['RotatingFileHandler'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'AccountPickup': {
            'handlers': ['RotatingFileHandler'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'MyInfo': {
            'handlers': ['RotatingFileHandler'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'PasswordReset': {
            'handlers': ['RotatingFileHandler'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'django_cas': {
            'handlers': ['RotatingFileHandler'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'lib': {
            'handlers': ['RotatingFileHandler'],
            'level': 'DEBUG',
            'propagate': False,
        },
    }
}

AUTH_USER_MODEL = 'CustomUser.PSUCustomUser'

# Settings related to CAS authentication.
# CAS_SERVER_URL = ''
# CAS_VERSION = '1'
CAS_SERVER_URL = 'https://ssodevel.oit.pdx.edu/cas/'
CAS_VERSION = 'CAS_2_SAML_1_0'

# Settings related to sailpoint.
SAILPOINT_SERVER_URL = ''
SAILPOINT_USERNAME = ''
SAILPOINT_PASSWORD = ''

# Username length patch.
MAX_USERNAME_LENGTH = 36

# Downtime exempt paths.
DOWNTIME_EXEMPT_PATHS = (
    '/admin',
    '/accounts/login',
    '/MyInfo/ping',
)

# Settings for password reset import management command.
ORACLE_USER = ''
ORACLE_PASS = ''

ORACLE_HOST = ''
ORACLE_PORT = ''
ORACLE_SID = ''

ORACLE_SQL = ''

# Cache backend for ratelimiting when behind a load balancer.
RATELIMIT_CACHE_BACKEND = 'lib.brake_cache.LoadBalancerCache'

# Duo Settings
DUO_LOGIN_URL = 'duo'
DUO_HOST = 'api-ac9fc019.duosecurity.com'

# Duo WebSDK Api
DUO_IKEY = ''
DUO_SKEY = ''
DUO_AKEY = ''
