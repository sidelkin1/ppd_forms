from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.dao.local.simple_replace import SimpleReplaceDAO
from app.infrastructure.db.models.local import LayerReplace


class LayerReplaceDAO(SimpleReplaceDAO[LayerReplace]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(LayerReplace, session)
