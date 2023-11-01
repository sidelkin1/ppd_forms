from pathlib import Path

from app.core.models.dto import NewStrategyInjDB
from app.infrastructure.db.dao.excel.base import BaseDAO
from app.infrastructure.db.dao.excel.configs.new_strategy_inj import (
    RESERVOIRS_WELLS_SEPARATOR,
    column_names,
    excel_options,
)


class NewStrategyInjDAO(BaseDAO[NewStrategyInjDB]):
    def __init__(self, filepath: Path) -> None:
        super().__init__(
            NewStrategyInjDB, filepath, excel_options, column_names
        )

    async def get_all(self) -> list[NewStrategyInjDB]:
        df = await self._get_all()
        df[["reservoir_neighbs", "neighbs"]] = df["neighbs"].str.split(
            RESERVOIRS_WELLS_SEPARATOR, expand=True
        )
        return [
            self.model.model_validate(row)
            for row in df.itertuples(index=False)
        ]
