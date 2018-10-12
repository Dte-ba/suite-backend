# coding: utf-8
import os
import sys
import dj_database_url

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

VERSION_NUMBER = "2.1.49"

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '!b5t3zyyr+6(*&^75v%drix74^0b2kqebk81gtmozqk+w3*-1&'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    'localhost',
    '*',
    '0.0.0.0',
    '127.0.0.1',
    'suite.dtelab.com.ar',
    'suite2.dtelab.com.ar',
    'suite.enjambrelab.com.ar',
    '104.236.57.216',
    'testing-suite-backend.dtelab.com.ar',
]


JSON_API_FORMAT_KEYS = 'dasherize'
JSON_API_FORMAT_RELATION_KEYS = 'dasherize'
JSON_API_PLURALIZE_RELATION_TYPE = True
CORS_ORIGIN_ALLOW_ALL = True
APPEND_SLASH = False

# Application definition

INSTALLED_APPS = [
    'escuelas.apps.EscuelasConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django_rq',
    'permisos.apps.PermisosConfig',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django_coverage',
    'django.contrib.staticfiles',
    'dal',
    'dal_select2',
    'rest_framework',
    'rest_framework.authtoken',
    'django_extensions',
    'easy_pdf',
]


RQ_QUEUES = {
    'default': {
         'URL': os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
    }
}


STATIC_ROOT = 'staticfiles'
STATIC_URL = '/static/'

MEDIA_ROOT = os.environ.get('SUITE_MEDIA_ROOT', 'media_archivos_locales')
MEDIA_URL = '/media/'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'suite.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['suite/templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
    ),
    'PAGE_SIZE': 15,
    'EXCEPTION_HANDLER': 'rest_framework_json_api.exceptions.exception_handler',
    'DEFAULT_PAGINATION_CLASS':
        'rest_framework_json_api.pagination.PageNumberPagination',
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework_json_api.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser'
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework_json_api.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ),
    'DEFAULT_METADATA_CLASS': 'rest_framework_json_api.metadata.JSONAPIMetadata',
}

WSGI_APPLICATION = 'suite.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases


"""
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
"""

DATABASES = {
}



db_url = os.environ.get('DOKKU_POSTGRES_WHITE_URL', 'sqlite://./database.sqlite')
DATABASES['default'] = dj_database_url.config(conn_max_age=600, default=db_url)

SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY', None)


# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'es-ar'

TIME_ZONE = 'America/Argentina/Buenos_Aires'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# Para que el resultado de los tests pueda verse en colores.
TEST_RUNNER="redgreenunittest.django.runner.RedGreenDiscoverRunner"

GRAPH_MODELS = {
  'all_applications': True,
  'group_models': True,
}


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
        },
        'xhtml2pdf': {
            'handlers': ['console'],
            'level': 'ERROR'
       },
    },
}
