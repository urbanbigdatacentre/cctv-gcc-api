import os
from pathlib import Path

# Project Paths
DJANGO_PROJ_DIR = Path(__file__).parent.parent
APP_DIR = DJANGO_PROJ_DIR.parent
STATIC_DIR = Path(os.getenv("STATIC_DIR", DJANGO_PROJ_DIR.parent / "staticfiles"))
SECRET_KEY = '@cv5wb5BH<Lh0>Xbe4ZA&5~zJ0:cITE%bMHD3f}"yIFNjG!r}?'
UPLOAD_REPORT_PIN = os.getenv("UPLOAD_REPORT_PIN", "123")
DEBUG = os.getenv("DJANGO_DEBUG", "False").lower() == "true"
ALLOWED_HOSTS = ["*"]
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"
# noinspection SpellCheckingInspection
INSTALLED_APPS = [
    "whitenoise.runserver_nostatic",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "storages",
    "corsheaders",
    "cctv_api",
    "cctv_records",
    "cctv_core",
    "django_filters",
    "drf_spectacular",
    "rest_framework",
]
SPECTACULAR_DEFAULTS = {
    # OTHER SETTINGS
    # https://drf-spectacular.readthedocs.io/en/latest/settings.html
}

REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_AUTHENTICATION_CLASSES": [],
    "DEFAULT_PAGINATION_CLASS": "cctv_api.pagination.StandardPagination",
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
    ],
    "PAGE_SIZE": 25,
}


MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # serves static files
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "cctv_core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [DJANGO_PROJ_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "cctv_core.wsgi.application"

# Database

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.getenv("SQLITE_DB_PATH", APP_DIR / "db.sqlite3"),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "en-GB"

TIME_ZONE = "UTC"
USE_I18N = False
USE_TZ = True

# IMPORTANT:
# use the x-forwarded-host header that is added by a rev proxy.
USE_X_FORWARDED_HOST = True

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
DATE_INPUT_FORMATS = [
    "%Y%m%d",
    "%Y-%m-%d",
    "%d/%m/%Y",
    "%d-%m-%Y",
]

STATIC_URL = "/static/"
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}

STATIC_ROOT = STATIC_DIR / "static"
WHITENOISE_ROOT = STATIC_DIR / "root"

# Added CORS Settings
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_METHODS = ["GET", "OPTIONS"]
