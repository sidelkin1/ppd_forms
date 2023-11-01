from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.dao.local.regex_replace import RegexReplaceDAO
from app.infrastructure.db.models.local import ReservoirReplace


class ReservoirReplaceDAO(RegexReplaceDAO[ReservoirReplace]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(ReservoirReplace, session)
