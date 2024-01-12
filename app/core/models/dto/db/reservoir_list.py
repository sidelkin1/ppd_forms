from pydantic import BaseModel, ConfigDict


class UneftReservoirDB(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(extra="forbid", from_attributes=True)
