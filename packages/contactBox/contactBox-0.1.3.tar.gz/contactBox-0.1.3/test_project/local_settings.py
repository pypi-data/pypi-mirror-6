import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

project = lambda: os.path.dirname(os.path.realpath(__file__))
location = lambda x: os.path.join(str(project()), str(x))

DEBUG = True

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.admin',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'localflavor',
    'south',
    'contactBox',
)

SITE_ID = 1

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'contactbox',
        'USER': 'contactbox',
        'PASSWORD': 'contactbox',
        'HOST': "127.0.0.1",
        'PORT': '3306',
    },
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/
STATIC_ROOT = location(os.path.join("site_media", "static"))

# Additional directories which hold static files
STATICFILES_DIRS = [
    location("static"),
]

STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    "compressor.finders.CompressorFinder",
)

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = location(os.path.join("site_media", "media"))

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = "/static/"

ADMIN_MEDIA_ROOT = location(os.path.join("static", "admin"))

EMAIL_USE_TLS = True
EMAIL_HOST = 'email-smtp.us-east-1.amazonaws.com'
EMAIL_HOST_PASSWORD = 'ApkzlEQ9AuuQFFSgmCSSmOPqhawt+diMJvHxTxWUNtAk'
EMAIL_HOST_USER = 'AKIAIBZV3BA6HZSHI5BQ'
EMAIL_PORT = 587
DEFAULT_FROM_EMAIL = 'jacek@ivolution.pl'
SERVER_EMAIL = 'jacek@ivolution.pl'

EMAIL_FROM = DEFAULT_FROM_EMAIL
