from pydantic import BaseModel, Field, ConfigDict

from ai_review.clients.bitbucket_server.pr.schema.user import BitbucketServerUserSchema


class BitbucketServerCommentParentSchema(BaseModel):
    id: int


class BitbucketServerCommentAnchorSchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    path: str | None = None
    line: int | None = None
    line_type: str | None = Field(default=None, alias="lineType")


class BitbucketServerCommentSchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: int
    text: str
    author: BitbucketServerUserSchema
    anchor: BitbucketServerCommentAnchorSchema | None = None
    comments: list["BitbucketServerCommentSchema"] = Field(default_factory=list)
    created_date: int = Field(alias="createdDate")
    updated_date: int = Field(alias="updatedDate")


class BitbucketServerGetPRCommentsQuerySchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    start: int = 0
    limit: int = 100


class BitbucketServerGetPRCommentsResponseSchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    size: int
    limit: int
    start: int
    values: list[BitbucketServerCommentSchema]
    is_last_page: bool = Field(alias="isLastPage")
    next_page_start: int | None = Field(default=None, alias="nextPageStart")


class BitbucketServerCreatePRCommentRequestSchema(BaseModel):
    text: str
    parent: BitbucketServerCommentParentSchema | None = None
    anchor: BitbucketServerCommentAnchorSchema | None = None


class BitbucketServerCreatePRCommentResponseSchema(BitbucketServerCommentSchema):
    pass
