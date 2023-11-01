from datetime import datetime
from pathlib import Path

from app.core.config.settings import settings


def result_name():
    return datetime.now().strftime("result_%Y_%m_%dT%H_%M_%S")


def result_path(
    user_id: str | None = None,
    file_id: str | None = None,
) -> Path:
    if file_id is not None and user_id is None:
        raise ValueError("`file_id` is provided without `user_id`")

    result_dir = settings.result_dir
    if user_id is not None:
        result_dir /= user_id
    if file_id is not None:
        result_dir /= file_id
        result_dir = result_dir.with_suffix(".csv")

    return result_dir
