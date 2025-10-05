from pydantic import BaseModel, RootModel


class GitHubPRCommentSchema(BaseModel):
    id: int
    body: str
    path: str | None = None
    line: int | None = None


class GitHubGetPRCommentsQuerySchema(BaseModel):
    page: int = 1
    per_page: int = 100


class GitHubGetPRCommentsResponseSchema(RootModel[list[GitHubPRCommentSchema]]):
    root: list[GitHubPRCommentSchema]


class GitHubCreateIssueCommentRequestSchema(BaseModel):
    body: str


class GitHubCreateIssueCommentResponseSchema(BaseModel):
    id: int
    body: str


class GitHubCreateReviewCommentRequestSchema(BaseModel):
    body: str
    path: str
    line: int
    commit_id: str


class GitHubCreateReviewCommentResponseSchema(BaseModel):
    id: int
    body: str
