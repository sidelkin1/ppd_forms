from pathlib import Path

import aiofiles
import pandas as pd
from aiocsv import AsyncWriter


async def save_to_csv(
    df: pd.DataFrame, path: Path, encoding: str, delimiter: str
) -> None:
    async with aiofiles.open(
        path, mode="w", encoding=encoding, newline=""
    ) as afp:
        writer = AsyncWriter(afp, delimiter=delimiter)
        await writer.writerow(df.columns.to_list())
        for row in df.itertuples(index=False):
            await writer.writerow(row)
