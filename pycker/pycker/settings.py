from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
AUTH_USER_MODEL = "users.User"

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'INSERT YOUR SECRET KEY HERE'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    "users.apps.UsersConfig",
    "lifecycles.apps.LifecyclesConfig",
    "tickets.apps.TicketsConfig",
    "customfields.apps.CustomfieldsConfig",
    "assets.apps.AssetsConfig",
    "links.apps.LinksConfig",
    "utils.apps.UtilsConfig"
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

ROOT_URLCONF = 'pycker.urls'

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

WSGI_APPLICATION = 'pycker.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
DEFAULT_TICKET_LIFECYCLE = {
    "new": {
        "initial": True,
        "default": True,
        "next": ["open", "resolved", "rejected", "deleted"]
    },
    "stalled": {
        "next": ["open", "resolved", "rejected", "deleted"]
    },
    "open": {
        "initial": True,
        "next": ["new", "resolved", "stalled", "rejected", "deleted"]
    },
    "resolved": {
        "initial": True,
        "next": ["closed", "stalled", "rejected", "deleted"]
    },
    "closed": {
        "final": True
    },
    "rejected": {
        "next": ["open", "deleted"]
    },
    "deleted": {
        "next": ["new"]
    }
}

DEFAULT_ASSET_LIFECYCLE = {
    "new": {
        "initial": True,
        "default": True,
        "next": ["allocated", "in-use", "recycled", "stolen", "deleted"]
    },
    "allocated": {
        "initial": True,
        "next": ["in-use", "recycled", "stolen"]
    },
    "in-use": {
        "initial": True,
        "next": ["allocated", "recycled", "stolen"]
    },
    "recycled": {
        "next": ["allocated", "deleted", "in-use"]
    },
    "stolen": {
        "next": ["allocated", "deleted", "in-use"]
    },
    "deleted": {
        "next": ["new"]
    }
}
