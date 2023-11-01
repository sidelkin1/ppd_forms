#!/bin/bash

poetry run task migrate
poetry run task initialize
# poetry run task uvicorn

exec "$@"
