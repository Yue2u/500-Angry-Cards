

# Use Python 3.10 image
FROM python:3.10-slim-buster

FROM python as python-build-stage

ENV POETRY_HOME /opt/poetry
RUN python3 -m venv ${POETRY_HOME}
RUN ${POETRY_HOME}/bin/pip install poetry==1.7.1

COPY pyproject.toml poetry.lock ./
RUN mkdir requirements && ${POETRY_HOME}/bin/poetry export -f requirements.txt --output requirements/prod.txt

RUN apt-get update && apt-get install --no-install-recommends -y build-essential python3-dev libpq-dev
# Create Python Dependency and Sub-Dependency Wheels.
RUN pip wheel --wheel-dir /usr/src/app/wheels  \
  -r requirements/prod.txt


# Python 'run' stage
FROM python as python-run-stage

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

ARG APP_HOME=/app

WORKDIR ${APP_HOME}

COPY . /app

# Install required system dependencies
RUN apt-get update && apt-get install --no-install-recommends --fix-missing -y \
  postgresql-client \
  git \
  unzip \
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && rm -rf /var/lib/apt/lists/*

COPY --from=python-build-stage /usr/src/app/wheels  /wheels/

# use wheels to install python dependencies
RUN pip install --no-cache-dir --no-index --find-links=/wheels/ /wheels/* \
  && rm -rf /wheels/


CMD alembic upgrade head && uvicorn app.application:fastapi_app --host "0.0.0.0" --port 8000 --proxy-headers
