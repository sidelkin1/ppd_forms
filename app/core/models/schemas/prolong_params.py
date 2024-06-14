from pydantic import BaseModel

from app.core.models.enums.interpolation import Interpolation


class ProlongParams(BaseModel):
    expected: str
    actual: str
    interpolation: Interpolation
