from pydantic import BaseModel, Field, ConfigDict


class BitbucketServerChangePathSchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    to_string: str = Field(alias="toString")


class BitbucketServerChangeSchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    path: BitbucketServerChangePathSchema
    type: str
    src_path: BitbucketServerChangePathSchema | None = Field(default=None, alias="srcPath")
    node_type: str = Field(alias="nodeType")
    executable: bool | None = None
    percent_unchanged: float | None = Field(default=None, alias="percentUnchanged")


class BitbucketServerGetPRChangesQuerySchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    start: int = 0
    limit: int = 100


class BitbucketServerGetPRChangesResponseSchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    size: int
    limit: int
    start: int
    values: list[BitbucketServerChangeSchema]
    is_last_page: bool = Field(alias="isLastPage")
    next_page_start: int | None = Field(default=None, alias="nextPageStart")
