from typing import Annotated

from pydantic import BaseModel, ConfigDict, StringConstraints

from app.core.models.dto import UneftFieldDB, UneftReservoirDB


class OwcRespParams(BaseModel):
    field: UneftFieldDB
    reservoir: UneftReservoirDB
    well: Annotated[
        str, StringConstraints(strip_whitespace=True, to_upper=True)
    ]

    model_config = ConfigDict(extra="forbid")
