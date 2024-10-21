from pydantic import BaseModel, Field, PositiveInt


class WellTestParams(BaseModel):
    file: str
    gtm_period: PositiveInt = Field(..., examples=[6])
