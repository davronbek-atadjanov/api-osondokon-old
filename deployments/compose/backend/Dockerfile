# syntax=docker/dockerfile:1.2
ARG PYTHON_VERSION=3.12
ARG UV_VERSION=0.7.2

FROM ghcr.io/astral-sh/uv:${UV_VERSION} AS uv

FROM python:${PYTHON_VERSION} AS builder
COPY --from=uv /uv /uvx /bin/

ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PYTHON_DOWNLOADS=never \
    PYTHONUNBUFFERED=1 \
    UV_PROJECT_ENVIRONMENT=/opt/venv

WORKDIR /app

COPY ./pyproject.toml ./uv.lock* ./

RUN uv sync --no-dev --frozen --no-install-project --all-groups

FROM python:${PYTHON_VERSION} AS app

WORKDIR /app

# libmagic required by python-magic (used in GraphQL file upload mutations)
RUN apt-get update && apt-get install -y --no-install-recommends libmagic1 && rm -rf /var/lib/apt/lists/*

ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    VIRTUAL_ENV=/opt/venv \
    PATH=/opt/venv/bin:$PATH

COPY ./deployments/compose/backend/celery/worker/start /start-celeryworker
RUN sed -i 's/\r$//g' /start-celeryworker && chmod +x /start-celeryworker

COPY ./deployments/compose/backend/celery/beat/start /start-celerybeat
RUN sed -i 's/\r$//g' /start-celerybeat && chmod +x /start-celerybeat

COPY ./deployments/compose/backend/celery/flower/start /start-flower
RUN sed -i 's/\r$//g' /start-flower && chmod +x /start-flower

COPY ./deployments/compose/backend/entrypoint /entrypoint
RUN sed -i 's/\r$//g' /entrypoint && chmod +x /entrypoint

COPY ./deployments/compose/backend/start /start
RUN sed -i 's/\r$//g' /start && chmod +x /start

COPY --from=builder /opt/venv /opt/venv
COPY ./pyproject.toml ./

# click_up/models.py imports project models at module load time — remove unused eager import
RUN sed -i '/^from django\.conf import settings/d; /^from django\.utils\.module_loading import import_string/d; /^AccountModel = import_string/d' \
    /opt/venv/lib/python3.12/site-packages/click_up/models.py

# src/ contents are copied to /app (PYTHONPATH=/app so imports work)
COPY src/. /app/

RUN chgrp -R 0 /app && chmod -R g=u /app

ENTRYPOINT ["/entrypoint"]
