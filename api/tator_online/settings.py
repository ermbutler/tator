"""
Django settings for tator_online project.

Generated by 'django-admin startproject' using Django 2.1.2.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os
from django.contrib.messages import constants as messages
import yaml
import sys

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")
DEBUG = False

MAIN_HOST = os.getenv("MAIN_HOST")
ALLOWED_HOSTS = [MAIN_HOST, "gunicorn-headless-svc", "gunicorn-svc", "gunicorn"]
ALIAS_HOSTS = os.getenv("ALIAS_HOSTS")
if ALIAS_HOSTS:
    ALLOWED_HOSTS += ALIAS_HOSTS.split(",")

# Whether keycloak is being used for authentication
KEYCLOAK_ENABLED = os.getenv("KEYCLOAK_ENABLED") == "TRUE"

STATSD_ENABLED = os.getenv("STATSD_ENABLED", "TRUE") == "TRUE"

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.gis",
    "main",
    "django_saml2_auth",
    "rest_framework",
    "rest_framework.authtoken",
    "django_extensions",
    "django_admin_json_editor",
    "django_ltree",
    "pgtrigger",
]

GRAPH_MODELS = {
    "all_applications": True,
    "group_models": True,
}

LOGIN_URL = "/accounts/login/"
LOGIN_REDIRECT_URL = "/projects"
LOGOUT_REDIRECT_URL = "/accounts/login/"
AUTH_USER_MODEL = "main.User"

MESSAGE_TAGS = {
    messages.DEBUG: "alert-info",
    messages.INFO: "alert-info",
    messages.SUCCESS: "alert-success",
    messages.WARNING: "alert-warning",
    messages.ERROR: "alert-danger",
}

MIDDLEWARE = (
    [
        "django.middleware.security.SecurityMiddleware",
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.middleware.common.CommonMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
    ]
    + (
        [
            "tator_online.KeycloakMiddleware",
        ]
        if KEYCLOAK_ENABLED
        else [
            "django.middleware.csrf.CsrfViewMiddleware",
        ]
    )
    + [
        "django.contrib.messages.middleware.MessageMiddleware",
        "django.middleware.clickjacking.XFrameOptionsMiddleware",
    ]
)

ROOT_URLCONF = "tator_online.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "main/templates")],
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

WSGI_APPLICATION = "tator_online.wsgi.application"


# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

if DEBUG:
    DATABASES = {
        "default": {
            "ENGINE": "django.contrib.gis.db.backends.postgis",
            "NAME": "tator_online",
            "USER": os.getenv("POSTGRES_USER"),
            "PASSWORD": os.getenv("POSTGRES_PASSWORD"),
            "HOST": os.getenv("POSTGRES_HOST"),
            "PORT": os.getenv("POSTGRES_PORT", 5432),
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.contrib.gis.db.backends.postgis",
            "NAME": "tator_online",
            "USER": os.getenv("POSTGRES_USER"),
            "PASSWORD": os.getenv("POSTGRES_PASSWORD"),
            "HOST": os.getenv("POSTGRES_HOST"),
            "PORT": os.getenv("POSTGRES_PORT", 5432),
        }
    }


# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "EST"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = "/static"

MEDIA_URL = "/media/"
MEDIA_ROOT = "/media"

RAW_ROOT = "/data/raw"

ASGI_APPLICATION = "tator_online.routing.application"


# Turn on logging
if os.getenv("DD_LOGS_INJECTION"):
    import ddtrace.auto
    FORMAT = (
        "%(asctime)s %(levelname)s [%(name)s] [%(filename)s:%(lineno)d] "
        "[dd.service=%(dd.service)s dd.env=%(dd.env)s "
        "dd.version=%(dd.version)s "
        "dd.trace_id=%(dd.trace_id)s dd.span_id=%(dd.span_id)s] "
        "- %(message)s"
    )
else:
    FORMAT = "%(asctime)s %(levelname)s [%(name)s] [%(filename)s:%(lineno)d] " "- %(message)s"
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": FORMAT,
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "loggers": {
        "ddtrace": {
            "handlers": ["console"],
            "level": "INFO",
        },
        "django": {
            "handlers": ["console"],
            "level": "INFO",
        },
        "main": {
            "handlers": ["console"],
            "level": "INFO",
        },
    },
}

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.TokenAuthentication",
        "tator_online.authentication.KeycloakAuthentication",
    )
    if KEYCLOAK_ENABLED
    else (
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.TokenAuthentication",
    ),
    "DEFAULT_RENDERER_CLASSES": (
        "main.renderers.TatorRenderer",
        "main.renderers.CsvRenderer",
        "main.renderers.PprintRenderer",
    ),
    "DEFAULT_SCHEMA_CLASS": "rest_framework.schemas.openapi.AutoSchema",
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "main.throttles.BurstableThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "10/second",
    },
    "TEST_REQUEST_RENDERER_CLASSES": [
        "main.renderers.TatorRenderer",
    ],
}

AUTHENTICATION_BACKENDS = ["main.auth.TatorAuth"]
REQUIRE_HTTPS = os.getenv("REQUIRE_HTTPS") == "TRUE"
if REQUIRE_HTTPS:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

TATOR_SLACK_TOKEN = os.getenv("TATOR_SLACK_TOKEN")
TATOR_SLACK_CHANNEL = os.getenv("TATOR_SLACK_CHANNEL")

TATOR_EMAIL_ENABLED = os.getenv("TATOR_EMAIL_ENABLED")
if TATOR_EMAIL_ENABLED is not None:
    TATOR_EMAIL_ENABLED = TATOR_EMAIL_ENABLED.lower() == "true"
else:
    TATOR_EMAIL_ENABLED = False

if TATOR_EMAIL_ENABLED:
    TATOR_EMAIL_SENDER = os.getenv("TATOR_EMAIL_SENDER")
    TATOR_EMAIL_SERVICE = os.getenv("TATOR_EMAIL_SERVICE")

    if TATOR_EMAIL_SERVICE == "AWS":
        TATOR_EMAIL_AWS_REGION = os.getenv("TATOR_EMAIL_AWS_REGION")
        TATOR_EMAIL_AWS_ACCESS_KEY_ID = os.getenv("TATOR_EMAIL_AWS_ACCESS_KEY_ID")
        TATOR_EMAIL_AWS_SECRET_ACCESS_KEY = os.getenv("TATOR_EMAIL_AWS_SECRET_ACCESS_KEY")
    # TODO Add `elif TATOR_EMAIL_SERVICE == "OCI":` case when OCI integration is complete

    TATOR_EMAIL_NOTIFY_STAFF = os.getenv("TATOR_EMAIL_NOTIFY_STAFF")
    if TATOR_EMAIL_NOTIFY_STAFF:
        TATOR_EMAIL_NOTIFY_STAFF = TATOR_EMAIL_NOTIFY_STAFF.lower() == "true"
    else:
        TATOR_EMAIL_NOTIFY_STAFF = False

ANONYMOUS_REGISTRATION_ENABLED = os.getenv("ANONYMOUS_REGISTRATION_ENABLED")
if ANONYMOUS_REGISTRATION_ENABLED is not None:
    ANONYMOUS_REGISTRATION_ENABLED = ANONYMOUS_REGISTRATION_ENABLED.lower() == "true"
if ANONYMOUS_REGISTRATION_ENABLED:
    EMAIL_CONFIRMATION_REQUIRED = os.getenv("EMAIL_CONFIRMATION")
    if EMAIL_CONFIRMATION_REQUIRED is not None:
        EMAIL_CONFIRMATION_REQUIRED = EMAIL_CONFIRMATION_REQUIRED.lower() == "true"

ANONYMOUS_GATEWAY_ENABLED = os.getenv("ANONYMOUS_GATEWAY_ENABLED")
if ANONYMOUS_GATEWAY_ENABLED is not None:
    ANONYMOUS_GATEWAY_ENABLED = ANONYMOUS_GATEWAY_ENABLED.lower() == "true"

SILENCED_SYSTEM_CHECKS = ["fields.W342"]

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

# Cognito configuration
COGNITO_ENABLED = os.getenv("COGNITO_ENABLED")
COGNITO_ENABLED = (
    COGNITO_ENABLED
    and COGNITO_ENABLED.lower() == "true"
    and os.path.exists("/cognito/cognito.yaml")
)

if COGNITO_ENABLED:
    with open("/cognito/cognito.yaml", "r") as cfile:
        data = yaml.safe_load(cfile)

    REST_FRAMEWORK["DEFAULT_AUTHENTICATION_CLASSES"] = (
        *REST_FRAMEWORK["DEFAULT_AUTHENTICATION_CLASSES"],
        "django_cognito_jwt.JSONWebTokenAuthentication",
    )

    COGNITO_AWS_REGION = data["aws-region"]
    COGNITO_USER_POOL = data["pool-id"]
    COGNITO_AUDIENCE = data["client-id"]
    COGNITO_DOMAIN = f"{data['domain-prefix']}.auth.{data['aws-region']}.amazoncognito.com"
    COGNITO_USER_MODEL = "main.User"

# Okta configuration
OKTA_ENABLED = os.getenv("OKTA_ENABLED")
OKTA_ENABLED = OKTA_ENABLED and OKTA_ENABLED.lower() == "true"

if OKTA_ENABLED:
    OKTA_OAUTH2_KEY = os.getenv("OKTA_OAUTH2_KEY")
    OKTA_OAUTH2_SECRET = os.getenv("OKTA_OAUTH2_SECRET")
    OKTA_OAUTH2_TOKEN_URI = os.getenv("OKTA_OAUTH2_TOKEN_URI")
    OKTA_OAUTH2_USERINFO_URI = os.getenv("OKTA_OAUTH2_USERINFO_URI")
    OKTA_OAUTH2_ISSUER = os.getenv("OKTA_OAUTH2_ISSUER")
    OKTA_OAUTH2_AUTH_URI = os.getenv("OKTA_OAUTH2_AUTH_URI")

SAML_ENABLED = os.getenv("SAML_ENABLED")
SAML_ENABLED = SAML_ENABLED and SAML_ENABLED.lower() == "true"
PROTO = "https" if REQUIRE_HTTPS else "http"

if SAML_ENABLED:
    SAML2_AUTH = {
        "METADATA_AUTO_CONF_URL": os.getenv("SAML_METADATA_URL"),
        "DEFAULT_NEXT_URL": LOGIN_REDIRECT_URL,
        "CREATE_USER": True,
        "NEW_USER_PROFILE": {
            "USER_GROUPS": [],
            "ACTIVE_STATUS": True,
            "STAFF_STATUS": False,
            "SUPERUSER_STATUS": False,
        },
        "ENTITY_ID": f"{PROTO}://{MAIN_HOST}/saml2_auth/acs/",
        "TOKEN_REQUIRED": False,
    }

    SAML_SSO_URL = os.getenv("SAML_SSO_URL")
