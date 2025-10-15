from pydantic import BaseModel, RootModel


class GiteaPRFileSchema(BaseModel):
    patch: str | None = None
    status: str
    filename: str


class GiteaGetPRFilesQuerySchema(BaseModel):
    page: int = 1
    per_page: int = 100


class GiteaGetPRFilesResponseSchema(RootModel[list[GiteaPRFileSchema]]):
    root: list[GiteaPRFileSchema]
