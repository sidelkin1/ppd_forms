from pathlib import Path

from app.core.models.dto import NeighborhoodDB
from app.infrastructure.files.dao.excel.base import BaseDAO
from app.infrastructure.files.dao.excel.configs.neighborhood import (
    column_names,
    excel_options,
)


class NeighborhoodDAO(BaseDAO[NeighborhoodDB]):
    def __init__(self, filepath: Path) -> None:
        super().__init__(NeighborhoodDB, filepath, excel_options, column_names)

    async def get_all(self) -> list[NeighborhoodDB]:
        df = await self._get_all()
        cols = ["field", "reservoir", "well"]
        df = df.dropna().groupby(cols, as_index=False).agg(",".join)
        return [
            self.model.model_validate(row)
            for row in df.itertuples(index=False)
        ]
