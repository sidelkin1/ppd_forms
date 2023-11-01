from pydantic import BaseModel, ConfigDict


class InjWellDatabaseDB(BaseModel):
    id: int | None = None
    field: str
    well: str

    model_config = ConfigDict(extra="forbid", from_attributes=True)
