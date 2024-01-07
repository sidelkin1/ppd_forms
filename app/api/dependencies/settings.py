from typing import Annotated

from fastapi import Depends, FastAPI

from app.core.config.settings import Settings

app = FastAPI()


def settings_provider() -> Settings:
    raise NotImplementedError


SettingsDep = Annotated[Settings, Depends(settings_provider)]
