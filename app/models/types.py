import sqlalchemy.types as types
from sqlalchemy.orm import mapped_column
from typing_extensions import Annotated

from app.unify.layer_mapper import LayerMapper
from app.unify.regex_mapper import RegexMapper
from app.unify.well_mapper import WellMapper


class BaseType(types.TypeDecorator):
    __abstract__ = True

    impl = types.String

    cache_ok = True

    # TODO Данный метод реализован для того, чтобы в подклассах
    # атрибут `cache_ok` появлялся в `self.__class__.__dict__`
    def __init_subclass__(cls, /, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.cache_ok = BaseType.cache_ok

    def process_bind_param(self, value, dialect):
        return self.mapper[value]

    @property
    def python_type(self):
        return str


class FieldType(BaseType):
    mapper = RegexMapper(split=False)


class ResevoirType(BaseType):
    mapper = RegexMapper(split=False, sort=True, unique=True)


class MultiResevoirType(BaseType):
    mapper = RegexMapper(sort=True, unique=True)


class WellType(BaseType):
    mapper = WellMapper(split=False)


class MultiWellType(BaseType):
    mapper = WellMapper()


class LayerType(BaseType):
    mapper = LayerMapper(split=False, sort=True)


class MultiLayerType(BaseType):
    mapper = LayerMapper(sort=True)


field_type = Annotated[str, mapped_column(FieldType(50))]
well_type = Annotated[str, mapped_column(WellType(10))]
multi_well_type = Annotated[str, mapped_column(MultiWellType(100))]
reservoir_type = Annotated[str, mapped_column(ResevoirType(100))]
multi_reservoir_type = Annotated[str, mapped_column(MultiResevoirType(200))]
layer_type = Annotated[str, mapped_column(LayerType(20))]
multi_layer_type = Annotated[str, mapped_column(MultiLayerType(100))]
