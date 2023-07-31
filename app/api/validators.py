from pathlib import Path

from fastapi import HTTPException, status


def check_file_exists(path: Path) -> None:
    if not path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Файл не найден!',
        )
