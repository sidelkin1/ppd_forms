from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.initial_data import init_mapper


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_mapper()
    yield
