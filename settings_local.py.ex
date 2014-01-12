import os

CACHE_TIMEOUT = 0

# Django settings for pressurenet project.
DEBUG = True
TEMPLATE_DEBUG = DEBUG

DATABASES = {
    'default': {
        'ENGINE': 'sqlite3',  # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'pnet_dev',                      # Or path to database file if using sqlite3.
        # The following settings are not used with sqlite3:
        'USER': 'root',
        'PASSWORD': 'root',
        'HOST': 'localhost',                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '',                      # Set to empty string for default.
    }
}


CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# Sentry Logging
RAVEN_CONFIG = {
}

# AWS Settings
AWS_ACCESS_KEY_ID = 'TODO'
AWS_SECRET_ACCESS_KEY = 'TODO'

# SQS Queue
SQS_QUEUE = 'TODO'

# S3 Bucket
S3_PUBLIC_BUCKET = 'TODO'
S3_PRIVATE_BUCKET = 'TODO'

# S3 Readings Log Duration in milliseconds
LOG_PERSIST_DURATION = 1 * 60 * 1000
LOG_DURATIONS = (
)
