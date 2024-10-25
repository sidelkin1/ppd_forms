from pydantic import BaseModel, Field, NonNegativeFloat, PositiveInt


class WellTestParams(BaseModel):
    file: str
    gtm_period: PositiveInt = Field(..., examples=[6])
    gdis_period: PositiveInt = Field(..., examples=[3])
    radius: NonNegativeFloat = Field(..., examples=[300])
