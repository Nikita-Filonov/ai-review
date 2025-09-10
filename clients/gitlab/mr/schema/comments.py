from pydantic import BaseModel


class GitLabCreateMRCommentRequestSchema(BaseModel):
    body: str


class GitLabCreateMRCommentResponseSchema(BaseModel):
    id: int
    body: str
