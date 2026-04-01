"""
Django settings for sidecar_c project.
"""

from pathlib import Path

#  LOGGING 
from sidecar_c.logging_config import setup_logging
from sidecar_c.logging_context import ContextFilter

logger = setup_logging()
for handler in logger.handlers:
    handler.addFilter(ContextFilter())


#  Base dir
BASE_DIR = Path(__file__).resolve().parent.parent


#  Segurança
SECRET_KEY = 'django-insecure-3k&gmui&8!vqba2k-=bdwr7yx#zjavlfn8&$me75^cs!tty-ob'
DEBUG = True
ALLOWED_HOSTS = ["*"]


#  Apps
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'proxy'
]


#  Middleware 
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',

    'sidecar_c.middleware.RequestIDMiddleware',
    'sidecar_c.middleware.LoggingContextMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


#  URLs / WSGI
ROOT_URLCONF = 'sidecar_c.urls'
WSGI_APPLICATION = 'sidecar_c.wsgi.application'


#  Templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


#  Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


#  Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


#  Internacionalização
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


#  Static
STATIC_URL = 'static/'
