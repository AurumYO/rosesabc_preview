import os
from pathlib import Path

# Load environment variables with environ
import environ

# Initialise environment variables
env = environ.Env()
environ.Env.read_env()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

SITE_ID = 1


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("MY_SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env("MY_ENV_DEBUG", default=False)

ALLOWED_HOSTS = ["*"]
if not DEBUG:
    ALLOWED_HOSTS += env("MY_ALLOWED_HOSTS")


# Application definition

INSTALLED_APPS = [
    "account.apps.AccountConfig",  # authentication app
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",  # sitemaps
    "django.contrib.sitemaps",  # sitemaps
    # Third party packages
    "rosetta",
    "taggit",
    "social_django",  # authentication with social apps
    "django_extensions",
    "parler",
    "easy_thumbnails",
    "embed_video",
    "django_filters",
    "rest_framework",
    # "roses.apps.RosesConfig",  # roses library app
    # "actions.apps.ActionsConfig",  # actions app
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",  # add localization middleware for internalization support
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "rosesabc.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
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

WSGI_APPLICATION = "rosesabc.wsgi.application"

from django.urls import reverse_lazy

ABSOLUTE_URL_OVERRIDES = {
    "auth.user": lambda u: reverse_lazy("user_detail", args=[u.username])
}

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql_psycopg2',
#         'NAME': env('DB_NAME'),
#         'USER': env('DB_USER'),
#         'PASSWORD': env('DB_PASSWORD'),
#         'HOST': env('DB_HOST'),
#         'PORT': env('DB_PORT'),
#     }
# }


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = "static/"

STATICFILES_DIRS = (os.path.join(BASE_DIR, "static"),)

MEDIA_URL = "/media/"

MEDIA_ROOT = os.path.join(BASE_DIR, "media/")


# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


from django.utils.translation import gettext_lazy as _

LANGUAGE_CODE = "en"
TIME_ZONE = "UTC"
USE_I18N = True
USE_L10N = True
USE_TZ = True
LANGUAGES = (
    ("en", _("English")),
    ("uk", _("Ukrainian")),
)
LOCALE_PATHS = [
    os.path.join(BASE_DIR, "locale/"),
]

# Authentication settings
LOGIN_REDIRECT_URL = "dashboard"
LOGIN_URL = "login"
LOGOUT_URL = "logout"
ACCOUNT_SESSION_REMEMBER = True

# Authentication with social apps settings
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "account.authentication.EmailAuthBackend",
    "social_core.backends.google.GoogleOAuth2",  # uncomment on production
]

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = env(
    "MY_SOCIAL_AUTH_GOOGLE_OAUTH2_KEY"
)  # Google Consumer Key
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = env(
    "MY_SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET"
)  # Google Consumer Secret


# Email backend settings
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_HOST_USER = env("MY_EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = env("MY_EMAIL_HOST_PASSWORD")
EMAIL_PORT = 587
EMAIL_USE_TLS = True


# Django-parler translations settings
PARLER_LANGUAGES = {
    1: (
        {
            "code": "en",
        },
        {
            "code": "uk",
        },
    ),
    "default": {
        "fallback": "en",  # defaults to PARLER_DEFAULT_LANGUAGE_CODE
        "hide_untranslated": False,  # the default; let .active_translations() return fallbacks too.
    },
}
PARLER_DEFAULT_LANGUAGE_CODE = "en"


# # Redis settings
# REDIS_HOST = "localhost"
# REDIS_PORT = 6379
# REDIS_DB = 0


# REST configuration
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.BasicAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 25,
    "ORDERING_PARAM": "ordering",
}
