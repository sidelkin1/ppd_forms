FROM python:3.11-slim-bookworm as builder

COPY --from=ghcr.io/astral-sh/uv:0.5.1 /uv /uv/bin/uv

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/app/.venv \
    PATH="/uv/bin:$PATH"

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-install-project --no-dev --no-group worker --group web

FROM python:3.11-slim-bookworm as docs-builder

COPY --from=ghcr.io/astral-sh/uv:0.5.1 /uv /uv/bin/uv

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/app/.venv \
    PATH="/uv/bin:$PATH"

WORKDIR /app

COPY pyproject.toml uv.lock ./
COPY docs ./docs
COPY mkdocs.yml ./

RUN uv sync --frozen --no-install-project --no-dev --no-group web --no-group worker --group docs
RUN .venv/bin/mkdocs build --clean

FROM python:3.11-slim-bookworm as runtime

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}
COPY --from=docs-builder /app/site /app/site

WORKDIR /app

COPY . .

RUN chmod +x scripts/backend-start.sh
ENTRYPOINT [ "/app/scripts/backend-start.sh" ]
