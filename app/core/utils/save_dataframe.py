import asyncio
from pathlib import Path
from typing import Any

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


async def save_to_excel(df: pd.DataFrame, path: Path, **kwargs: Any) -> None:
    await asyncio.to_thread(
        df.to_excel,
        path,
        engine="xlsxwriter",
        index=False,
        engine_kwargs={"options": {"default_date_format": "dd.mm.yyyy"}},
        **kwargs,
    )  # type: ignore[call-arg]
