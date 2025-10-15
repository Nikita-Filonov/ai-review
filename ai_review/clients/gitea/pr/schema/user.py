from pydantic import BaseModel


class GiteaUserSchema(BaseModel):
    id: int
    login: str
