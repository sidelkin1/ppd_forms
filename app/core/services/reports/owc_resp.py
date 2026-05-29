from pathlib import Path

# from shutil import make_archive
from app.infrastructure.db.dao.sql.reporters import OwcRespReporter


async def owc_resp_report(
    path: Path,
    field_id: int,
    reservoir_id: int,
    well: str,
    dao: OwcRespReporter,
) -> None:
    df = await dao.read_one(
        field_id=field_id, reservoir_id=reservoir_id, well=well
    )
    df.to_excel(path / "owc_resp.xlsx")
    # make_archive(str(path), "zip", root_dir=path)
