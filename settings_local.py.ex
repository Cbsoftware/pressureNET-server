import os

# Django settings for pressurenet project.

PROJECT_PATH = os.path.realpath(os.path.dirname(__file__))

DEBUG = True
TEMPLATE_DEBUG = DEBUG

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',  # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'TODO',                      # Or path to database file if using sqlite3.
        # The following settings are not used with sqlite3:
        'USER': 'TODO',
        'PASSWORD': 'TODO',
        'HOST': 'localhost',                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '',                      # Set to empty string for default.
    }
}

MAPS_API = 'TODO'
ANALYTICS_API = 'TODO'
PRESSURENET_DATA_URL = 'TODO'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'TODO'
