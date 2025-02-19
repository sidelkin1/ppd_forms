from pathlib import Path

from app.core.models.dto import WellTestDB
from app.infrastructure.files.dao.excel.base import BaseDAO
from app.infrastructure.files.dao.excel.configs.well_test import (
    column_names,
    excel_options,
)


class WellTestDAO(BaseDAO[WellTestDB]):
    def __init__(self, filepath: Path) -> None:
        super().__init__(WellTestDB, filepath, excel_options, column_names)

    async def get_all(self) -> list[WellTestDB]:
        df = await self._get_all()
        df = df.drop_duplicates().assign(layer=df["reservoir"])
        return [
            self.model.model_validate(row)
            for row in df.itertuples(index=False)
        ]
