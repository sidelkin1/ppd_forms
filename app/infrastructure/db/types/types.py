from sqlalchemy import String
from sqlalchemy.orm import mapped_column
from typing_extensions import Annotated

from app.core.config.main import get_app_settings
from app.infrastructure.db.types.base import BaseType
from app.infrastructure.db.types.unify import (
    LayerMapper,
    RegexMapper,
    SplitMode,
    WellMapper,
)

settings = get_app_settings()  # FIXME avoid global variable


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
    mapper = WellMapper(unique=True, delimiter=settings.delimiter)


class LayerType(BaseType):
    mapper = LayerMapper(split=False, sort=True, delimiter=settings.delimiter)


class MultiLayerType(BaseType):
    mapper = LayerMapper(sort=True, delimiter=settings.delimiter)


class GtmType(BaseType):
    mapper = LayerMapper(split=False, delimiter=settings.delimiter)


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
gtm_type = Annotated[str, mapped_column(GtmType(20))]

# Типы без mapper
ofm_field_type = Annotated[str, mapped_column(String(50))]
ofm_well_type = Annotated[str, mapped_column(String(10))]
ofm_reservoir_type = Annotated[str, mapped_column(String(100))]
ofm_layer_type = Annotated[str, mapped_column(String(20))]
