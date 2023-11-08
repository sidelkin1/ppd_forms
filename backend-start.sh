#!/bin/bash
set -e

alembic upgrade head
python -m app.initial_data
uvicorn app.main:main --port 8000 --host 0 --factory

exec "$@"
