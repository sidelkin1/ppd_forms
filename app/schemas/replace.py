from typing import Union

from pydantic import BaseModel, Extra, PositiveInt

from app.schemas.validators import EmptyStrToNone


class BaseReplaceDB(BaseModel):
    group: str
    replace: str
    order: Union[None, PositiveInt, EmptyStrToNone]

    class Config:
        extra = Extra.forbid


class SimpleReplaceDB(BaseReplaceDB):
    pass


class RegexReplaceDB(BaseReplaceDB):
    pattern: str
