from concurrent.futures.process import ProcessPoolExecutor
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import settings
from app.initial_data import init_mapper


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_mapper()
    with ProcessPoolExecutor(max_workers=settings.max_workers) as pool:
        app.state.pool_executor = pool
        yield
