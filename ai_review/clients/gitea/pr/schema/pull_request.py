from pydantic import BaseModel

from ai_review.clients.gitea.pr.schema.user import GiteaUserSchema


class GiteaBranchSchema(BaseModel):
    ref: str
    sha: str


class GiteaGetPRResponseSchema(BaseModel):
    id: int
    number: int
    title: str
    body: str | None = None
    user: GiteaUserSchema
    base: GiteaBranchSchema
    head: GiteaBranchSchema
