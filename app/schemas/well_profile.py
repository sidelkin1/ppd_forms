from datetime import date
from typing import Optional, Union

from pydantic import BaseModel, Extra

from app.schemas.validators import EmptyStrToNone


class WellProfileDB(BaseModel):
    field: str
    uwi: str
    well_name: str
    well_type: Optional[str]
    rec_date: date
    cid: str
    layer: Optional[str]
    top: float
    bottom: float
    abstop: Union[None, float, EmptyStrToNone]
    absbotm: Union[None, float, EmptyStrToNone]
    diff_absorp: Union[None, float, EmptyStrToNone]
    tot_absorp: Union[None, float, EmptyStrToNone]
    liq_rate: Union[None, float, EmptyStrToNone]
    remarks: Optional[str]

    class Config:
        extra = Extra.forbid
