from pydantic import BaseModel


class DiffFileSchema(BaseModel):
    file: str
    diff: str
