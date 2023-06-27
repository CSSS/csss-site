import logging
import logging.config
import sys
from typing import Optional

import environ
import os


if 'ENVIRONMENT' not in os.environ:
    raise Exception("[settings.py] ENVIRONMENT was not detected")
ENVIRONMENT = os.environ['ENVIRONMENT']
print(f"[settings.py] ENVIRONMENT set to {ENVIRONMENT}")

if ENVIRONMENT != "LOCALHOST" and ENVIRONMENT != "STAGING" and ENVIRONMENT != "PRODUCTION":
    print('[settings.py] ENVIRONMENT is not a valid value')
    exit(1)


# SECURITY WARNING: keep the secret key used in production secret!
if ENVIRONMENT != "LOCALHOST":
    if 'WEBSITE_SECRET_KEY' not in os.environ:
        raise Exception("[settings.py] NO WEBSITE_SECRET_KEY was detected")
    SECRET_KEY = os.environ['WEBSITE_SECRET_KEY']
else:
    SECRET_KEY = 'localhost'


if 'BASE_DIR' in os.environ:
    BASE_DIR = os.environ['BASE_DIR']
else:
    # Build paths inside the project like this: os.path.join(BASE_DIR, ...)
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))

LOG_LOCATION = os.environ['LOG_LOCATION'] if 'LOG_LOCATION' in os.environ else None
if LOG_LOCATION is None:
    raise Exception("[settings.py] NO LOG_LOCATION was detected")

if 'LOG_LOCATION' not in os.environ:
    raise Exception("[settings.py] NO LOG_LOCATION was detected")

LOG_LOCATION = os.environ['LOG_LOCATION']

# SECURITY WARNING: don't run with debug turned on in production!
if ENVIRONMENT != "LOCALHOST":
    if "DEBUG" not in os.environ:
        raise Exception("[settings.py] DEBUG was not detected")
    DEBUG = os.environ['DEBUG'] == "true"
else:
    DEBUG = True

print(f'[settings.py] DEBUG set to {DEBUG}')

USE_I18N = True

USE_L10N = True

USE_TZ = True


SYS_STREAM_LOG_HANDLER_NAME = 'sys_stream'
DJANGO_SETTINGS_LOG_HANDLER_NAME = "django_settings"

from csss.setup_logger import Loggers # noqa E402

Loggers.get_logger(logger_name=DJANGO_SETTINGS_LOG_HANDLER_NAME)

print(f'[settings.py] BASE_DIR set to {BASE_DIR}')
print(f'[settings.py] LOG_LOCATION set to {LOG_LOCATION}')

SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"

SESSION_COOKIE_HTTPONLY = True

# https://stackoverflow.com/a/40522604/7734535
SESSION_COOKIE_AGE = 3600  # one hour in seconds

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/


if 'STAGING_SERVER' in os.environ:
    STAGING_SERVER = os.environ['STAGING_SERVER']
else:
    STAGING_SERVER = 'https://dev.sfucsss.org/'
print(f'[settings.py] STAGING_SERVER set to {STAGING_SERVER}')

PORT = 8000

if ENVIRONMENT != "LOCALHOST" and "HOST_ADDRESS" not in os.environ:
    raise Exception("[settings.py] HOST_ADDRESS is not set but the environment is not LOCALHOST")

if "HOST_ADDRESS" in os.environ:
    HOST_ADDRESS = os.environ['HOST_ADDRESS']
else:
    HOST_ADDRESS = "127.0.0.1"
ALLOWED_HOSTS = [HOST_ADDRESS]

print(f'[settings.py] HOST_ADDRESS set to {HOST_ADDRESS}')
print(f'[settings.py] ALLOWED_HOSTS set to {ALLOWED_HOSTS}')

if "DB_TYPE" not in os.environ:
    raise Exception("[settings.py] DB_TYPE is not detected")
DB_TYPE = os.environ['DB_TYPE']
print(f'[settings.py] DB_TYPE set to {DB_TYPE}')

if "BRANCH_NAME" not in os.environ and ENVIRONMENT == "STAGING":
    raise Exception("[settings.py] there is no branch name detected in staging environment")

URL_ROOT = "/"
URL_PATTERN = ""

if "BRANCH_NAME" in os.environ:
    if os.environ['BRANCH_NAME'] != "master":
        URL_PATTERN = f"{os.environ['BRANCH_NAME']}/"
        URL_ROOT = f"/{URL_PATTERN}"

print(f'[settings.py] URL_ROOT set to {URL_ROOT}')
print(f'[settings.py] URL_PATTERN set to {URL_PATTERN}')

# SETTINGS FOR GOOGLE_DRIVE
GDRIVE_SCOPES = ['https://www.googleapis.com/auth/drive']


def env_getter(key) -> Optional[str]:
    env_variable = None
    if ENVIRONMENT == "LOCALHOST" and key in os.environ:
        env_variable = os.environ[key]
    elif ENVIRONMENT == "PRODUCTION" or ENVIRONMENT == "STAGING":
        if key not in os.environ:
            raise Exception(f"[settings.py] {key} is not detected in ENVIRONMENT {ENVIRONMENT}")
        env_variable = os.environ[key]
    if env_variable is not None and not env_variable != "":
        raise Exception(f"[settings.py] empty value for {key}")
    return env_variable

GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_ID_FOR_GENERAL_DOCUMENTS = env_getter('GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_ID_FOR_GENERAL_DOCUMENTS') # noqa E501

GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_FOLDER_ID_FOR_PUBLIC_GALLERY = env_getter('GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_FOLDER_ID_FOR_PUBLIC_GALLERY') # noqa E501
GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_ID_FOR_PUBLIC_GALLERY = env_getter('GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_ID_FOR_PUBLIC_GALLERY') # noqa E501

GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_FOLDER_ID_FOR_PRIVATE_GALLERY = env_getter('GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_FOLDER_ID_FOR_PRIVATE_GALLERY') # noqa E501
GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_ID_FOR_PRIVATE_GALLERY = env_getter('GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_ID_FOR_PRIVATE_GALLERY') # noqa E501

GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_FOLDER_ID_FOR_DEEP_EXEC = env_getter('GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_FOLDER_ID_FOR_DEEP_EXEC') # noqa E501

GDRIVE_TOKEN_LOCATION = env_getter('GDRIVE_TOKEN_LOCATION')
GITHUB_ACCESS_TOKEN = env_getter('GITHUB_ACCESS_TOKEN')
SFU_CSSS_GMAIL_USERNAME = env_getter('SFU_CSSS_GMAIL_USERNAME')
SFU_CSSS_GMAIL_PASSWORD = env_getter('SFU_CSSS_GMAIL_PASSWORD')
DISCORD_BOT_TOKEN = env_getter('DISCORD_BOT_TOKEN')
GUILD_ID = env_getter('GUILD_ID')
SFU_ENDPOINT_TOKEN = env_getter('SFU_ENDPOINT_TOKEN')
DEV_DISCORD_ID = os.environ['DEV_DISCORD_ID'] if 'DEV_DISCORD_ID' in os.environ else None

if DEV_DISCORD_ID is not None and not DEV_DISCORD_ID != "":
    raise Exception("[settings.py] empty value for DEV_DISCORD_ID")

print(f"[settings.py] GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_ID_FOR_GENERAL_DOCUMENTS={GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_ID_FOR_GENERAL_DOCUMENTS}") # noqa E501
print(f"[settings.py] GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_FOLDER_ID_FOR_PUBLIC_GALLERY={GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_FOLDER_ID_FOR_PUBLIC_GALLERY}") # noqa E501
print(f"[settings.py] GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_ID_FOR_PUBLIC_GALLERY={GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_ID_FOR_PUBLIC_GALLERY}") # noqa E501
print(f"[settings.py] GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_FOLDER_ID_FOR_PRIVATE_GALLERY={GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_FOLDER_ID_FOR_PRIVATE_GALLERY}") # noqa E501
print(f"[settings.py] GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_ID_FOR_PRIVATE_GALLERY={GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_ID_FOR_PRIVATE_GALLERY}") # noqa E501
print(f"[settings.py] GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_FOLDER_ID_FOR_DEEP_EXEC={GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_FOLDER_ID_FOR_DEEP_EXEC}") # noqa E501
print(f"[settings.py] GDRIVE_TOKEN_LOCATION={GDRIVE_TOKEN_LOCATION}")
print(f"[settings.py] GITHUB_ACCESS_TOKEN={GITHUB_ACCESS_TOKEN}")
print(f"[settings.py] SFU_CSSS_GMAIL_USERNAME={SFU_CSSS_GMAIL_USERNAME}")
print(f"[settings.py] SFU_CSSS_GMAIL_PASSWORD={SFU_CSSS_GMAIL_PASSWORD}")
print(f"[settings.py] DISCORD_BOT_TOKEN={DISCORD_BOT_TOKEN}")
print(f"[settings.py] GUILD_ID={GUILD_ID}")
print(f"[settings.py] SFU_ENDPOINT_TOKEN={SFU_ENDPOINT_TOKEN}")
print(f"[settings.py] DEV_DISCORD_ID={DEV_DISCORD_ID}")

if GDRIVE_TOKEN_LOCATION is not None and not os.path.isfile(GDRIVE_TOKEN_LOCATION):
    raise Exception(f"[settings.py] file {GDRIVE_TOKEN_LOCATION} does not exist for GDRIVE_TOKEN_LOCATION")

# Application definition

discord_header = {
    "Authorization": f"Bot {DISCORD_BOT_TOKEN}",
    'Content-Type': 'application/json'
}

INSTALLED_APPS = [
    'csss',
    'announcements',
    'about',
    'events',
    'events.frosh',
    'events.mountain_madness',
    'events.fall_hacks',
    'events.tech_fair',
    'events.workshops',
    'resource_management',
    'static_pages',
    'django_mailbox',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'bootstrap3',
    'elections',
    'django.contrib.sites',
    'django_cas_ng'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

if not DEBUG:
    MIDDLEWARE.append(
        'csss.views.error_handlers.HandleBusinessExceptionMiddleware',
    )

ROOT_URLCONF = 'csss.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR + '/templates/', ],
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

WSGI_APPLICATION = 'csss.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

if DB_TYPE == "sqlite3":
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }

elif DB_TYPE == "postgres":

    if "DB_PASSWORD" not in os.environ:
        raise Exception("[settings.py] DB_PASSWORD is not detected")
    DB_PASSWORD = os.environ['DB_PASSWORD']

    if "DB_PORT" not in os.environ:
        raise Exception("[settings.py] DB_PORT is not detected")
    DB_PORT = os.environ['DB_PORT']
    if "DB_NAME" not in os.environ:
        raise Exception("[settings.py] DB_NAME is not detected")
    DB_NAME = os.environ['DB_NAME']

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': DB_NAME,
            'USER': 'postgres',
            'PASSWORD': DB_PASSWORD,
            'HOST': '127.0.0.1',
            'PORT': DB_PORT,
        }
    }
else:
    raise Exception(
        "[settings.py] DB_TYPE is not set to an acceptable type\nneed to use either \"sqlite3\" or \"postgres\""
    )

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'django_cas_ng.backends.CASBackend',
)

SITE_ID = 1

CAS_SERVER_URL = "https://cas.sfu.ca/cas/"
CAS_VERSION = '3'
CAS_LOGIN_MSG = None

STATICFILES_DIRS = []
if 'STATICFILES_DIRS' in os.environ:
    STATICFILES_DIRS = os.environ['STATICFILES_DIRS'].split(":")
print(f"[settings.py] STATICFILES_DIRS={STATICFILES_DIRS}")

# STATICFILES_DIRS = [
#    'static_files/',
# ]
# This is list of full paths your project should look fotr static files, beside standard apps. Namely,
# Django will automatically look for static files in your installed apps. If app has dir called static
# (app/static) all files and folders will be copied once you run collectstatic command. STATICFILES_DIRS
# defines additional paths where your staticfiles can be found

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

ROOT_DIR = environ.Path(__file__) - 4
print(f'[settings.py] ROOT_DIR set to {ROOT_DIR}')

STATIC_URL = f"{URL_ROOT}STATIC_URL/"
print(f'[settings.py] STATIC_URL set to {STATIC_URL}')

# is the URL on your website where these collected files will be accessible. IE: mysite.com/ static/
# This is something that tells your browser where to look for JavaScript and CSS files

STATIC_ROOT = os.path.join(BASE_DIR, 'static_root/')
print(f'[settings.py] STATIC_ROOT set to {STATIC_ROOT}')

# This is destination directory for your static files. This should be absolute path in yor file system,
# for example: "/var/www/project/static" If you run 'python manage.py collectstatic' it will collect all
# static files from your project and copy them into STATIC_ROOT dir
MEDIA_URL = '/MEDIA_URL/'
print(f'[settings.py] MEDIA_URL set to {MEDIA_URL}')

# URL that handles the media served from MEDIA_ROOT, used for managing stored files. It must end in a slash
# if set to a non-empty value. You will need to configure these
# files to be served in both development and production environments.


MEDIA_ROOT = os.path.join(BASE_DIR, 'media_root/')
print(f'[settings.py] MEDIA_ROOT set to {MEDIA_ROOT}')

# Absolute filesystem path to the directory that will hold user-uploaded files.


FILE_FORM_MASTER_DIR = 'form_uploads/form_uploads/'
FILE_FORM_UPLOAD_DIR = FILE_FORM_MASTER_DIR + 'temporary_files/'  # temporary files from form upload go here
DJANGO_MAILBOX_ATTACHMENT_UPLOAD_TO = 'mailbox_attachments/%Y/%m/%d/'  # will be placed under the MEDIA_ROOT folder
print(f'[settings.py] FILE_FORM_MASTER_DIR set to {FILE_FORM_MASTER_DIR}')
print(f'[settings.py] FILE_FORM_UPLOAD_DIR set to {FILE_FORM_UPLOAD_DIR}')
print(f'[settings.py] DJANGO_MAILBOX_ATTACHMENT_UPLOAD_TO set to {DJANGO_MAILBOX_ATTACHMENT_UPLOAD_TO}')

Loggers.setup_sys_stream_logger()

LOGGING_CONFIG = None

logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'formatters': {
        'django.server': {
            '()': 'django.utils.log.ServerFormatter',
            'format': '[{server_time}] {message}',
            'style': '{',
        }
    },
    'handlers': {
        'info_handler': {
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'csss.CSSSLoggerHandlers.CSSSDebugStreamHandler',
            "stream": sys.__stdout__  # setting this up manually because this specific property had to be changed,
            # and I was too lazy to figure out how to customize this via
            # https://docs.djangoproject.com/en/4.1/topics/logging/#configuring-logging
        },
        'error_handler': {
            'level': 'ERROR',
            'filters': ['require_debug_true'],
            'class': 'csss.CSSSLoggerHandlers.CSSSErrorHandler',
            "stream": sys.__stderr__  # setting this up manually because this specific property had to be changed,
            # and I was too lazy to figure out how to customize this via
            # https://docs.djangoproject.com/en/4.1/topics/logging/#configuring-logging
        },
        'django.server': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            "stream": sys.__stdout__,  # setting this up manually because this specific property had to be changed,
            # and I was too lazy to figure out how to customize this via
            # https://docs.djangoproject.com/en/4.1/topics/logging/#configuring-logging
            'formatter': 'django.server',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
        }
    },
    'loggers': {
        'django': {
            'handlers': ['info_handler', 'error_handler', 'mail_admins'],
            'level': 'INFO',
        },
        'django.server': {
            'handlers': ['django.server'],
            'level': 'INFO',
            'propagate': False,
        },
    }
})

print("settings.py finished")
