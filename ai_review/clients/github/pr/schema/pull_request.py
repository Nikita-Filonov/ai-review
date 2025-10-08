from pydantic import BaseModel, Field

from ai_review.clients.github.pr.schema.user import GitHubUserSchema


class GitHubLabelSchema(BaseModel):
    id: int
    name: str | None = None


class GitHubBranchSchema(BaseModel):
    ref: str
    sha: str
    label: str | None = None


class GitHubGetPRResponseSchema(BaseModel):
    id: int
    number: int
    title: str
    body: str | None = None
    user: GitHubUserSchema
    labels: list[GitHubLabelSchema] = Field(default_factory=list)
    assignees: list[GitHubUserSchema] = Field(default_factory=list)
    requested_reviewers: list[GitHubUserSchema] = Field(default_factory=list)
    base: GitHubBranchSchema
    head: GitHubBranchSchema
