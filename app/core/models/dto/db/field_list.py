from pydantic import BaseModel, ConfigDict


class UneftFieldDB(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(extra="forbid", from_attributes=True)
