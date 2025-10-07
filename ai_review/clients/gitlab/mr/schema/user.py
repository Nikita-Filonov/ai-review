from pydantic import BaseModel


class GitLabUserSchema(BaseModel):
    id: int
    name: str
    username: str
