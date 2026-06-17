from datetime import date
from pathlib import Path
from shutil import make_archive

from app.core.utils.save_dataframe import save_to_excel
from app.infrastructure.db.dao.sql.reporters import CompensationReporter


async def compensation_report(
    path: Path, on_date: date, dao: CompensationReporter
) -> None:
    df = await dao.read_one(on_date=on_date)
    df["oil_fvf"] = df["oil_fvf"].fillna("")
    await save_to_excel(df, path / "compensation.xlsx")
    make_archive(str(path), "zip", root_dir=path)
