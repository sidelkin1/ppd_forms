#!/bin/bash

set -e

alembic upgrade head
python -m app.initial_data

exec "$@"
