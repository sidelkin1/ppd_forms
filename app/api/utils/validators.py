from pathlib import Path

from fastapi import HTTPException, WebSocketException, status

from app.core.models.dto import UneftFieldDB


def check_file_exists(path: Path) -> None:
    if not path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Файл не найден!",
        )


def check_user_id_exists_http(user_id: str) -> None:
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)


def check_user_id_exists_ws(user_id: str) -> None:
    if user_id is None:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)


def check_field_exists(field_id: int, fields: list[UneftFieldDB]) -> None:
    if not any(field.id == field_id for field in fields):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Месторождение не найдено!",
        )
