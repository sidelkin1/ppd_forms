from sqlalchemy import Engine
from sqlalchemy import create_engine as create_sync_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config.settings import Settings


def create_pool(settings: Settings) -> sessionmaker[Session]:
    engine = create_engine(settings)
    return create_session_maker(engine)


def create_engine(settings: Settings) -> Engine:
    return create_sync_engine(str(settings.ofm_database_url), thick_mode=True)


def create_session_maker(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(engine)
