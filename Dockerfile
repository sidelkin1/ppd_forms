FROM python:3.11-slim-bookworm as builder

RUN pip install --no-cache-dir poetry==1.6.1

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache \
    PIP_OPTIONS="--proxy $HTTP_PROXY"


WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN poetry install --with web --no-root && rm -rf $POETRY_CACHE_DIR

FROM python:3.11-slim-bookworm as runtime

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

WORKDIR /app

COPY . .

RUN chmod +x scripts/backend-start.sh
ENTRYPOINT [ "/app/scripts/backend-start.sh" ]
