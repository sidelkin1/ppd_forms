from sqlalchemy import Column, Integer
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import (DeclarativeMeta, declarative_base, declared_attr,
                            sessionmaker)
from sqlalchemy.schema import Constraint

from app.core.config import settings


class PreBase:

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id = Column(Integer, primary_key=True)

    @classmethod
    def get_constraint_by_name(cls, name: str) -> Constraint:
        return next(
            (constraint for constraint in cls.__table__.constraints
             if constraint.name == name)
        )


Base: type[DeclarativeMeta] = declarative_base(cls=PreBase)

engine = create_async_engine(settings.local_database_url)

AsyncSessionLocal = sessionmaker(bind=engine, class_=AsyncSession)


async def get_async_session():
    async with AsyncSessionLocal() as async_session:
        yield async_session
