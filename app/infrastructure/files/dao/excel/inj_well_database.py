from pathlib import Path

from app.core.models.dto import InjWellDatabaseDB
from app.infrastructure.files.dao.excel.base import BaseDAO
from app.infrastructure.files.dao.excel.configs.inj_well_database import (
    column_names,
    excel_options,
)


class InjWellDatabaseDAO(BaseDAO[InjWellDatabaseDB]):
    def __init__(self, filepath: Path) -> None:
        super().__init__(
            InjWellDatabaseDB, filepath, excel_options, column_names
        )

    async def get_all(self) -> list[InjWellDatabaseDB]:
        df = await self._get_all()
        df = df.dropna().drop_duplicates()
        return [
            self.model.model_validate(row)
            for row in df.itertuples(index=False)
        ]
