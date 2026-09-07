from pydantic import BaseModel, ConfigDict


class CsvPath(BaseModel):
    file: str

    model_config = ConfigDict(extra="forbid")
