from pathlib import Path

from fastapi import HTTPException, status

from app.core.models.dto import UneftFieldDB


def check_file_exists(path: Path) -> None:
    if not path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Файл не найден!",
        )


def check_field_exists(field: UneftFieldDB | None) -> None:
    if field is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Месторождение не найдено!",
        )
