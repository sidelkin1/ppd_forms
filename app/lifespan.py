from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.dependencies.dao.provider import DbProvider
from app.initial_data import initialize_mapper


@asynccontextmanager
async def lifespan(app: FastAPI):
    provider = DbProvider(local_pool=app.state.pool)
    await initialize_mapper(provider)
    yield
