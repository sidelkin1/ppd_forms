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
