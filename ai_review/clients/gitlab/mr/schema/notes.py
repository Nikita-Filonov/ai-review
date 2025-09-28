from pydantic import BaseModel, RootModel


class GitLabNoteSchema(BaseModel):
    id: int
    body: str


class GitLabGetMRNotesResponseSchema(RootModel[list[GitLabNoteSchema]]):
    root: list[GitLabNoteSchema]


class GitLabCreateMRNoteRequestSchema(BaseModel):
    body: str


class GitLabCreateMRNoteResponseSchema(BaseModel):
    id: int
    body: str
