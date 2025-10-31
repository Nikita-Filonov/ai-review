from pydantic import BaseModel, Field, ConfigDict


class BitbucketCloudPRFilePathSchema(BaseModel):
    path: str


class BitbucketCloudPRFileSchema(BaseModel):
    new: BitbucketCloudPRFilePathSchema | None = None
    old: BitbucketCloudPRFilePathSchema | None = None
    status: str
    lines_added: int
    lines_removed: int


class BitbucketCloudGetPRFilesQuerySchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    page: int = 1
    page_len: int = Field(alias="pagelen", default=100)


class BitbucketCloudGetPRFilesResponseSchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    size: int
    page: int | None = None
    next: str | None = None
    values: list[BitbucketCloudPRFileSchema]
    page_len: int = Field(alias="pagelen")
