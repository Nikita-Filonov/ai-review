from pydantic import BaseModel, RootModel


class GitLabNoteSchema(BaseModel):
    id: int
    body: str


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


class GitLabGetMRDiscussionsResponseSchema(RootModel[list[GitLabDiscussionSchema]]):
    root: list[GitLabDiscussionSchema]


class GitLabCreateMRDiscussionRequestSchema(BaseModel):
    body: str
    position: GitLabDiscussionPositionSchema


class GitLabCreateMRDiscussionResponseSchema(BaseModel):
    id: str
    body: str | None = None
