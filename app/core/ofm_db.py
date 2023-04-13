from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import DeferredReflection
from sqlalchemy.orm import DeclarativeMeta, declarative_base, sessionmaker

from app.core.config import settings

Base: type[DeclarativeMeta] = declarative_base()


class Reflected(DeferredReflection):
    __abstract__ = True


engine = create_engine(settings.ofm_database_url)

SessionLocal = sessionmaker(bind=engine)


def get_session():
    with SessionLocal() as session:
        yield session
