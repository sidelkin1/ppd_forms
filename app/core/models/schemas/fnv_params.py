from pydantic import BaseModel, ConfigDict, NonNegativeFloat

from app.core.models.dto.db.field_list import UneftFieldDB


class FnvParams(BaseModel):
    fields: list[UneftFieldDB]
    min_radius: NonNegativeFloat
    alternative: bool
    max_fields: int = 5

    model_config = ConfigDict(extra="forbid")
