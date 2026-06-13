import os

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

_dsn = os.getenv("SENTRY_DSN")
if _dsn:
    _raw_rate = os.getenv("SENTRY_TRACES_SAMPLE_RATE")
    try:
        traces_sample_rate: float = float(_raw_rate) if _raw_rate else 1.0
    except ValueError:
        traces_sample_rate = 1.0

    sentry_sdk.init(
        dsn=_dsn,
        integrations=[DjangoIntegration()],
        traces_sample_rate=traces_sample_rate,
        send_default_pii=True,
        environment=os.getenv("SENTRY_ENVIRONMENT", "development"),
    )
