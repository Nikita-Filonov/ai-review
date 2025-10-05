from pydantic import BaseModel, RootModel


class GitLabNoteSchema(BaseModel):
    id: int
    body: str


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
