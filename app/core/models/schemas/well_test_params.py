from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    NonNegativeFloat,
    PositiveInt,
)


class WellTestParams(BaseModel):
    file: str
    gtm_period: PositiveInt = Field(..., examples=[6])
    gdis_period: PositiveInt = Field(..., examples=[3])
    radius: NonNegativeFloat = Field(..., examples=[300])

    model_config = ConfigDict(extra="forbid")
