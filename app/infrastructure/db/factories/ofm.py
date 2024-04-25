from sqlalchemy import Engine
from sqlalchemy import create_engine as create_sync_engine
from sqlalchemy.orm import Session, sessionmaker

from app.infrastructure.db.config.models.ofm import OracleSettings


def create_pool(settings: OracleSettings) -> sessionmaker[Session]:
    engine = create_engine(settings)
    return create_session_maker(engine)


def create_engine(settings: OracleSettings) -> Engine:
    return create_sync_engine(
        str(settings.url), thick_mode=True, coerce_to_decimal=False
    )


def create_session_maker(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(engine)
