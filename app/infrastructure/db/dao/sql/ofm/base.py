from typing import Generic, TypeVar

from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import Select

Model = TypeVar("Model", bound=BaseModel, covariant=True, contravariant=False)


class BaseDAO(Generic[Model]):
    def __init__(
        self, model: type[Model], queryset: Select, session: Session
    ) -> None:
        self.model = model
        self.queryset = queryset
        self.session = session

    async def get_by_params(self, **params) -> list[Model]:
        result = await run_in_threadpool(
            self.session.execute, self.queryset, params
        )
        return [self.model.model_validate(row) for row in result.all()]
