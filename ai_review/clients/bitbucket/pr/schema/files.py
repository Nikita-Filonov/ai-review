from pydantic import BaseModel, Field, ConfigDict


class BitbucketPRFilePathSchema(BaseModel):
    path: str


class BitbucketPRFileSchema(BaseModel):
    new: BitbucketPRFilePathSchema | None = None
    old: BitbucketPRFilePathSchema | None = None
    status: str
    lines_added: int
    lines_removed: int


class BitbucketGetPRFilesQuerySchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    page: int = 1
    page_len: int = Field(alias="pagelen", default=100)


class BitbucketGetPRFilesResponseSchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    size: int
    page: int | None = None
    next: str | None = None
    values: list[BitbucketPRFileSchema]
    page_len: int = Field(alias="pagelen")
