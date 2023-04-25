from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import (DeclarativeBase, Mapped, declared_attr,
                            mapped_column)
from sqlalchemy.schema import Constraint

from app.core.config import settings


class Base(DeclarativeBase):

    @declared_attr.directive
    def __tablename__(cls):
        return f'{cls.__name__.lower()}'

    id: Mapped[int] = mapped_column(primary_key=True)

    @classmethod
    def get_constraint_by_name(cls, name: str) -> Constraint:
        return next(
            (constraint for constraint in cls.__table__.constraints
             if constraint.name == name)
        )


engine = create_async_engine(settings.local_database_url)

AsyncSessionLocal = async_sessionmaker(engine)


async def get_async_session():
    async with AsyncSessionLocal() as async_session:
        yield async_session
