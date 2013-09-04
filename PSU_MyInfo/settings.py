# Django settings for PSU_MyInfo project.

# To keep certain information out of git, we move it to an ini file. The basic configuration
# syntax is therefore available to be seen, but the specific values are retained out of git.

from ConfigParser import RawConfigParser
config = RawConfigParser()
config.read('secure_settings.ini')

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = tuple(config.items('adminmail'))

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE':   config.get('database', 'DATABASE_ENGINE'),
        'NAME':     config.get('database', 'DATABASE_NAME'),
        'USER':     config.get('database', 'DATABASE_USER'),
        'PASSWORD': config.get('database', 'DATABASE_PASS'),
        'HOST':     config.get('database', 'DATABASE_HOST'),
        'PORT':     config.get('database', 'DATABASE_PORT'),
    }
}

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ['.pdx.edu']

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'America/Los_Angeles'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = config.get('static', 'STATIC_ROOT')

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
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = config.get('secrets', 'SECRET_KEY')

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django_cas.middleware.CASMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'lib.backends.ExpiredPasswordBackend',
    'lib.backends.AccountPickupBackend',
    'lib.backends.ForgotPasswordBackend',
    'django_cas.backends.CASBackend',
)


ROOT_URLCONF = 'PSU_MyInfo.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'PSU_MyInfo.wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# It is possible that we will need to implement a cache solution for rate limiting.

INSTALLED_APPS = (
    'longerusername', # This must be first so that it can patch the auth model.         
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    'MyInfo',
    'AccountPickup',
    'PasswordReset',
    'lib',
    # Apps related to plugins.
    'ajax',
    'widget_tweaks',
    'captcha',
    'south',
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
            'filename': 'my_info_log.txt',
            'maxBytes' : 262144,
            'backupCount' : 5,
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
        'PSU_MyInfo': {
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

# Settings related to CAS authentication.
CAS_SERVER_URL = config.get('cas', 'CAS_SERVER_URL')
CAS_VERSION = config.get('cas', 'CAS_VERSION')

# Settings related to sailpoint.
SAILPOINT_SERVER_URL = config.get('sailpoint', 'SAILPOINT_SERVER_URL')
SAILPOINT_USERNAME = config.get('sailpoint', 'SAILPOINT_USERNAME')
SAILPOINT_PASSWORD = config.get('sailpoint', 'SAILPOINT_PASSWORD')

# Settings related to reCAPTCHA
RECAPTCHA_USE_SSL = True
RECAPTCHA_PUBLIC_KEY = config.get('recaptcha', 'RECAPTCHA_PUBLIC_KEY')
RECAPTCHA_PRIVATE_KEY = config.get('recaptcha', 'RECAPTCHA_PRIVATE_KEY')

# Username length patch.
MAX_USERNAME_LENGTH = 36