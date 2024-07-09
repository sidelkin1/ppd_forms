from pydantic import Field, PositiveInt

from app.core.models.enums import ExcludeGTM
from app.core.models.schemas.date_range import DateRange
from app.core.models.schemas.on_date import OnDate


class MatrixEffect(DateRange, OnDate):
    base_period: PositiveInt = Field(..., examples=[1])
    pred_period: PositiveInt = Field(..., examples=[12])
    excludes: list[ExcludeGTM] = Field(..., examples=[[ExcludeGTM.perf]])
