import logging

import oracledb.exceptions as oracle_exc
import sqlalchemy.exc as sqlalchemy_exc

from app.infrastructure.db.config.models.ofm import OracleSettings
from app.infrastructure.db.factories.ofm import create_engine
from app.infrastructure.db.models.ofm.base import Reflected
from app.infrastructure.db.models.ofm.unofm import setup_column_properties

logger = logging.getLogger(__name__)


def setup(settings: OracleSettings) -> bool:
    engine = None
    try:
        engine = create_engine(settings)
        Reflected.prepare(engine, views=True)
        setup_column_properties()
    except (
        oracle_exc.DatabaseError,
        sqlalchemy_exc.DatabaseError,
    ) as error:
        logger.warning(str(error))
        return False
    finally:
        if engine is not None:
            engine.dispose()
    return True
