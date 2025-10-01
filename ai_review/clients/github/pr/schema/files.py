from pydantic import BaseModel, RootModel


class GitHubPRFileSchema(BaseModel):
    sha: str
    patch: str | None = None
    status: str
    filename: str


class GitHubGetPRFilesQuerySchema(BaseModel):
    per_page: int


class GitHubGetPRFilesResponseSchema(RootModel[list[GitHubPRFileSchema]]):
    root: list[GitHubPRFileSchema]
