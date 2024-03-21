#!/bin/bash

python -m app.ofm_pre_start

set -e

arq app.worker.WorkerSettings

exec "$@"
