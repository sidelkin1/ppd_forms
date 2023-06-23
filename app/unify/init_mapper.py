import re

from sqlalchemy import func, select
from sqlalchemy.engine import Row
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.local_db import Base
from app.models.types import (FieldType, LayerType, MultiLayerType,
                              MultiResevoirType, ResevoirType)
from app.models.utility import FieldReplace, LayerReplace, ReservoirReplace
from app.unify.base_mapper import BaseMapper

NULL_ORDER = BaseMapper.NULL_ORDER


async def get_grouped_patterns(
    model: type[Base],
    session: AsyncSession,
) -> list[Row]:
    subq = select(
        func.min(model.id).label('id'),
        model.group,
        func.group_concat(model.pattern, '|').label('regex'),
        model.replace,
        func.coalesce(model.order, NULL_ORDER).label('order'),
    ).group_by(
        model.group,
        model.replace,
        model.order,
    ).subquery()
    result = await session.execute(
        select(
            subq.c.group,
            subq.c.regex,
            subq.c.replace,
            subq.c.order,
        ).order_by(subq.c.id)
    )
    return result.all()


async def update_simple_mapper(
    mapper: BaseMapper,
    model: type[Base],
    session: AsyncSession,
) -> list[Row]:
    result = await session.scalars(select(model))
    mapper.update({
        item.group: (item.replace, item.order or NULL_ORDER)
        for item in result.all()
    })


async def update_regex_mapper(
    mapper: BaseMapper,
    model: type[Base],
    session: AsyncSession,
) -> None:
    patterns = await get_grouped_patterns(model, session)
    pattern = re.compile('|'.join((
        f'(?P<{pattern.group}>{pattern.regex})'
        for pattern in patterns
    )), flags=re.IGNORECASE)
    replace = {
        pattern.group: (pattern.replace, pattern.order)
        for pattern in patterns
    }
    mapper.update(replace, pattern)


async def init_field_mapper(session: AsyncSession) -> None:
    await update_regex_mapper(
        FieldType.mapper, FieldReplace, session
    )


async def init_reservoir_mapper(session: AsyncSession) -> None:
    await update_regex_mapper(
        ResevoirType.mapper, ReservoirReplace, session
    )


async def init_multi_reservoir_mapper(session: AsyncSession) -> None:
    await update_regex_mapper(
        MultiResevoirType.mapper, ReservoirReplace, session
    )


async def init_layer_mapper(session: AsyncSession) -> None:
    await update_simple_mapper(
        LayerType.mapper, LayerReplace, session
    )


async def init_multi_layer_mapper(session: AsyncSession) -> None:
    await update_simple_mapper(
        MultiLayerType.mapper, LayerReplace, session
    )
