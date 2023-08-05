import os
import random
import string

DEBUG = True

DATABASES = {
  'default': {
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME': ':memory:',
    'TEST_NAME': ':memory:',
  },
}

ROOT_URLCONF = 'homebanking.urls'
SITE_ID = 1
SECRET_KEY = ''.join([random.choice(string.ascii_letters) for x in range(40)])

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'homebanking',
)

TEST_RUNNER = 'django.test.simple.DjangoTestSuiteRunner'

PASSWORD_HASHERS = ('django.contrib.auth.hashers.MD5PasswordHasher',)
LOGIN_REDIRECT_URL = '/users/me/'
TIMEZONE = 'UTC'

# homebanking settings
HOMEBANKING_BACKEND = 'sparnord'
