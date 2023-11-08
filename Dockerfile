FROM python:3.11-slim-bookworm as builder

RUN pip install --no-cache-dir poetry==1.6.1

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN poetry install --without dev --no-root && rm -rf $POETRY_CACHE_DIR

# Used own image due to error 'Request has been forbidden by antivirus'
# FROM python:3.11-slim-bookworm as runtime

# RUN apt-get update && \
#     apt-get install -y curl

FROM sidelkin/python311-slim-bookworm-curl:latest

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

WORKDIR /app

COPY . .

RUN chmod +x backend-start.sh
ENTRYPOINT [ "/app/backend-start.sh" ]
