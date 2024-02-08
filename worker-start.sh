#!/bin/bash

python -m app.ofm_pre_start

set -e

alembic upgrade head
python -m app.initial_data
arq app.worker.WorkerSettings

exec "$@"
