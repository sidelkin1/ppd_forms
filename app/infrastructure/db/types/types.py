from sqlalchemy.orm import mapped_column
from typing_extensions import Annotated

from app.core.config.settings import get_settings
from app.infrastructure.db.types.base import BaseType
from app.infrastructure.db.types.unify.base_mapper import SplitMode
from app.infrastructure.db.types.unify.layer_mapper import LayerMapper
from app.infrastructure.db.types.unify.regex_mapper import RegexMapper
from app.infrastructure.db.types.unify.well_mapper import WellMapper

settings = get_settings()  # FIXME avoid global variable


class FieldType(BaseType):
    mapper = RegexMapper(split=False, delimiter=settings.delimiter)


class ResevoirType(BaseType):
    mapper = RegexMapper(
        split=False, sort=True, unique=True, delimiter=settings.delimiter
    )


class MultiResevoirType(BaseType):
    mapper = RegexMapper(sort=True, unique=True, delimiter=settings.delimiter)


class MultiSplitResevoirType(BaseType):
    mapper = RegexMapper(
        sort=True,
        unique=True,
        delimiter=settings.delimiter,
        split_mode=SplitMode.split_in,
    )


class WellType(BaseType):
    mapper = WellMapper(split=False, delimiter=settings.delimiter)


class MultiWellType(BaseType):
    mapper = WellMapper(delimiter=settings.delimiter)


class LayerType(BaseType):
    mapper = LayerMapper(split=False, sort=True, delimiter=settings.delimiter)


class MultiLayerType(BaseType):
    mapper = LayerMapper(sort=True, delimiter=settings.delimiter)


field_type = Annotated[str, mapped_column(FieldType(50))]
well_type = Annotated[str, mapped_column(WellType(10))]
multi_well_type = Annotated[str, mapped_column(MultiWellType(100))]
reservoir_type = Annotated[str, mapped_column(ResevoirType(100))]
multi_reservoir_type = Annotated[str, mapped_column(MultiResevoirType(200))]
multi_split_reservoir_type = Annotated[
    str, mapped_column(MultiSplitResevoirType(200))
]
layer_type = Annotated[str, mapped_column(LayerType(20))]
multi_layer_type = Annotated[str, mapped_column(MultiLayerType(100))]
