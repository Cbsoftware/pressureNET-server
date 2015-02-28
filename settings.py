import datetime
import os
from logging.handlers import SysLogHandler
# Django settings for pressurenet project.

DEBUG = False
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

PROJECT_PATH = os.path.realpath(os.path.dirname(__file__))

MANAGERS = ADMINS

ALLOWED_HOSTS = (
    # Staging
    'staging.pressurenet.io',
    'pressurenet-staging.elasticbeanstalk.com',

    # Live
    'web.pressurenet.io',
    'ingest.pressurenet.io',
    'api.pressurenet.io',
    'pressurenet.io',
    'www.pressurenet.io',
    'pressurenet.cumulonimbus.ca',
)

DEFAULT_FROM_EMAIL = 'pressureNET API <livestream@cumulonimbus.ca>'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': os.environ.get('PSQL_DB_NAME'),
        'USER': os.environ.get('PSQL_USERNAME'),
        'PASSWORD': os.environ.get('PSQL_PASSWORD'),
        'HOST': os.environ.get('PSQL_ENDPOINT'),
        'PORT': os.environ.get('PSQL_PORT'),
    }
}

CACHE_TIMEOUT = 14 * 24 * 60 * 60

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': os.environ.get('CACHE_ENDPOINT', ''),
    }
}

EMAIL_BACKEND = 'django_ses.SESBackend'

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'America/Toronto'

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

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = os.environ.get('MEDIA_URL', '/media/')

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
MEDIA_ROOT = os.path.join(PROJECT_PATH, 'served/media')
STATIC_ROOT = os.path.join(PROJECT_PATH, 'served/static')


# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = os.environ.get('STATIC_URL', '/static/')

STATICFILES_DIRS = (
    os.path.join(PROJECT_PATH, 'static/'),
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = os.environ.get('SECRET_KEY', 'TODO')

TEMPLATE_DIRS = (
    os.path.join(PROJECT_PATH, 'templates/'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

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
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.request',
    'django.core.context_processors.i18n',
    'django.core.context_processors.debug',
    'django.contrib.messages.context_processors.messages',
    'django.core.context_processors.static',
)

ROOT_URLCONF = 'urls'

INSTALLED_APPS = (
    'grappelli.dashboard',
    'grappelli',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.staticfiles',

    'froala_editor',
    'raven.contrib.django.raven_compat',
    'rest_framework',
    'south',
    'storages',
    'urlobject',
    'widget_tweaks',

    'blog',
    'customers',
    'home',
    'readings',
    'utils',
)

# AWS Settings
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID', '')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_KEY', '')

# S3 Bucket
S3_PUBLIC_BUCKET = os.environ.get('S3_PUBLIC_BUCKET', '')
S3_PRIVATE_BUCKET = os.environ.get('S3_PRIVATE_BUCKET', '')

# DynamoDB
DYNAMODB_TABLE = os.environ.get('DYNAMODB_TABLE', '')

# S3 Readings Log Duration in milliseconds
ALL_DURATIONS = (
    ('10minute', (10 * 60 * 1000)),
    #('hourly', (60 * 60 * 1000)),
    #('daily', (24 * 60 * 60 * 1000)),
)
LOG_DURATIONS = {
    'split': [], #('daily',),
    'combined': ('10minute', ),#'hourly', 'daily'),
}
STATISTICS_DURATIONS = ('10minute', 'hourly')

# Storage Settings
DEFAULT_FILE_STORAGE = 'utils.s3.MediaS3Storage'
AWS_STORAGE_BUCKET_NAME = S3_PUBLIC_BUCKET

# Redis Settings
REDIS_URL = os.environ.get('REDIS_URL', '')

# Celery Settings
BROKER_URL = 'redis://{redis}:6379/0'.format(redis=REDIS_URL)

CELERYBEAT_SCHEDULE = {
    'block-handler': {
        'task': 'tasks.aggregator.BlockHandler',
        'schedule': datetime.timedelta(minutes=10),
    },
}

CELERY_TIMEZONE = 'UTC'

# Grappelli Admin
GRAPPELLI_ADMIN_TITLE = 'PressureNET Admin'

GRAPPELLI_INDEX_DASHBOARD = 'dashboard.PressureNETIndexDashboard'


# Django Rest Framework
REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': ('rest_framework.filters.DjangoFilterBackend',),
    'DEFAULT_THROTTLE_CLASSES': (
    ),
    'DEFAULT_THROTTLE_RATES': {
        'user': '4/min',
    }
}

MAX_CALL_LENGTH = 10000

# Google Play
PLAY_STORE_URL = 'https://play.google.com/store/apps/details?id=ca.cumulonimbus.barometernetwork'


# Sentry Logging
RAVEN_CONFIG = {
    'dsn': os.environ.get('SENTRY_ENDPOINT', ''),
}

# Loggly Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'loggly': {
            'format':'loggly: %(message)s',
        },
    },
    'handlers': {
        'syslog': {
            'level':'DEBUG',
            'class':'logging.handlers.SysLogHandler',
            'formatter': 'loggly',
            'facility': SysLogHandler.LOG_LOCAL2,
            'address': '/dev/log',
        },
    },
    'loggers': {
        'loggly':{
            'handlers': ['syslog'],
            'propagate': True,
            'level': 'DEBUG',
        },
    }
}

try:
    from settings_local import *
except:
    pass
