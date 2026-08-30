from app.core.services import init_mapper
from app.infrastructure.db.dao import local
from app.infrastructure.sessions import Sessions


async def init_field_mapper(sessions: Sessions) -> None:
    async with sessions.local_session() as session:
        await init_mapper.init_field_mapper(local.FieldReplaceDAO(session))


async def init_reservoir_mapper(sessions: Sessions) -> None:
    async with sessions.local_session() as session:
        await init_mapper.init_reservoir_mapper(
            local.ReservoirReplaceDAO(session)
        )


async def init_multi_reservoir_mapper(sessions: Sessions) -> None:
    async with sessions.local_session() as session:
        await init_mapper.init_multi_reservoir_mapper(
            local.ReservoirReplaceDAO(session)
        )


async def init_multi_split_reservoir_mapper(sessions: Sessions) -> None:
    async with sessions.local_session() as session:
        await init_mapper.init_multi_split_reservoir_mapper(
            local.ReservoirReplaceDAO(session)
        )


async def init_layer_mapper(sessions: Sessions) -> None:
    async with sessions.local_session() as session:
        await init_mapper.init_layer_mapper(local.LayerReplaceDAO(session))


async def init_gtm_mapper(sessions: Sessions) -> None:
    async with sessions.local_session() as session:
        await init_mapper.init_gtm_mapper(local.GtmReplaceDAO(session))


async def init_multi_layer_mapper(sessions: Sessions) -> None:
    async with sessions.local_session() as session:
        await init_mapper.init_multi_layer_mapper(
            local.LayerReplaceDAO(session)
        )
