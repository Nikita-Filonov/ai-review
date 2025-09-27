from pydantic import BaseModel


class GitHubUserSchema(BaseModel):
    id: int
    login: str


class GitHubLabelSchema(BaseModel):
    id: int
    name: str


class GitHubBranchSchema(BaseModel):
    ref: str
    sha: str
    label: str


class GitHubGetPRResponseSchema(BaseModel):
    id: int
    number: int
    title: str
    body: str | None = None
    user: GitHubUserSchema
    labels: list[GitHubLabelSchema]
    assignees: list[GitHubUserSchema] = []
    requested_reviewers: list[GitHubUserSchema] = []
    base: GitHubBranchSchema
    head: GitHubBranchSchema
