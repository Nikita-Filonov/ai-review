from pydantic import BaseModel, RootModel


class GitLabMRCommentSchema(BaseModel):
    id: int
    body: str


class GitLabGetMRCommentsResponseSchema(RootModel[list[GitLabMRCommentSchema]]):
    root: list[GitLabMRCommentSchema]


class GitLabCreateMRCommentRequestSchema(BaseModel):
    body: str


class GitLabCreateMRCommentResponseSchema(BaseModel):
    id: int
    body: str
