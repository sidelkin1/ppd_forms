from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware

from .context import RequestIDMiddleware
from .structlog import StructlogMiddleware


def setup(app: FastAPI) -> None:
    app.add_middleware(StructlogMiddleware)
    app.add_middleware(RequestIDMiddleware)
