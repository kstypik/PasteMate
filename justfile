set dotenv-load := false

@_default:
    just --list

# Format the justfile
@fmt:
    just --fmt --unstable

# Builds the Docker Images with no optional arguments
@cibuild:
    just build

# Builds the Docker Images with optional arguments
@build *ARGS:
    docker compose {{ ARGS }} build

# --------------------------------------------------
# Docker recipes
# --------------------------------------------------

# Bring down your docker containers
@down *ARGS:
    docker compose down {{ ARGS }}

# Allows you to view the output from running containers
@logs *ARGS:
    docker compose logs {{ ARGS }}

# Restart all services
@restart *ARGS:
    docker compose restart {{ ARGS }}

@recreate *ARGS:
    docker compose down {{ ARGS }}
    docker compose build
    docker compose up -d

# Start all services
@start *ARGS="--detach":
    docker compose up {{ ARGS }}

@status:
    docker compose ps

# Stop all services
@stop:
    docker compose down

# Tail service logs
@tail:
    just logs --follow

# Bring up your Docker Containers
@up *ARGS:
    docker compose up {{ ARGS }}

# Django recipes
# --------------------------------------------------

# Drop into the console on the docker image
@console:
    docker compose run --rm pastemate /bin/bash

@manage *ARGS:
    docker compose run --rm pastemate python manage.py {{ ARGS }}

@makemigrations *ARGS:
    just manage makemigrations {{ ARGS }}

@migrate *ARGS:
    just manage migrate {{ ARGS }}

@showmigrations *ARGS:
    just manage showmigrations {{ ARGS }}

# Run the shell management command
@shell *ARGS:
    just manage shell {{ ARGS }}

# Create a Superuser
@createsuperuser USERNAME EMAIL:
    just manage createsuperuser \
        --username={{ USERNAME }} \
        --email={{ EMAIL }}

@uvsync:
    uv sync

@pytest *ARGS:
    docker compose run --rm pastemate pytest {{ ARGS }}

@ruff *ARGS:
    ruff check {{ ARGS }}

@mypy *ARGS:
    docker compose run --rm pastemate mypy {{ ARGS }}