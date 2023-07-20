from pathlib import Path

import aiofiles
import pandas as pd
from aiocsv import AsyncWriter


async def save_to_csv(df: pd.DataFrame, path: Path) -> None:
    async with aiofiles.open(
        path,
        mode='w',
        encoding='cp1251',
        newline='',
    ) as afp:
        writer = AsyncWriter(afp, delimiter=';')
        await writer.writerow(df.columns.to_list())
        for row in df.itertuples(index=False):
            await writer.writerow(row)
