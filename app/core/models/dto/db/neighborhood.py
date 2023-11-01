from pydantic import BaseModel, ConfigDict


class NeighborhoodDB(BaseModel):
    id: int | None = None
    field: str
    reservoir: str
    well: str
    neighbs: str

    model_config = ConfigDict(extra="forbid", from_attributes=True)
