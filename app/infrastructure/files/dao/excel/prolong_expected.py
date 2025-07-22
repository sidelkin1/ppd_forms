from pathlib import Path

from app.core.models.dto import ProlongExpected
from app.infrastructure.files.dao.excel.base import BaseDAO
from app.infrastructure.files.dao.excel.configs.prolong_expected import (
    column_names,
    excel_options,
)


class ProlongExpectedDAO(BaseDAO[ProlongExpected]):
    def __init__(self, filepath: Path) -> None:
        super().__init__(
            ProlongExpected, filepath, excel_options, column_names
        )

    async def get_all(self) -> list[ProlongExpected]:
        df = await self._get_all()
        df = df.dropna(subset=df.columns.drop(["oil_total_1", "liq_total_1"]))
        return [
            self.model.model_validate(row)
            for row in df.itertuples(index=False)
        ]
