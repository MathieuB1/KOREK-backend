import os

SECRET_KEY = 'fake-key'

PRIVACY_MODE = os.environ.get('PRIVACY_MODE', 'PRIVATE'),
EMAIL_HOST_USER = 'xxxx.yyy@gmail.com',

DATA_UPLOAD_MAX_NUMBER_FIELDS = 10240

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'tests',
]
ROOT_URLCONF = []
DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3'}}
