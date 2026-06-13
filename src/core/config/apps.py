THIRD_PARTY_APPS = [
    "unfold",
    "unfold.contrib.filters",
    "unfold.contrib.forms",
    "unfold.contrib.import_export",
    "corsheaders",
    "modeltranslation",
    "rosetta",
    "rest_framework",
    "drf_spectacular",
    "django_filters",
    "django_prometheus",
    "django_celery_beat",
    # GraphQL
    "graphene_django",
    "graphene_file_upload",
    "graphql_jwt.refresh_token",
    # Storage
    "storages",
]

DEFAULT_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
]

PROJECT_APPS = [
    "apps.account",
    "apps.business",
    "apps.category",
    "apps.order",
    "apps.product",
    "apps.marketing",
    "apps.delivery",
    "apps.common",
    "apps.telegrambot",
    "apps.payments",
]

# Payment libs import project models at load time — must come AFTER project apps
PAYMENT_APPS = [
    "payme",
    "click_up",
]
