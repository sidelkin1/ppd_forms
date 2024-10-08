import re

from app.infrastructure.db.dao import local
from app.infrastructure.db.types import types
from app.infrastructure.db.types.unify import (
    BaseMapper,
    RegexMapper,
    SimpleMapper,
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
    await _update_regex_mapper(types.FieldType.mapper, dao)


async def init_reservoir_mapper(dao: local.ReservoirReplaceDAO) -> None:
    await _update_regex_mapper(types.ResevoirType.mapper, dao)


async def init_multi_reservoir_mapper(dao: local.ReservoirReplaceDAO) -> None:
    await _update_regex_mapper(types.MultiResevoirType.mapper, dao)


async def init_multi_split_reservoir_mapper(
    dao: local.ReservoirReplaceDAO,
) -> None:
    await _update_regex_mapper(types.MultiSplitResevoirType.mapper, dao)


async def init_layer_mapper(dao: local.LayerReplaceDAO) -> None:
    await _update_simple_mapper(types.LayerType.mapper, dao)


async def init_gtm_mapper(dao: local.GtmReplaceDAO) -> None:
    await _update_simple_mapper(types.GtmType.mapper, dao)


async def init_multi_layer_mapper(dao: local.LayerReplaceDAO) -> None:
    await _update_simple_mapper(types.MultiLayerType.mapper, dao)
