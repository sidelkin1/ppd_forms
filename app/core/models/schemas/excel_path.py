from pydantic import BaseModel, ConfigDict


class ExcelPath(BaseModel):
    file: str

    model_config = ConfigDict(extra="forbid")
