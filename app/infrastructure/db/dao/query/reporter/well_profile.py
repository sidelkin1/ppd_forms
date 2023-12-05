from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.infrastructure.db.dao.query.reporter.base import BaseDAO
from app.infrastructure.db.dao.query.reporter.querysets.well_profile import (
    select_profile_report,
)


class WellProfileReporter(BaseDAO):
    def __init__(self, pool: async_sessionmaker[AsyncSession]) -> None:
        super().__init__({"profile": select_profile_report()}, pool)
