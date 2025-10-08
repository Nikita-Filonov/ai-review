from pydantic import BaseModel, RootModel

from ai_review.clients.gitlab.mr.schema.position import GitLabPositionSchema
from ai_review.clients.gitlab.mr.schema.user import GitLabUserSchema


class GitLabNoteSchema(BaseModel):
    id: int
    body: str
    author: GitLabUserSchema | None = None
    position: GitLabPositionSchema | None = None


class GitLabGetMRNotesQuerySchema(BaseModel):
    page: int = 1
    per_page: int = 100


class GitLabGetMRNotesResponseSchema(RootModel[list[GitLabNoteSchema]]):
    root: list[GitLabNoteSchema]


class GitLabCreateMRNoteRequestSchema(BaseModel):
    body: str


class GitLabCreateMRNoteResponseSchema(BaseModel):
    id: int
    body: str
