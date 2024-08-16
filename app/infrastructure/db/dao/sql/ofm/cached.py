from redis.asyncio import Redis
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import CompoundSelect, Select

from app.infrastructure.db.dao.sql.ofm.base import BaseDAO, Model
from app.infrastructure.redis.dao import CacheDAO


class CachedDAO(BaseDAO[Model]):
    def __init__(
        self,
        model: type[Model],
        queryset: Select | CompoundSelect,
        session: Session,
        redis: Redis,
    ) -> None:
        super().__init__(model, queryset, session)
        self.cache = CacheDAO(model, redis)

    async def get_by_params_cached(self, key, **params) -> list[Model]:
        if objs := await self.cache.get_objects(key):
            return objs
        objs = await self.get_by_params(**params)
        await self.cache.add_objects(key, objs)
        return objs
