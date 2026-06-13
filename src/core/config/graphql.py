import os
from datetime import timedelta

GRAPHENE = {
    "MIDDLEWARE": [
        "graphql_jwt.middleware.JSONWebTokenMiddleware",
        "apps.common.middleware.TrafficMiddleware",
    ],
}

AUTHENTICATION_BACKENDS = [
    "graphql_jwt.backends.JSONWebTokenBackend",
    "django.contrib.auth.backends.ModelBackend",
]

GRAPHQL_JWT = {
    "JWT_PAYLOAD_HANDLER": "core.utils.jwt_payload",
    "JWT_PAYLOAD_GET_USERNAME_HANDLER": lambda payload: payload.get("user_id"),
    "JWT_GET_USER_BY_NATURAL_KEY_HANDLER": "core.utils.get_user_by_natural_key",
    "JWT_VERIFY_EXPIRATION": True,
    "JWT_EXPIRATION_DELTA": timedelta(days=15),
    "JWT_REFRESH_EXPIRATION_DELTA": timedelta(days=7),
    "JWT_SECRET_KEY": os.getenv("SECRET_KEY", ""),
    "JWT_ALGORITHM": "HS256",
    "JWT_AUTH_HEADER_PREFIX": "Bearer",
    "JWT_ALLOW_REFRESH": True,
}
