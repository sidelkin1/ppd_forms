from pathlib import Path

from app.core.models.dto import NewStrategyOilDB
from app.infrastructure.files.dao.excel.base import BaseDAO
from app.infrastructure.files.dao.excel.configs.new_strategy_oil import (
    column_names,
    excel_options,
)


class NewStrategyOilDAO(BaseDAO[NewStrategyOilDB]):
    def __init__(self, filepath: Path) -> None:
        super().__init__(
            NewStrategyOilDB, filepath, excel_options, column_names
        )

    async def get_all(self) -> list[NewStrategyOilDB]:
        df = await self._get_all()
        df["vnr_date"].fillna(df["start_date"], inplace=True)
        df["start_date"].fillna(df["vnr_date"], inplace=True)
        cols = ["start_date", "vnr_date"]
        df.dropna(subset=cols, inplace=True)
        return [
            self.model.model_validate(row)
            for row in df.itertuples(index=False)
        ]
