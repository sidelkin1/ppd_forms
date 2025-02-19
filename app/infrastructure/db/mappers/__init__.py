from app.core.config.main import get_app_settings

from .base import BaseMapper, SplitMode
from .layer import LayerMapper
from .regex import RegexMapper
from .simple import SimpleMapper
from .well import TRANSLATE_TO, WellMapper
from .well_test_layer import WellTestLayerMapper

settings = get_app_settings()  # FIXME avoid global variable

# Название месторождения
field_mapper = RegexMapper(split=False, delimiter=settings.delimiter)

# Название объекта
reservoir_mapper = RegexMapper(split=False, delimiter=settings.delimiter)

# Список из нескольких объектов
multi_reservoir_mapper = RegexMapper(
    sort=True, unique=True, delimiter=settings.delimiter
)

# Список из нескольких объектов (другой способ разбивки)
multi_split_reservoir_mapper = RegexMapper(
    sort=True,
    unique=True,
    delimiter=settings.delimiter,
    split_mode=SplitMode.split_in,
)

# Номер скважины
well_mapper = WellMapper(split=False, delimiter=settings.delimiter)

# Список скважин
multi_well_mapper = WellMapper(unique=True, delimiter=settings.delimiter)

# Индекс пласта
layer_mapper = LayerMapper(split=False, delimiter=settings.delimiter)

# Список индексов пласта
multi_layer_mapper = LayerMapper(sort=True, delimiter=settings.delimiter)
well_test_multi_layer_mapper = WellTestLayerMapper(
    unique=True, delimiter=settings.delimiter, split_mode=SplitMode.split_in
)

# Название ГТМ
gtm_mapper = SimpleMapper(split=False, delimiter=settings.delimiter)
