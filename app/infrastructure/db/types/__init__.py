from sqlalchemy import String
from sqlalchemy.orm import mapped_column
from typing_extensions import Annotated

from .base import BaseType
from .fields import FieldType
from .gtms import GtmType
from .layers import LayerType, MultiLayerType, WellTestMultiLayerType
from .reservoirs import MultiResevoirType, MultiSplitResevoirType, ResevoirType
from .wells import MultiWellType, WellType

# Типы с mapper
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
well_test_multi_layer_type = Annotated[
    str, mapped_column(WellTestMultiLayerType(100))
]
gtm_type = Annotated[str, mapped_column(GtmType(20))]

# Типы без mapper
ofm_field_type = Annotated[str, mapped_column(String(50))]
ofm_well_type = Annotated[str, mapped_column(String(10))]
ofm_reservoir_type = Annotated[str, mapped_column(String(100))]
ofm_layer_type = Annotated[str, mapped_column(String(20))]
