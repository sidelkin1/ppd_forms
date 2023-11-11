#!/bin/bash

python -m app.ofm_pre_start
arq app.worker.WorkerSettings

exec "$@"
