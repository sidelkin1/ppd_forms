from pathlib import Path

from python_calamine import CalamineWorkbook

from app.core.models.dto import NewStrategyInjDB
from app.infrastructure.files.dao.excel.base import AbstractBaseDAO, BaseDAO
from app.infrastructure.files.dao.excel.configs.new_strategy_inj import (
    RESERVOIRS_WELLS_SEPARATOR,
    SHORT_EXCEL_WIDTH,
    extra_columns,
    narrow_column_names,
    narrow_excel_options,
    wide_column_names,
    wide_excel_options,
)


class NarrowNewStrategyInjDAO(BaseDAO[NewStrategyInjDB]):
    def __init__(self, filepath: Path) -> None:
        super().__init__(
            NewStrategyInjDB,
            filepath,
            narrow_excel_options,
            narrow_column_names,
        )

    async def get_all(self) -> list[NewStrategyInjDB]:
        df = await self._get_all()
        df = df.dropna(subset="gtm_date").assign(**extra_columns)
        return [
            self.model.model_validate(row)
            for row in df.itertuples(index=False)
        ]


class WideNewStrategyInjDAO(BaseDAO[NewStrategyInjDB]):
    def __init__(self, filepath: Path, delimiter: str) -> None:
        super().__init__(
            NewStrategyInjDB,
            filepath,
            wide_excel_options(delimiter),
            wide_column_names,
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


class NewStrategyInjDAO(AbstractBaseDAO[NewStrategyInjDB]):
    def __init__(self, filepath: Path, delimiter: str) -> None:
        self.narrow_dao = NarrowNewStrategyInjDAO(filepath)
        self.wide_dao = WideNewStrategyInjDAO(filepath, delimiter)

    @property
    def width(self) -> int:
        with CalamineWorkbook.from_path(self.narrow_dao.filepath) as workbook:
            sheet = workbook.get_sheet_by_name(
                self.narrow_dao.excel_options["sheet_name"]
            )
            return sheet.width

    async def get_all(self) -> list[NewStrategyInjDB]:
        if self.width == SHORT_EXCEL_WIDTH:
            return await self.narrow_dao.get_all()
        return await self.wide_dao.get_all()
