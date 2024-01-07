from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.dependencies.dao.provider import DbProvider
from app.infrastructure.db.factories.local import create_pool
from app.initial_data import initialize_mapper


@asynccontextmanager
async def lifespan(app: FastAPI):
    pool = create_pool(app.state.settings)
    provider = DbProvider(local_pool=pool)
    await initialize_mapper(provider)
    yield
