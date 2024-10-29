from app.infrastructure.db.mappers import gtm_mapper
from app.infrastructure.db.types.base import BaseType


class GtmType(BaseType):
    def process_bind_param(self, value, dialect):
        return gtm_mapper[value]
