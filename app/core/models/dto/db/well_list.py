from pydantic import BaseModel, ConfigDict


class UneftWellDB(BaseModel):
    uwi: str
    name: str

    model_config = ConfigDict(extra="forbid", from_attributes=True)
