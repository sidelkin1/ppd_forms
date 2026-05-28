from pydantic import BaseModel, ConfigDict


class MmbParams(BaseModel):
    file: str
    alternative: bool

    model_config = ConfigDict(extra="forbid")
