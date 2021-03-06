"""
Django settings for opencontest project.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, "contest/static")

# --------------- Configure settings from environment ---------------------
# Default LOG_LEVEL 
OC_LOG_LEVEL = os.environ.get('OC_LOG_LEVEL', 'INFO')
# Maximum test output to retain / display
OC_MAX_OUTPUT_LEN = int(os.environ.get('OC_MAX_OUTPUT_LEN', 10000000))    # (bytes) Submission output larger than this is discarded
OC_MAX_DISPLAY_LEN = int(os.environ.get('OC_MAX_DISPLAY_LEN', 50000))     # (bytes) Submission output larger than this is not displayed
OC_MAX_DISPLAY_LINES = int(os.environ.get('OC_MAX_DISPLAY_LINES', 300))   # (lines) Submission output having more lines than this is not displayed
OC_DOCKERIMAGE_BASE = os.environ.get('OC_DOCKERIMAGE_BASE', 'bjucps/open-contest')
# Maximum submissions to run at once
OC_MAX_CONCURRENT_SUBMISSIONS = int(os.environ.get("OC_MAX_CONCURRENT_SUBMISSIONS", 15))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '0oqd#=9^s2r3q9*43=4#d0_n8f5-#=lurr9x!^8(-45+jclrkl'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'contest.apps.ContestConfig'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'opencontest.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'opencontest.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'log': {
            'format': '{asctime} {levelname} {module}  {message}',
            'style': '{',
            'datefmt' : '%H:%M:%S'
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'log'
        }
    },
    'loggers': {
        'contest': {
            'handlers': ['console'],
            'level': OC_LOG_LEVEL, 
        },
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True
        }
    }
}
