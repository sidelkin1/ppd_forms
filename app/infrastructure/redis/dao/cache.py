import json
from datetime import timedelta
from typing import Generic, TypeVar

from pydantic import BaseModel
from redis.asyncio import Redis

Model = TypeVar("Model", bound=BaseModel, covariant=True, contravariant=False)


class CacheDAO(Generic[Model]):
    def __init__(
        self,
        model: type[Model],
        redis: Redis,
        prefix: str = "uneft",
        expires: timedelta = timedelta(days=1),
    ):
        self.model = model
        self.redis = redis
        self.expires = expires
        self.prefix = prefix

    def _create_key(self, key: str) -> str:
        return f"{self.prefix}:{key}"

    async def add_objects(self, key: str, objs: list[Model]) -> None:
        key_ = self._create_key(key)
        objs_dict = [obj.model_dump_json() for obj in objs]
        objs_json = json.dumps(objs_dict)
        await self.redis.setex(key_, self.expires, objs_json)

    async def get_objects(self, key: str) -> list[Model]:
        key_ = self._create_key(key)
        objs_json = await self.redis.get(key_)
        if objs_json:
            objs_dict = json.loads(objs_json)
            return [self.model.model_validate_json(obj) for obj in objs_dict]
        return []
