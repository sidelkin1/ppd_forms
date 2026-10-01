from pydantic import BaseModel


class FileExists(BaseModel):
    exists: bool
