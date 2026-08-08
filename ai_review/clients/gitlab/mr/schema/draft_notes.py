from pydantic import BaseModel, RootModel

from ai_review.clients.gitlab.mr.schema.position import GitLabPositionSchema


class GitLabDraftNoteSchema(BaseModel):
    id: int
    note: str
    position: GitLabPositionSchema | None = None


class GitLabCreateMRDraftNoteRequestSchema(BaseModel):
    note: str
    position: GitLabPositionSchema | None = None


class GitLabGetMRDraftNotesQuerySchema(BaseModel):
    page: int = 1
    per_page: int = 100


class GitLabGetMRDraftNotesResponseSchema(RootModel[list[GitLabDraftNoteSchema]]):
    root: list[GitLabDraftNoteSchema]
