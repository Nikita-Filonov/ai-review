from pydantic import BaseModel, RootModel, Field

from ai_review.clients.gitlab.mr.schema.notes import GitLabNoteSchema
from ai_review.clients.gitlab.mr.schema.position import GitLabPositionSchema


class GitLabDiscussionSchema(BaseModel):
    id: str
    notes: list[GitLabNoteSchema]
    position: GitLabPositionSchema | None = None


class GitLabGetMRDiscussionsQuerySchema(BaseModel):
    page: int = 1
    per_page: int = 100


class GitLabGetMRDiscussionsResponseSchema(RootModel[list[GitLabDiscussionSchema]]):
    root: list[GitLabDiscussionSchema]


class GitLabCreateMRDiscussionRequestSchema(BaseModel):
    body: str
    position: GitLabPositionSchema


class GitLabCreateMRDiscussionResponseSchema(BaseModel):
    id: str
    notes: list[GitLabNoteSchema] = Field(default_factory=list)


class GitLabCreateMRDiscussionReplyRequestSchema(BaseModel):
    body: str


class GitLabCreateMRDiscussionReplyResponseSchema(BaseModel):
    id: int
    body: str
