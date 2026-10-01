from pydantic import BaseModel, ConfigDict, NonNegativeFloat

from app.core.models.dto.db.field_list import UneftFieldDB


class FnvParams(BaseModel):
    field: UneftFieldDB
    min_radius: NonNegativeFloat
    alternative: bool

    model_config = ConfigDict(extra="forbid")
