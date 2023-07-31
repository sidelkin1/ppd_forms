import asyncio
from itertools import count
from pathlib import Path
from typing import Optional

from fastapi import Depends

from app.core.config import settings

RESULT_DIR: Path = settings.base_dir / 'results'
RESULT_NAME: str = 'result_{:03d}'

lock_status: dict[str, asyncio.Lock] = {}


def unique_file_id() -> str:
    for num in count(start=1):
        file_id = RESULT_NAME.format(num)
        if file_id not in lock_status:
            return file_id


async def file_path_from_id(file_id: Optional[str] = None) -> Path:
    file_id = file_id or unique_file_id()
    return (RESULT_DIR / file_id).with_suffix('.csv')


async def get_result_path(
    path: Path = Depends(file_path_from_id),
) -> Path:
    lock = asyncio.Lock()
    lock_status[path.stem] = lock
    await lock.acquire()
    try:
        yield path
    finally:
        lock.release()
        lock_status.pop(path.stem, None)


async def result_is_locked(file_id: str) -> bool:
    lock = lock_status.get(file_id, None)
    return lock is not None and lock.locked()
