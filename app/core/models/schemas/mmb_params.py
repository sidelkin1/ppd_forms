from pydantic import BaseModel


class MmbParams(BaseModel):
    file: str
    alternative: bool
