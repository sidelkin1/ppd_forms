from app.infrastructure.db.mappers import (
    multi_reservoir_mapper,
    multi_split_reservoir_mapper,
    reservoir_mapper,
)
from app.infrastructure.db.types.base import BaseType


class ResevoirType(BaseType):
    def process_bind_param(self, value, dialect):
        return reservoir_mapper[value]


class MultiResevoirType(BaseType):
    def process_bind_param(self, value, dialect):
        return multi_reservoir_mapper[value]


class MultiSplitResevoirType(BaseType):
    def process_bind_param(self, value, dialect):
        return multi_split_reservoir_mapper[value]
