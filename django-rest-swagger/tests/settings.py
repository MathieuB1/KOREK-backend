import os

SECRET_KEY = 'fake-key'

PRIVACY_MODE = os.environ.get('PRIVACY_MODE', 'PRIVATE'),

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'tests',
]
ROOT_URLCONF = []
DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3'}}
