#!/bin/bash

set -e

uvicorn app.main:main --port 8000 --host 0 --factory

exec "$@"
