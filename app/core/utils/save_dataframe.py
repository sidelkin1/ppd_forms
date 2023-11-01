from pathlib import Path

import aiofiles
import pandas as pd
from aiocsv import AsyncWriter

from app.core.config.settings import settings


async def save_to_csv(df: pd.DataFrame, path: Path) -> None:
    async with aiofiles.open(
        path,
        mode="w",
        encoding=settings.csv_encoding,
        newline="",
    ) as afp:
        writer = AsyncWriter(afp, delimiter=settings.csv_delimiter)
        await writer.writerow(df.columns.to_list())
        for row in df.itertuples(index=False):
            await writer.writerow(row)
