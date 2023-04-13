from pathlib import Path

from pydantic import BaseSettings


class Settings(BaseSettings):
    base_dir: Path = Path(__file__).resolve().parent.parent.parent
    app_title: str = 'Стандартные формы для ППД'
    app_description: str = 'Приложение для создания типовых отчетов ППД'
    local_database_url: str
    ofm_database_url: str

    class Config:
        env_file = '.env'


settings = Settings()
