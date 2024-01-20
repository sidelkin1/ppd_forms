from typing import Generic, TypeVar

from pydantic import BaseModel
from sqlalchemy import delete, exists, func, insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.models.local.base import Base

Model = TypeVar("Model", bound=Base, covariant=True, contravariant=False)
DataModel = TypeVar(
    "DataModel", bound=BaseModel, covariant=True, contravariant=False
)


class BaseDAO(Generic[Model, DataModel]):
    def __init__(
        self,
        model: type[Model],
        data_model: type[DataModel],
        session: AsyncSession,
    ) -> None:
        self.model = model
        self.data_model = data_model
        self.session = session

    async def get_all(self) -> list[DataModel]:
        result = await self.session.scalars(select(self.model))
        return [self.data_model.model_validate(obj) for obj in result.all()]

    async def insert(self, data: list[DataModel]) -> None:
        await self.session.execute(
            insert(self.model), [dto.model_dump() for dto in data]
        )

    async def is_empty(self) -> bool:
        result = await self.session.execute(
            select(exists().where(self.model.id.is_not(None)))
        )
        return not result.scalar()

    async def delete_all(self) -> None:
        await self.session.execute(delete(self.model))

    async def count(self):
        result = await self.session.execute(select(func.count(self.model.id)))
        return result.scalar_one()

    async def commit(self) -> None:
        await self.session.commit()
