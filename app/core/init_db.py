import csv

from sqlalchemy import exists, insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.local_db import Base
from app.models.local import WellProfile
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


async def init_db(session: AsyncSession) -> None:
    is_filled = await check_table_not_empty(WellProfile, session)
    if not is_filled:
        base_dir = settings.base_dir
        with open(base_dir / 'data/results.csv', encoding='utf8') as csvfile:
            reader = csv.DictReader(csvfile)
            await session.execute(
                insert(WellProfile),
                [WellProfileDB(**row).dict() for row in reader],
            )
            await session.commit()
