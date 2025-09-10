from pydantic import BaseModel


class GitLabDiscussionPositionSchema(BaseModel):
    position_type: str = "text"
    base_sha: str
    head_sha: str
    start_sha: str
    new_path: str
    new_line: int


class GitLabCreateMRDiscussionRequestSchema(BaseModel):
    body: str
    position: GitLabDiscussionPositionSchema


class GitLabCreateMRDiscussionResponseSchema(BaseModel):
    id: int
    body: str
