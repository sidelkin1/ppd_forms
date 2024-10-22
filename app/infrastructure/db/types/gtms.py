from app.core.config.main import get_app_settings
from app.infrastructure.db.mappers import gtm_mapper
from app.infrastructure.db.types.base import BaseType

settings = get_app_settings()  # FIXME avoid global variable


class GtmType(BaseType):
    def process_bind_param(self, value, dialect):
        return gtm_mapper[value]
