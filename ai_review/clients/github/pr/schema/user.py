from pydantic import BaseModel


class GitHubUserSchema(BaseModel):
    id: int | None = None
    login: str
