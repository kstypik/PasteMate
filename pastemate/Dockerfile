# syntax=docker/dockerfile:1.9
FROM python:3.13 AS build

SHELL ["sh", "-exc"]

### Start Build Prep.

RUN apt-get update -qy

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# - Silence uv complaining about not being able to use hard links,
# - tell uv to byte-compile packages for faster application startups,
# - prevent uv from accidentally downloading isolated Python builds,
# - pick a Python,
# - and finally declare `/app` as the target for `uv sync`.
ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PYTHON_DOWNLOADS=never \
    UV_PYTHON=python3.13 \
    UV_PROJECT_ENVIRONMENT=/app

### End Build Prep

# Since there's no point in shipping lock files, we move them
# into a directory that is NOT copied into the runtime image.
# The trailing slash makes COPY create `/_lock/` automagically.
COPY pyproject.toml /_lock/
COPY uv.lock /_lock/

# Synchronize DEPENDENCIES without the application itself.
# This layer is cached until uv.lock or pyproject.toml change.
RUN --mount=type=cache,target=/root/.cache <<EOT
cd /_lock
uv sync --frozen
EOT

##########################################################################

# Add Node.js build stage
FROM node:22 AS node-builder

WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci

COPY assets_build/ ./

RUN mkdir -p static/js
RUN npm run build

##########################################################################

FROM python:3.13

ARG PYTHONDEVMODE

SHELL ["sh", "-exc"]

# add the application virtualenv to search path.
ENV PATH=/app/bin:$PATH

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHON_HISTORY_APPEND_DEFAULT=1
# Enable Python Development Mode
# https://docs.python.org/3/library/devmode.html
ENV PYTHONDEVMODE=${PYTHONDEVMODE}

# Don't run your app as root.
RUN <<EOT
groupadd -r app
useradd -r -d /app -g app -N app
EOT

# See <https://hynek.me/articles/docker-signals/>.
STOPSIGNAL SIGINT

RUN <<EOT
apt-get update -qy
apt-get install -qyy \
    -o APT::Install-Recommends=false \
    -o APT::Install-Suggests=false \
    gettext \
    libpcre3 \
    libxml2 \
    vim \
    netcat-openbsd

apt-get clean
rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
EOT

COPY containers/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

COPY containers/start.sh /start.sh
RUN chmod +x /start.sh

RUN mkdir -p /app/staticfiles /app/media /app/.pytest_cache && \
    chown app:app /app/staticfiles /app/media /app/.pytest_cache

COPY --chown=app:app --from=build /app /app
COPY --chown=app:app --from=node-builder /app/static /app/static-build
COPY --chown=app:app ./pyproject.toml /app/pyproject.toml
COPY --chown=app:app ./pastemate /app/pastemate

ENV PYTHONPATH="/app"

USER app
WORKDIR /app/pastemate

ENTRYPOINT ["/entrypoint.sh"]