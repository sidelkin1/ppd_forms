import re
from datetime import date
from typing import Annotated

from pydantic import (
    BaseModel,
    ConfigDict,
    PositiveFloat,
    StringConstraints,
    field_validator,
)

from app.core.models.dto import UneftFieldDB, UneftReservoirDB
from app.core.models.enums import WellTest


class OwcRespParams(BaseModel):
    field: UneftFieldDB
    reservoir: UneftReservoirDB
    well: Annotated[
        str, StringConstraints(strip_whitespace=True, to_upper=True)
    ]
    pressure: PositiveFloat
    depth: PositiveFloat
    well_test: WellTest
    on_date: date

    model_config = ConfigDict(extra="forbid")

    @field_validator("well", mode="after")
    @classmethod
    def remove_well_branch(cls, v: str) -> str:
        if not (v := re.sub(r"[ВB]\d+$", "", v)):
            raise ValueError("`well` cannot be empty")
        return v
