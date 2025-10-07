from pydantic import BaseModel, RootModel

from ai_review.clients.github.pr.schema.user import GitHubUserSchema


class GitHubIssueCommentSchema(BaseModel):
    """Represents a top-level comment in a PR discussion (issue-level)."""
    id: int
    body: str
    user: GitHubUserSchema | None = None


class GitHubPRCommentSchema(BaseModel):
    """Represents an inline code review comment on a specific line in a PR."""
    id: int
    body: str
    path: str | None = None
    line: int | None = None
    user: GitHubUserSchema | None = None
    in_reply_to_id: int | None = None


class GitHubGetPRCommentsQuerySchema(BaseModel):
    page: int = 1
    per_page: int = 100


class GitHubGetPRCommentsResponseSchema(RootModel[list[GitHubPRCommentSchema]]):
    root: list[GitHubPRCommentSchema]


class GitHubGetIssueCommentsResponseSchema(RootModel[list[GitHubIssueCommentSchema]]):
    root: list[GitHubIssueCommentSchema]


class GitHubCreateIssueCommentRequestSchema(BaseModel):
    body: str


class GitHubCreateIssueCommentResponseSchema(BaseModel):
    id: int
    body: str


class GitHubCreateReviewReplyRequestSchema(BaseModel):
    body: str
    in_reply_to: int


class GitHubCreateReviewCommentRequestSchema(BaseModel):
    body: str
    path: str
    line: int
    commit_id: str


class GitHubCreateReviewCommentResponseSchema(BaseModel):
    id: int
    body: str
