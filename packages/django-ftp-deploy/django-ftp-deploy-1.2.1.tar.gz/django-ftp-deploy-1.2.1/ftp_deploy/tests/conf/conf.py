from os.path import abspath, basename, dirname, join, normpath
from os.path import join

import logging
selenium_logger = logging.getLogger('selenium.webdriver.remote.remote_connection')
selenium_logger.setLevel(logging.ERROR)

from service.settings import *


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
        "USER": "",
        "PASSWORD": "",
        "HOST": "",
        "PORT": "",
    },
}

DJANGO_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
)

THIRD_PARTY_APPS = (
    'crispy_forms',
    'braces',
    'south',
    'django_nose',
    'django_coverage'
)

LOCAL_APPS = (
    'ftp_deploy',
    'ftp_deploy.server',
)

INSTALLED_APPS = THIRD_PARTY_APPS + LOCAL_APPS + DJANGO_APPS

PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.MD5PasswordHasher',
)
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

SOUTH_TESTS_MIGRATE = False
DEFAULT_FILE_STORAGE = "inmemorystorage.InMemoryStorage"

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'


