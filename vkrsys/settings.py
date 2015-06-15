"""
Django settings for vkrsys project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import ConfigParser
from datetime import timedelta
import urlparse
from celery.schedules import crontab

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, 'config.conf')
SONGS_PATH = os.path.join(BASE_DIR, 'songs')

config = ConfigParser.ConfigParser()
config.read(CONFIG_PATH)

API_URL = config.get('api', 'URL')

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config.get('django', 'SECRET_KEY')

VK_APP_ID = config.get('vk', 'VK_APP_ID')
VK_API_SECRET = config.get('vk', 'VK_API_SECRET')
VK_EXTRA_SCOPE = [
    'audio',
    'friends'
]

VK_LOGIN_URL = '/social/login/vk-oauth/'


# Celery Daemon
BROKER_URL = config.get('celery', 'BROKER_URL')
CELERY_RESULT_BACKEND = config.get('celery', 'CELERY_RESULT_BACKEND')

CELERY_TASK_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']  # Ignore other content
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Europe/Moscow'
CELERY_ENABLE_UTC = True

CELERYBEAT_SCHEDULE = {
    'rsys-learn-online': {
        'task': 'app.tasks.rsys_learn_online',
        'schedule': crontab(hour='*', minute=30),
        'args': []
    },
    'rsys-learn-offline': {
        'task': 'app.tasks.rsys_learn_offline',
        'schedule': crontab(hour=0, minute=0),
        'args': []
    },
    'music-downloader': {
        'task': 'app.tasks.download_and_process_songs',
        'schedule': crontab(hour=3, minute=0),
        'args': [10]
    }
}

CELERY_ROUTES = {
    'app.tasks.save_music': {'queue': 'q__save_music'},
    'app.tasks.download_and_process_songs': {'queue': 'q__download_and_process_songs'},
    'app.tasks.download_and_process_song': {'queue': 'q__download_and_process_song'},
    'app.tasks.fingerprint_song': {'queue': 'q__fingerprint_song'},
    'app.tasks.rsys_learn_online': {'queue': 'q__rsys_learn_online'},
    'app.tasks.rsys_learn_offline': {'queue': 'q__rsys_learn_offline'},
}


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
PRODUCTION = not DEBUG
PREVIEW = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = ['*']

CSRF_COOKIE_HTTPONLY = False
CROSS_ORIGIN_ALLOW_ALL = True if DEBUG else False


# Application definition

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGIN_ERROR_URL = '/login-error/'

SOCIAL_AUTH_PIPELINE = (
    'social_auth.backends.pipeline.social.social_auth_user',
    # 'social_auth.backends.pipeline.associate.associate_by_email',
    'social_auth.backends.pipeline.user.get_username',
    'social_auth.backends.pipeline.user.create_user',
    'social_auth.backends.pipeline.social.associate_user',
    'social_auth.backends.pipeline.social.load_extra_data',
    'social_auth.backends.pipeline.user.update_user_details',
    'app.pipeline.user_created',

)

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'app',
    'social_auth',
    'vkrsys'
)

AUTHENTICATION_BACKENDS = (
    'social_auth.backends.contrib.vk.VKOAuth2Backend',
    'django.contrib.auth.backends.ModelBackend',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'vkrsys.urls'

WSGI_APPLICATION = 'vkrsys.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': config.get('db', 'ENGINE'),
        'NAME': config.get('db', 'NAME'),
        'USER': config.get('db', 'USER'),
        'PASSWORD': config.get('db', 'PASSWORD'),
        'HOST': config.get('db', 'HOST'),
        'PORT': config.get('db', 'PORT')
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '%s:%s' % (config.get('memcached', 'HOST'), config.get('memcached', 'PORT')),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

ugettext = lambda s: s
LANGUAGES = (
    ('en', ugettext('English')),
    ('ru', ugettext('Russian')),
)
LANGUAGE_CODE = 'en-us'

LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'app/locale'),
)

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_L10N = True

USE_TZ = True





# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'app/static')
SONGS_ARTS_PATH = os.path.join(STATIC_ROOT, 'arts')
SONGS_ARTS_URL = urlparse.urljoin(STATIC_URL, 'arts/')
SONGS_DEFAULT_ART_URL = urlparse.urljoin(SONGS_ARTS_URL, 'default.png')

USERPIC_CACHE_DURATION = eval(config.get('memcached', 'USERPIC_CACHE_DURATION'))
SONG_URL_CACHE = eval(config.get('memcached', 'SONG_URL_CACHE'))

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "static"),
)

TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, 'templates'),
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
    "app.context_processors.production_state",
)