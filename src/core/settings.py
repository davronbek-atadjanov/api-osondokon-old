import os
import sys
from pathlib import Path

from dotenv import load_dotenv, find_dotenv

# Must load .env BEFORE importing core.config — importing core.config.apps
# triggers core/config/__init__.py which reads os.getenv() in payments.py etc.
load_dotenv(find_dotenv(".env"))

from django.utils.translation import gettext_lazy as _
from core.config.apps import DEFAULT_APPS, PAYMENT_APPS, PROJECT_APPS, THIRD_PARTY_APPS
from core.config import *  # noqa: E402, F403

BASE_DIR = Path(__file__).resolve().parent.parent.parent


def env_bool(name: str, default: bool = False) -> bool:
    val = os.getenv(name)
    if val is None:
        return default
    return val.strip().lower() in {"1", "true", "yes", "on"}


SECRET_KEY: str = os.getenv("SECRET_KEY", "")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable is required")

DEBUG: bool = env_bool("DEBUG", False)

ALLOWED_HOSTS: list[str] = [
    "127.0.0.1",
    "localhost",
    "api.osondokon.uz",
    *[h for h in os.getenv("ALLOWED_HOSTS", "").split(",") if h.strip()],
]

CSRF_TRUSTED_ORIGINS: list[str] = [
    "http://127.0.0.1",
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:5173",
    "https://www.osondokon.uz",
    "https://osondokon.uz",
    "https://api.osondokon.uz",
    "https://app.osondokon.uz",
    "https://crm-oson.vercel.app",
]

INSTALLED_APPS = [*THIRD_PARTY_APPS, *DEFAULT_APPS, *PROJECT_APPS, *PAYMENT_APPS]

MIDDLEWARE = [
    "django_prometheus.middleware.PrometheusBeforeMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_prometheus.middleware.PrometheusAfterMiddleware",
]

ROOT_URLCONF = "core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "assets/templates")],
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

WSGI_APPLICATION = "core.wsgi.application"
ASGI_APPLICATION = "core.asgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB"),
        "USER": os.getenv("POSTGRES_USER"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD"),
        "HOST": os.getenv("POSTGRES_HOST"),
        "PORT": os.getenv("POSTGRES_PORT", "5432"),
    }
}

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.Argon2PasswordHasher",
]

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

AUTH_USER_MODEL = "account.User"

LANGUAGE_CODE = "uz"
TIME_ZONE = "Asia/Tashkent"
USE_I18N = True
USE_TZ = True
SITE_ID = 1

LANGUAGES = (
    ("en", _("English")),
    ("uz", _("Uzbek")),
    ("ru", _("Russian")),
)

LOCALE_PATHS = [os.path.join(BASE_DIR, "assets/locale")]

MODELTRANSLATION_LANGUAGES = ("uz", "ru", "en")
MODELTRANSLATION_DEFAULT_LANGUAGE = "uz"
MODELTRANSLATION_PREPOPULATE_LANGUAGE = "uz"
MODELTRANSLATION_FALLBACK_LANGUAGES = ("uz", "ru", "en")

STATIC_URL = "/static/"
STATICFILES_DIRS = [str(BASE_DIR / "assets" / "static")]
STATIC_ROOT = str(BASE_DIR / "assets" / "staticfiles")

MEDIA_URL = "/media/"
MEDIA_ROOT = str(BASE_DIR / "assets" / "media")

STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS: list[str] = [
    "http://127.0.0.1:3000",
    "http://localhost:3000",
    "http://localhost:5173",
    "https://www.osondokon.uz",
    "https://osondokon.uz",
    "https://www.osonstore.uz",
    "https://app.osondokon.uz",
    "https://oson-store.vercel.app",
    "https://crm-oson.vercel.app",
]
CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^https:\/\/([a-zA-Z0-9_-]+\.)?osonstore\.uz$",
]
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = ["DELETE", "GET", "OPTIONS", "PATCH", "POST", "PUT"]
CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "origin",
    "user-agent",
    "apollo-require-preflight",
    "content-disposition",
    "x-csrftoken",
    "x-requested-with",
]

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv("SMTP_EMAIL", "")
EMAIL_HOST_PASSWORD = os.getenv("SMTP_PASSWORD", "")

SMS_API_URL = os.getenv("SMS_API_URL", "")
SMS_API_UNIQUE_ID = os.getenv("SMS_API_UNIQUE_ID", "")
ESKIZ_UZ_EMAIL = os.getenv("ESKIZ_UZ_EMAIL", "")
ESKIZ_UZ_PASSWORD = os.getenv("ESKIZ_UZ_PASSWORD", "")

DOMAIN_NAME = os.getenv("DOMAIN_NAME", ".osondokon.uz")
OTP_EXPIRE_TIME = int(os.getenv("OTP_EXPIRE_TIME", 5))

SERVER_IP = os.getenv("SERVER_IP", "")
SERVER_DOMAIN = os.getenv("SERVER_DOMAIN", "")
HOST = os.getenv("HOST", "")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")

VERCEL_API_KEY = os.getenv("VERCEL_API_KEY", "")
VERCEL_PROJECT_ID = os.getenv("VERCEL_PROJECT_ID", "")

RUNNING_MIGRATIONS = "makemigrations" in sys.argv or "migrate" in sys.argv or "showmigrations" in sys.argv

X_FRAME_OPTIONS = "SAMEORIGIN"
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True

if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    X_FRAME_OPTIONS = "DENY"
