import os

DATABASE_ENGINE = 'sqlite3'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'localflavor',
    'contactBox',
)
DATABASES = {
    'default': {
        'NAME': ':memory:',
        'ENGINE': 'django.db.backends.sqlite3',
    },
}

project = lambda: os.path.dirname(os.path.realpath(__file__))
location = lambda x: os.path.join(str(project()), str(x))

TEMPLATE_DIRS = (
    location("templates"),
)

STATIC_ROOT = location("static")

STATICFILES_DIRS = [
    location("static"),
]

SECRET_KEY = 'fake'

ROOT_URLCONF = 'test_project.urls'

try:
    from local_settings import *
except ImportError:
    pass


import sys
TESTING = ('test' in sys.argv)
TEST_CHARSET = 'utf8'

if TESTING:
    try:
        from test_settings import *        # pyflakes:ignore
        update_settings_for_tests(locals())
    except ImportError:
        pass
