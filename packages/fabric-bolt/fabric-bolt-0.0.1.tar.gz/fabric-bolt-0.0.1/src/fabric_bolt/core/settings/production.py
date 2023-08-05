# production server settings for core project.
from fabric_bolt.core.settings.base import *

DEBUG = True

DATABASES = {
    'default': {
        # The last part of ENGINE is 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'ado_mssql'.
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'django_dash', # Or path to database file if using sqlite3
        'USER': 'django_dash', # Not used with sqlite3.
        'PASSWORD': 'ad2@#adaw', # Not used with sqlite3.
        'HOST': 'dbc1.worthwhilenetwork.net', # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '', # Set to empty string for default. Not used with sqlite3.
        'SCHEMA': 'django_dash',
    }
}

# Make this unique, and don't share it with anybody.
SECRET_KEY = '3(-(r&8u8tawdawdawdawdwadSSSSSSSSSdawd@@#@#d=48-5p&(f'