import aiocsv
import aiofiles
from pydantic import BaseModel
from sqlalchemy import exists, insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.local_db import Base
from app.models.utility import FieldReplace, LayerReplace, ReservoirReplace
from app.models.well_profile import WellProfile
from app.schemas.replace import RegexReplaceDB, SimpleReplaceDB
from app.schemas.well_profile import WellProfileDB


async def check_table_not_empty(
    model: type[Base],
    session: AsyncSession
) -> bool:
    result = await session.execute(
        select(exists().where(
            model.id.is_not(None)
        ))
    )
    return result.scalar()


async def fill_empty_table_with_data(
    model: type[Base],
    schema: type[BaseModel],
    session: AsyncSession,
    file_name: str,
) -> None:
    is_filled = await check_table_not_empty(model, session)
    if not is_filled:
        path = settings.base_dir / 'data' / file_name
        async with aiofiles.open(path, encoding='utf8') as csvfile:
            reader = aiocsv.AsyncDictReader(csvfile)
            await session.execute(
                insert(model),
                [schema(**row).dict() async for row in reader],
            )
            await session.commit()


async def init_profile(session: AsyncSession) -> None:
    await fill_empty_table_with_data(
        WellProfile, WellProfileDB, session, 'results.csv'
    )


async def init_field_replace(session: AsyncSession) -> None:
    await fill_empty_table_with_data(
        FieldReplace, RegexReplaceDB, session, 'fields.csv'
    )


async def init_reservoir_replace(session: AsyncSession) -> None:
    await fill_empty_table_with_data(
        ReservoirReplace, RegexReplaceDB, session, 'reservoirs.csv'
    )


async def init_layer_replace(session: AsyncSession) -> None:
    await fill_empty_table_with_data(
        LayerReplace, SimpleReplaceDB, session, 'layers.csv'
    )
