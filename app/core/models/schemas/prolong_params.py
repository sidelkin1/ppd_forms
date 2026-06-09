from pydantic import BaseModel, ConfigDict

from app.core.models.enums.interpolation import Interpolation


class ProlongParams(BaseModel):
    expected: str
    actual: str
    interpolations: list[Interpolation]

    model_config = ConfigDict(extra="forbid")
