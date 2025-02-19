from app.infrastructure.db.mappers import (
    layer_mapper,
    multi_layer_mapper,
    well_test_multi_layer_mapper,
)
from app.infrastructure.db.types.base import BaseType


class LayerType(BaseType):
    def process_bind_param(self, value, dialect):
        return layer_mapper[value]


class MultiLayerType(BaseType):
    def process_bind_param(self, value, dialect):
        return multi_layer_mapper[value]


class WellTestMultiLayerType(BaseType):
    def process_bind_param(self, value, dialect):
        return well_test_multi_layer_mapper[value] or None
