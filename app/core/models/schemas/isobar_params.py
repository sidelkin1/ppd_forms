import re
from datetime import date
from pathlib import Path

from dateutil.relativedelta import relativedelta
from pydantic import BaseModel, ConfigDict, field_validator

FILE_DATE_RE = re.compile(r"(\d{2})\.(\d{2})\.(\d{4})")
FILE_SUFFIX = ".xlsm"


def parse_previous_date(filename: str) -> date:
    """Дата предыдущей карты из имени файла ``СВОДНЫЙ_ИЗОБАРЫ_DD.MM.YYYY``."""
    if not filename.lower().endswith(FILE_SUFFIX):
        raise ValueError("Ожидается файл предыдущей сводной в формате .xlsm")
    match = FILE_DATE_RE.search(Path(filename).stem)
    if match is None:
        raise ValueError(
            "В имени файла нет даты в формате ДД.ММ.ГГГГ, например "
            "«СВОДНЫЙ_ИЗОБАРЫ_01.07.2026.xlsm»"
        )
    day, month, year = (int(part) for part in match.groups())
    try:
        result = date(year, month, day)
    except ValueError as error:
        raise ValueError("Некорректная дата в имени файла") from error
    if result.day != 1:
        raise ValueError("Дата в имени файла должна быть первым числом месяца")
    return result


class IsobarParams(BaseModel):
    file: str

    model_config = ConfigDict(extra="forbid")

    @field_validator("file")
    @classmethod
    def check_file(cls, value: str) -> str:
        parse_previous_date(value)
        return value

    @property
    def previous_date(self) -> date:
        return parse_previous_date(self.file)

    @property
    def on_date(self) -> date:
        return self.previous_date + relativedelta(months=3)

    @property
    def stock_date(self) -> date:
        return self.on_date - relativedelta(months=1)
