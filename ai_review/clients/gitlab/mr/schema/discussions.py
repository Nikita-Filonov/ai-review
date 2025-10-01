from pydantic import BaseModel, RootModel

from ai_review.clients.gitlab.mr.schema.notes import GitLabNoteSchema


class GitLabDiscussionSchema(BaseModel):
    id: str
    notes: list[GitLabNoteSchema]


class GitLabDiscussionPositionSchema(BaseModel):
    position_type: str = "text"
    base_sha: str
    head_sha: str
    start_sha: str
    new_path: str
    new_line: int


class GitLabGetMRDiscussionsQuerySchema(BaseModel):
    per_page: int


class GitLabGetMRDiscussionsResponseSchema(RootModel[list[GitLabDiscussionSchema]]):
    root: list[GitLabDiscussionSchema]


class GitLabCreateMRDiscussionRequestSchema(BaseModel):
    body: str
    position: GitLabDiscussionPositionSchema


class GitLabCreateMRDiscussionResponseSchema(BaseModel):
    id: str
    body: str | None = None
