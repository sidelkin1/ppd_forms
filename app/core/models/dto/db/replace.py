from pydantic import BaseModel, ConfigDict, NonNegativeInt

from app.core.models.dto.db.validators import EmptyStrToNone


class BaseReplaceDB(BaseModel):
    id: int | None = None
    group: str
    replace: str
    order: EmptyStrToNone[NonNegativeInt] = None

    model_config = ConfigDict(extra="forbid", from_attributes=True)


class SimpleReplaceDB(BaseReplaceDB):
    pass


class RegexReplaceDB(BaseReplaceDB):
    pattern: str
