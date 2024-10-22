import re

from app.infrastructure.db.dao import local
from app.infrastructure.db.mappers import (
    BaseMapper,
    RegexMapper,
    SimpleMapper,
    field_mapper,
    gtm_mapper,
    layer_mapper,
    multi_layer_mapper,
    multi_reservoir_mapper,
    multi_split_reservoir_mapper,
    reservoir_mapper,
)


async def _update_simple_mapper(
    mapper: SimpleMapper, dao: local.SimpleReplaceDAO
) -> None:
    objs = await dao.get_all()
    mapper.update(
        {
            dto.group: (dto.replace, dto.order or BaseMapper.NULL_ORDER)
            for dto in objs
        }
    )


async def _update_regex_mapper(
    mapper: RegexMapper, dao: local.RegexReplaceDAO
) -> None:
    objs = await dao.get_grouped_patterns()
    pattern = re.compile(
        "|".join(f"(?P<{dto.group}>{dto.pattern})" for dto in objs),
        flags=re.IGNORECASE,
    )
    replace = {
        dto.group: (dto.replace, dto.order or BaseMapper.NULL_ORDER)
        for dto in objs
    }
    mapper.update(replace, pattern)


async def init_field_mapper(dao: local.FieldReplaceDAO) -> None:
    await _update_regex_mapper(field_mapper, dao)


async def init_reservoir_mapper(dao: local.ReservoirReplaceDAO) -> None:
    await _update_regex_mapper(reservoir_mapper, dao)


async def init_multi_reservoir_mapper(dao: local.ReservoirReplaceDAO) -> None:
    await _update_regex_mapper(multi_reservoir_mapper, dao)


async def init_multi_split_reservoir_mapper(
    dao: local.ReservoirReplaceDAO,
) -> None:
    await _update_regex_mapper(multi_split_reservoir_mapper, dao)


async def init_layer_mapper(dao: local.LayerReplaceDAO) -> None:
    await _update_simple_mapper(layer_mapper, dao)


async def init_gtm_mapper(dao: local.GtmReplaceDAO) -> None:
    await _update_simple_mapper(gtm_mapper, dao)


async def init_multi_layer_mapper(dao: local.LayerReplaceDAO) -> None:
    await _update_simple_mapper(multi_layer_mapper, dao)
