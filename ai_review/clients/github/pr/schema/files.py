from pydantic import BaseModel, RootModel


class GitHubPRFileSchema(BaseModel):
    sha: str
    patch: str | None = None
    status: str
    filename: str


class GitHubGetPRFilesQuerySchema(BaseModel):
    page: int = 1
    per_page: int = 100


class GitHubGetPRFilesResponseSchema(RootModel[list[GitHubPRFileSchema]]):
    root: list[GitHubPRFileSchema]
