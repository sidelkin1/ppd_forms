from datetime import date
from pathlib import Path
from shutil import make_archive

from app.core.utils.save_dataframe import save_to_csv
from app.infrastructure.db.dao.sql.reporters import CompensationReporter
from app.infrastructure.files.config.models.csv import CsvSettings


async def compensation_report(
    path: Path,
    on_date: date,
    dao: CompensationReporter,
    csv_config: CsvSettings,
) -> None:
    df = await dao.read_one(on_date=on_date)
    df["oil_fvf"] = df["oil_fvf"].fillna("")
    await save_to_csv(
        df,
        path / "compensation.csv",
        csv_config.encoding,
        csv_config.delimiter,
    )
    make_archive(str(path), "zip", root_dir=path)
