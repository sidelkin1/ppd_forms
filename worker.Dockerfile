FROM oraclelinux:8 as builder

RUN dnf -y module disable python36 && \
    dnf -y install python3.11-3.11.5 python3.11-pip python3.11-setuptools python3.11-wheel && \
    rm -rf /var/cache/dnf

COPY --from=ghcr.io/astral-sh/uv:0.5.1 /uv /usr/local/bin/uv

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/app/.venv \
    UV_PYTHON_PREFERENCE=system

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-install-project --no-dev --no-group web --group worker

FROM oraclelinux:8 as runtime

ARG release=19
ARG update=18

RUN dnf -y module disable python36 && \
    dnf -y install python3.11-3.11.5 && \
    dnf -y install oracle-release-el8 && \
    dnf -y install oracle-instantclient${release}.${update}-basiclite && \
    dnf -y install libreoffice-calc && \
    rm -rf /var/cache/dnf && \
    ln -s /usr/bin/python3 /usr/bin/python

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

WORKDIR /app

COPY . .

RUN chmod +x scripts/worker-start.sh
ENTRYPOINT [ "/app/scripts/worker-start.sh" ]
