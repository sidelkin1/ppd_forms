FROM oraclelinux:8 as builder

RUN dnf -y module disable python36 && \
    dnf -y install python3.11-3.11.5 python3.11-pip python3.11-setuptools python3.11-wheel && \
    rm -rf /var/cache/dnf

RUN pip3 install poetry==1.6.1

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN poetry install --with worker --no-root && rm -rf $POETRY_CACHE_DIR

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
