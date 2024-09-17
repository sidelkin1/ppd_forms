from datetime import timedelta

from redis.asyncio import Redis
from sqlalchemy import CompoundSelect, Select, select
from sqlalchemy.orm import Session

from app.infrastructure.db.dao.sql.ofm.base import Model
from app.infrastructure.db.dao.sql.ofm.cached import CachedDAO


class AssetListDAO(CachedDAO[Model]):
    def __init__(
        self,
        model: type[Model],
        querysets: dict[str, Select | CompoundSelect],
        cache_keys: list[str],
        session: Session,
        redis: Redis,
        expires: timedelta,
    ) -> None:
        super().__init__(model, select(), session, redis, expires)
        self.cache_keys = dict(zip(querysets.keys(), cache_keys))
        self.querysets = querysets

    async def get_all(self, asset: str) -> list[Model]:
        key = self.cache_keys[asset]
        self.queryset = self.querysets[asset]
        return await self.get_by_params_cached(key)

    async def get_by_field(self, asset: str, field_id: int) -> list[Model]:
        key = self.cache_keys[asset].format(field_id)
        self.queryset = self.querysets[asset]
        return await self.get_by_params_cached(key, field_id=field_id)
