from pydantic import BaseModel

from ai_review.clients.gitlab.mr.schema.position import GitLabPositionSchema


class GitLabDraftNoteSchema(BaseModel):
    id: int
    note: str
    position: GitLabPositionSchema | None = None


class GitLabCreateMRDraftNoteRequestSchema(BaseModel):
    note: str
    position: GitLabPositionSchema | None = None
