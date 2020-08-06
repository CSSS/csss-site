import environ
import os
from csss.logger_setup import initialize_logger

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
logger = initialize_logger()

if 'BASE_DIR' in os.environ:
    BASE_DIR = os.environ['BASE_DIR']
else:
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
logger.info(f'[settings.py] BASE_DIR set to {BASE_DIR}')

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
if 'WEBSITE_SECRET_KEY' not in os.environ:
    logger.error("[settings.py] NO WEBSITE_SECRET_KEY was detected")
    exit(1)

SECRET_KEY = os.environ['WEBSITE_SECRET_KEY']

# SECURITY WARNING: don't run with debug turned on in production!
if "DEBUG" not in os.environ:
    logger.error("[settings.py] DEBUG was not detected")
    exit(1)
DEBUG = os.environ['DEBUG'] == "true"
logger.info(f'[settings.py] DEBUG set to {DEBUG}')

if "PORT" in os.environ:
    PORT = os.environ['PORT']
else:
    PORT = None
logger.info(f'[settings.py] PORT set to {PORT}')

if "HOST_ADDRESS" not in os.environ:
    logger.error("[settings.py] HOST_ADDRESS was not detected")
    exit(1)
HOST_ADDRESS = os.environ['HOST_ADDRESS']
ALLOWED_HOSTS = [HOST_ADDRESS]

logger.info(f'[settings.py] HOST_ADDRESS set to {HOST_ADDRESS}')
logger.info(f'[settings.py] ALLOWED_HOSTS set to {ALLOWED_HOSTS}')


if "DB_TYPE" not in os.environ:
    logger.error("[settings.py] DB_TYPE is not detected")
    exit(1)
DB_TYPE = os.environ['DB_TYPE']
logger.info(f'[settings.py] DB_TYPE set to {DB_TYPE}')


if "BRANCH_NAME" in os.environ:
    BRANCH_NAME = os.environ['BRANCH_NAME']
    if BRANCH_NAME != "master":
        URL_ROOT = f"/{os.environ['BRANCH_NAME']}/"
        URL_PATTERN = f"{os.environ['BRANCH_NAME']}/"
    else:
        URL_ROOT = "/"
        URL_PATTERN = ""
    logger.info(f'[settings.py] BASE_DIR set to {BRANCH_NAME}')
    logger.info(f'[settings.py] BASE_DIR set to {URL_ROOT}')
    logger.info(f'[settings.py] BASE_DIR set to {URL_PATTERN}')
else:
    URL_ROOT = "/"
    URL_PATTERN = ""
    logger.info(f'[settings.py] BASE_DIR set to {URL_ROOT}')
    logger.info(f'[settings.py] BASE_DIR set to {URL_PATTERN}')

# SETTINGS FOR GOOGLE_DRIVE
GDRIVE_SCOPES = ['https://www.googleapis.com/auth/drive']

if 'GDRIVE_ROOT_FOLDER_ID' in os.environ:
    GDRIVE_ROOT_FOLDER_ID = os.environ['GDRIVE_ROOT_FOLDER_ID']
else:
    GDRIVE_ROOT_FOLDER_ID = None
if 'GDRIVE_TOKEN_LOCATION' in os.environ:
    GDRIVE_TOKEN_LOCATION = os.environ['GDRIVE_TOKEN_LOCATION']
else:
    GDRIVE_TOKEN_LOCATION = None
if 'GITHUB_ACCESS_TOKEN' in os.environ:
    GITHUB_ACCESS_TOKEN = os.environ['GITHUB_ACCESS_TOKEN']
else:
    GITHUB_ACCESS_TOKEN = None
if 'GITLAB_PRIVATE_TOKEN' in os.environ:
    GITLAB_PRIVATE_TOKEN = os.environ['GITLAB_PRIVATE_TOKEN']
else:
    GITLAB_PRIVATE_TOKEN = None
if 'OFFICER_PHOTOS_PATH' in os.environ:
    OFFICER_PHOTOS_PATH = os.environ['OFFICER_PHOTOS_PATH']
else:
    OFFICER_PHOTOS_PATH = None

if not DEBUG:
    if GDRIVE_ROOT_FOLDER_ID is None:
        logger.error("[settings.py] GDRIVE_ROOT_FOLDER_ID was not detected")
        exit(1)

    if GDRIVE_TOKEN_LOCATION is None:
        logger.error("[settings.py] GDRIVE_TOKEN_LOCATION was not detected")
        exit(1)

    if GITHUB_ACCESS_TOKEN is None:
        logger.error("[settings.py] GITHUB_ACCESS_TOKEN was not detected")
        exit(1)

    if OFFICER_PHOTOS_PATH is None:
        logger.error("[settings.py] OFFICER_PHOTOS_PATH was not detected")
        exit(1)

    if GITLAB_PRIVATE_TOKEN is None:
        logger.error("[settings.py] GITLAB_PRIVATE_TOKEN was not detected")
        exit(1)


# Application definition

INSTALLED_APPS = [
    'csss',
    'announcements',
    'about',
    'documents',
    'events',
    'administration',
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
    'django_file_form',
    'file_uploads',
    'django_file_form.ajaxuploader',
    'django_bootstrap3_form',
    'django_pony_forms',
    'elections',
    'django.contrib.sites',
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


LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/done/'

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
        logger.error("[settings.py] DB_PASSWORD is not detected")
        exit(1)
    DB_PASSWORD = os.environ['DB_PASSWORD']

    if "DB_PORT" not in os.environ:
        logger.error("[settings.py] DB_PORT is not detected")
        exit(1)
    DB_PORT = os.environ['DB_PORT']
    if "DB_NAME" not in os.environ:
        logger.error("[settings.py] DB_NAME is not detected")
        exit(1)
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
    logger.error("[settings.py] DB_TYPE is not set to an acceptable type")
    logger.error("[settings.py] need to use either \"sqlite3\" or \"postgres\"")
    exit(1)

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

TIME_ZONE = 'America/Vancouver'

USE_I18N = True

USE_L10N = True

USE_TZ = False


AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)

SITE_ID = 1
LOGIN_REDIRECT_URL = '/products'

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
logger.info(f'[settings.py] ROOT_DIR set to {ROOT_DIR}')

STATIC_URL = f"{URL_ROOT}STATIC_URL/"
logger.info(f'[settings.py] STATIC_URL set to {STATIC_URL}')

# is the URL on your website where these collected files will be accessible. IE: mysite.com/ static/
# This is something that tells your browser where to look for JavaScript and CSS files

STATIC_ROOT = os.path.join(BASE_DIR, 'static_root/')
logger.info(f'[settings.py] STATIC_ROOT set to {STATIC_ROOT}')

# This is destination directory for your static files. This should be absolute path in yor file system,
# for example: "/var/www/project/static" If you run 'python manage.py collectstatic' it will collect all
# static files from your project and copy them into STATIC_ROOT dir

MEDIA_URL = '/MEDIA_URL/'
logger.info(f'[settings.py] MEDIA_URL set to {MEDIA_URL}')

# URL that handles the media served from MEDIA_ROOT, used for managing stored files. It must end in a slash
# if set to a non-empty value. You will need to configure these
# files to be served in both development and production environments.


MEDIA_ROOT = os.path.join(BASE_DIR, 'media_root/')
logger.info(f'[settings.py] MEDIA_ROOT set to {MEDIA_ROOT}')

# Absolute filesystem path to the directory that will hold user-uploaded files.


FILE_FORM_MASTER_DIR = 'form_uploads/form_uploads/'
FILE_FORM_UPLOAD_DIR = FILE_FORM_MASTER_DIR+'temporary_files/'  # temporary files from form upload go here
DJANGO_MAILBOX_ATTACHMENT_UPLOAD_TO = 'mailbox_attachments/%Y/%m/%d/'  # will be placed under the MEDIA_ROOT folder
logger.info(f'[settings.py] FILE_FORM_MASTER_DIR set to {FILE_FORM_MASTER_DIR}')
logger.info(f'[settings.py] FILE_FORM_UPLOAD_DIR set to {FILE_FORM_UPLOAD_DIR}')
logger.info(f'[settings.py] DJANGO_MAILBOX_ATTACHMENT_UPLOAD_TO set to {DJANGO_MAILBOX_ATTACHMENT_UPLOAD_TO}')
