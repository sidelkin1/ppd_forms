from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models.dto import SimpleReplaceDB
from app.infrastructure.db.dao.local.base import BaseDAO, Model


class SimpleReplaceDAO(BaseDAO[Model, SimpleReplaceDB]):
    def __init__(self, model: type[Model], session: AsyncSession) -> None:
        super().__init__(model, SimpleReplaceDB, session)
