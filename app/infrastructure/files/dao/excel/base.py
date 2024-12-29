from pathlib import Path
from typing import Any, Generic, TypeVar

import pandas as pd
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel

Model = TypeVar("Model", bound=BaseModel, covariant=True, contravariant=False)


class BaseDAO(Generic[Model]):
    def __init__(
        self,
        model: type[Model],
        filepath: Path,
        excel_options: dict[str, Any] | None = None,
        column_names: list[str] | None = None,
    ) -> None:
        self.model = model
        self.filepath = filepath
        self.excel_options = excel_options or {}
        self.column_names = column_names

    async def _get_all(self) -> pd.DataFrame:
        df: pd.DataFrame = await run_in_threadpool(
            pd.read_excel,  # type: ignore[arg-type]
            self.filepath,
            **self.excel_options,
        )
        if self.column_names:
            df.columns = self.column_names  # type: ignore[assignment]
        return df

    async def get_all(self) -> list[Model]:
        df = await self._get_all()
        return [
            self.model.model_validate(row)
            for row in df.itertuples(index=False)
        ]
