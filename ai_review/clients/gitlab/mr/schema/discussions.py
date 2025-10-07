from pydantic import BaseModel, RootModel, Field

from ai_review.clients.gitlab.mr.schema.notes import GitLabNoteSchema


class GitLabDiscussionPositionSchema(BaseModel):
    position_type: str = "text"
    base_sha: str
    head_sha: str
    start_sha: str
    new_path: str
    new_line: int


class GitLabDiscussionSchema(BaseModel):
    id: str
    notes: list[GitLabNoteSchema]
    position: GitLabDiscussionPositionSchema | None = None


class GitLabGetMRDiscussionsQuerySchema(BaseModel):
    page: int = 1
    per_page: int = 100


class GitLabGetMRDiscussionsResponseSchema(RootModel[list[GitLabDiscussionSchema]]):
    root: list[GitLabDiscussionSchema]


class GitLabCreateMRDiscussionRequestSchema(BaseModel):
    body: str
    position: GitLabDiscussionPositionSchema


class GitLabCreateMRDiscussionResponseSchema(BaseModel):
    id: str
    notes: list[GitLabNoteSchema] = Field(default_factory=list)


class GitLabCreateMRDiscussionReplyRequestSchema(BaseModel):
    body: str


class GitLabCreateMRDiscussionReplyResponseSchema(BaseModel):
    id: int
    body: str
