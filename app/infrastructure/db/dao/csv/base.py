from pathlib import Path
from typing import Generic, TypeVar

import aiocsv
import aiofiles
from pydantic import BaseModel

Model = TypeVar("Model", bound=BaseModel, covariant=True, contravariant=False)


class BaseDAO(Generic[Model]):
    def __init__(self, model: type[Model], filepath: Path) -> None:
        self.model = model
        self.filepath = filepath

    async def get_all(self) -> list[Model]:
        async with aiofiles.open(self.filepath, encoding="utf8") as csvfile:
            reader = aiocsv.AsyncDictReader(csvfile)
            return [self.model(**row) async for row in reader]
